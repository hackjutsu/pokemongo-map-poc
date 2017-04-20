CREATE TABLE POKEMON_MAP (
    encounter_id    DOUBLE PRECISION,
    expire          DOUBLE PRECISION,
    pokemon_id      INT,
    latitude        DOUBLE PRECISION,
    longitude       DOUBLE PRECISION,
    PRIMARY KEY (encounter_id)
);


CREATE INDEX expire_idx ON POKEMON_MAP (expire);
CREATE INDEX pokemon_id_idx ON POKEMON_MAP (pokemon_id);
CREATE INDEX longitude_idx ON POKEMON_MAP (longitude);
CREATE INDEX latitude_idx ON POKEMON_MAP (latitude);