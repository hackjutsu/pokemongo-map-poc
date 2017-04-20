import psycopg2

# logging
import logging

logger = logging.getLogger("worker")

DBG = "-----> "

# INSERT INTO pokemon_map (encounter_id , expire , pokemon_id , latitude , longitude ) VALUES (1,1,1,1,1) ON CONFLICT (encounter_id) DO NOTHING;
def add_pokemon_to_db(encounter_id , expire , pokemon_id , latitude , longitude):
    # 1. Open connection
    conn = psycopg2.connect(host = "pkgo-0.c8yops2lyqcp.us-west-2.rds.amazonaws.com",
                            port = 5432,
                            user = "pkgo0",
                            password = "mypkgo-0")

    # 2. Execute SQL
    with conn.cursor() as cur:
        cur.execute("INSERT INTO pokemon_map (encounter_id , expire , pokemon_id , latitude , longitude )" +
                    " VALUES (%s, %s, %s, %s, %s)" +
                    " ON CONFLICT (encounter_id) DO NOTHING", (encounter_id , expire , pokemon_id , latitude , longitude))

    # 3. connection commit
    conn.commit()

    dbg_msg = DBG + "add_pokemon_to_db with encounter_id " + str(encounter_id)
    print dbg_msg
    logger.info(dbg_msg)
    return
