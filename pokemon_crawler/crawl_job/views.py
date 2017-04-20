# logging
import logging

# django imports
from django.shortcuts import render
from django.http import HttpResponse

# self-defined imports
from my_pokemon_api import *
from db_accessor import *

logger = logging.getLogger("worker")
DBG = "-----> "

class Config:
    pass

def add_crawl_point(request):
    print DBG + "I'm in add_crawl_point"
    logger.info(DBG + "Cosmo: I'm in add_crawl_point")
    logger.info(DBG + "The request body is ")
    logger.info(request.body)

    # Crawl pokemon data

    # 1. Get cell id from request
    request_obj = json.loads(request.body)
    cell_id = request_obj["cell_id"]

    # 2. Call my search api
    config = Config()
    config.auth_service = "ptc"
    config.username = "testuser1"
    config.password = "testuser1"
    config.proxy = "socks5://127.0.0.1:9050"
    
    api = init_api(config)

    search_response = search_point(cell_id, api)
    result = parse_pokemon(search_response)

    pokemon_data = json.dumps(result, indent=2)
    logger.info(pokemon_data)

    # 3. Store search result into database
    # encounter_id , expire , pokemon_id , latitude , longitude
    for pokemon in result:
        add_pokemon_to_db(pokemon["encounter_id"],
                          pokemon["expiration_timestamp_ms"],
                          pokemon["pokemon_id"],
                          pokemon["latitude"],
                          pokemon["longitude"])

    return HttpResponse(pokemon_data)  
