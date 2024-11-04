DROP TABLE IF EXISTS fdw.geom_demande;
CREATE TABLE fdw.geom_demande (
    id_geom             SERIAL PRIMARY KEY,     -- PK
    id_demande          integer NOT NULL,       -- FK 
    geom                geometry NOT NULL, 				


	CONSTRAINT fk_geom_demande FOREIGN KEY (id_demande) REFERENCES gestion.demande (id)
);