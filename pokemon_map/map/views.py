# logging
import logging

import json
from django.shortcuts import render
from django.http import HttpResponse
from db_accessor import get_pokemons_from_db

import boto3
import s2sphere

logger = logging.getLogger("worker")

DBG = "-----> "
SQS_QUEUE_NAME = "awseb-e-mtxmwdspvc-stack-AWSEBWorkerQueue-S7LQH9SCM9CV"

def break_down_area_to_cell(north, south, west, east):  
    print DBG + "Inside break_down_area_to_cell"
    result = []
    
    region = s2sphere.RegionCoverer()
    region.min_level = 15
    region.max_level = 15
    p1 = s2sphere.LatLng.from_degrees(north, west)
    p2 = s2sphere.LatLng.from_degrees(south, east)

    rect = s2sphere.LatLngRect.from_point_pair(p1, p2)
    area = rect.area()
    if (area * 1000 * 1000 * 100 > 7):
        print DBG + "The area is too big, return..."
        logger.info(DBG + "The area is too big, return...")
        return
    
    cell_ids = region.get_covering(s2sphere.LatLngRect.from_point_pair(p1, p2))
    result += [cell_id.id() for cell_id in cell_ids]
    print cell_ids

    return result


def scan_area(north, south, west, east):

    # 1. Find all points to search with the area
    cell_ids = break_down_area_to_cell(north, south, west, east) 
    if (cell_ids is None):
        return

    work_queue = boto3.resource(
        'sqs', region_name='us-west-2').get_queue_by_name(QueueName=SQS_QUEUE_NAME)

    print DBG + "The work queue is "
    print DBG +  work_queue.url
    for cell_id in cell_ids:
        # 3. Send request to elastic beanstalk worker server
        logger.info(DBG + "sending messages to work queue " + str(cell_id))
        work_queue.send_message(MessageBody=json.dumps({"cell_id":cell_id}))

    return

def pokemons(request):

    # 1. Get longitude and latitude
    north = request.GET["north"]
    south = request.GET["south"]
    east = request.GET["east"]
    west = request.GET["west"]

    logger.info(DBG + "north: " + north)
    logger.info(DBG + "south: " + south)
    logger.info(DBG + "east: " + east)
    logger.info(DBG + "west: " + west)

    # 2. Query database
    result = get_pokemons_from_db(north, south, west, east)

    # 3. Publish for crawl jobs
    scan_area(float(north), float(south), float(west), float(east))

    return HttpResponse(json.dumps(result))