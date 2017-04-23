import psycopg2
import time
import os

# logging
import logging

logger = logging.getLogger("worker")

DBG = "-----> "

def get_pokemons_from_db(north, south, west, east):
    # 1. Open connection
    conn = psycopg2.connect(host = os.environ['PKGO_DB_HOST'],
                            port = os.environ['PKGO_DB_PORT'],
                            user = os.environ['PKGO_DB_USER'],
                            password = os.environ['PKGO_DB_PASSWORD'])

    # 2. Execute SQL
    with conn.cursor() as cur:
        cur.execute("SELECT expire, pokemon_id, latitude, longitude" +
                    " FROM pokemon_map " +
                    " WHERE longitude > %s " +
                    " AND longitude < %s " + 
                    " AND latitude > %s " + 
                    " AND latitude < %s " +
                    " AND expire > %s " + 
                    " LIMIT 100",
                    (west, east, south, north, time.time() * 1000))
                    
        rows = cur.fetchall()
        result = []
        for row in rows:
            result.append({
                            "expire" : row[0],
                            "pokemon_id" : row[1],
                            "latitude" : row[2],
                            "longitude" : row[3]
                          })

    # 3. connection commit
    conn.commit()

    return result
