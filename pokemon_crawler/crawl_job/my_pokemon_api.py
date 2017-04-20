#!/usr/bin/env python
import os
import sys
import json
import time
import pprint
import logging
import getpass
import argparse
import s2sphere
from s2sphere import CellId, math
from mock_pgoapi import mock_pgoapi as pgoapi
import boto3

log = logging.getLogger(__name__)
DBG = "-----> "

SQS_QUEUE_NAME = 'awseb-e-sdp9xmthwk-stack-AWSEBWorkerQueue-1SBMLBQ6YUVYC'

def break_down_area_to_cell(north, south, west, east): 
    "return a list of s2 cell ids"
    result = []
    
    region = s2sphere.RegionCoverer()
    region.min_level = 15
    region.max_level = 15
    p1 = s2sphere.LatLng.from_degrees(north, west)
    p2 = s2sphere.LatLng.from_degrees(south, east)

    cell_ids = region.get_covering(s2sphere.LatLngRect.from_point_pair(p1, p2))
    result += [cell_id.id() for cell_id in cell_ids]
    #  print cell_ids

    return result

def get_position_from_cell(cellid):
    cell = CellId(id_ = long(cellid)).to_lat_lng()
    return (math.degrees(cell._LatLng__coords[0]), math.degrees(cell._LatLng__coords[1]), 0)

def search_point(cell_id, api):
    # parse position
    position = get_position_from_cell(cell_id) 

    # set player position on the earth
    api.set_position(*position)

    # print get maps object
    cell_ids = [ cell_id ] 
    timestamps = [0]
    response_dict = api.get_map_objects(latitude =position[0], 
                                        longitude = position[1], 
                                        since_timestamp_ms = timestamps, 
                                        cell_id = cell_ids )
    # print('Response dictionary (get_player): \n\r{}'.format(json.dumps(response_dict, indent=2)))

    return response_dict

def parse_pokemon(search_response):
    map_cells = search_response["responses"]["GET_MAP_OBJECTS"]["map_cells"]
    map_cell = map_cells[0]
    
    catchable_pokemons = map_cell["catchable_pokemons"]
    # print(json.dumps(catchable_pokemons, indent=2))

    return catchable_pokemons 

def scan_area(north, south, west, east, api):
    result = []
    
    # 1. Find all points to search with the area
    cell_ids = break_down_area_to_cell(north, south, west, east) 

    work_queue = boto3.resource('sqs', region_name='us-west-2').get_queue_by_name(QueueName=SQS_QUEUE_NAME)
    print DBG + "The work queue is "
    print work_queue.url
    for cell_id in cell_ids:
        # 3. Send request to elastic beanstalk worker server
        print "sending messages to work queue " + str(cell_id)
        work_queue.send_message(MessageBody=json.dumps({"cell_id":cell_id}))

    return result

def init_config():
    parser = argparse.ArgumentParser()
    config_file = "config.json"

    # If config file exists, load variables from json
    load = {}
    if os.path.isfile(config_file):
        with open(config_file) as data:
            load.update(json.load(data))

    # Read passed in Arguments
    required = lambda x: not x in load
    parser.add_argument("-a", "--auth_service", help="Auth Service ('ptc' or 'google')",
        required=required("auth_service"))
    parser.add_argument("-u", "--username", help="Username", required=required("username"))
    parser.add_argument("-p", "--password", help="Password")
    parser.add_argument("-l", "--location", help="Location", required=required("location"))
    parser.add_argument("-d", "--debug", help="Debug Mode", action='store_true')
    parser.add_argument("-t", "--test", help="Only parse the specified location", action='store_true')
    parser.add_argument("-px", "--proxy", help="Specify a socks5 proxy url")
    parser.set_defaults(DEBUG=False, TEST=False)
    config = parser.parse_args()

    # Passed in arguments shoud trump
    for key in config.__dict__:
        if key in load and config.__dict__[key] == None:
            config.__dict__[key] = str(load[key])

    if config.__dict__["password"] is None:
        log.info("Secure Password Input (if there is no password prompt, use --password <pw>):")
        config.__dict__["password"] = getpass.getpass()

    if config.auth_service not in ['ptc', 'google']:
      log.error("Invalid Auth service specified! ('ptc' or 'google')")
      return None

    return config

def init_api(config):
    # instantiate pgoapi
    api = pgoapi.PGoApi()
    if config.proxy:
        api.set_proxy({'http': config.proxy, 'https': config.proxy})
    
    # new authentication initialitation
    if config.proxy:
        api.set_authentication(provider = config.auth_service, username = config.username, password =  config.password, proxy_config = {'http': config.proxy, 'https': config.proxy})
    else:
        api.set_authentication(provider = config.auth_service, username = config.username, password =  config.password)

    # provide the path for your encrypt dll
    api.activate_signature("/home/ubuntu/pgoapi/libencrypt.so")

    return api


if __name__ == "__main__":
    
    config = init_config()
    print DBG + "The created config object is: " 
    print config
    api = init_api(config)

    # 34.4226329,-119.6997424
    # 34.4260804,-119.6893976
    scan_area(34.4226329, 34.4260804, -119.6893976, -119.6997424, api)
