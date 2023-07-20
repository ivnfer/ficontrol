/* Base de datos v2.0 */

CREATE TABLE IF NOT EXISTS screeninfo(
    modelname text,
    serialnumber text UNIQUE,
    fwversion text,
    build_date text,
    platform_label text,
    platform_version text,
    sicp_version text,
    powerstatus text,
    bootsource text,
    input text,
    volume text,
    mute text,
    powermode text,
    onewire text,
    brightness text,
    color text,
    contrast text,
    sharpness text,
    tint text,
    black_level text,
    gamma text,
    updated date
);

CREATE TABLE IF NOT EXISTS screenconfig(
    id integer primary key autoincrement,
    model text NOT NULL,
    platform text NOT NULL,
    powersavingmode text,
    onewire text
);

CREATE TABLE IF NOT EXISTS idgrupos(
    id integer primary key autoincrement,
    name text NOT NULL
);

CREATE TABLE IF NOT EXISTS codigos(
    id integer primary key autoincrement,
    idtype integer NOT NULL,
    codename text,
    hexcode text,
    foreign key (idtype) references idgrupos(id)
);

/* INSERTS */
/* Tabla idgrupos*/
INSERT INTO idgrupos (id, name) VALUES (1, 'inputvalue');
INSERT INTO idgrupos (id, name) VALUES (2, 'energymodevalue');
INSERT INTO idgrupos (id, name) VALUES (3, 'onewirevalue');
INSERT INTO idgrupos (id, name) VALUES (4, 'volumevalue');
INSERT INTO idgrupos (id, name) VALUES (5, 'mutevalue');
INSERT INTO idgrupos (id, name) VALUES (6, 'powervalue');

/* Tabla codigos */
INSERT INTO codigos (idtype, codename, hexcode) VALUES (1, 'HDMI 1', '0d');
INSERT INTO codigos (idtype, codename, hexcode) VALUES (1, 'HDMI 2', '06');
INSERT INTO codigos (idtype, codename, hexcode) VALUES (1, 'HDMI 3', '0f');
INSERT INTO codigos (idtype, codename, hexcode) VALUES (1, 'VGA', '05');
INSERT INTO codigos (idtype, codename, hexcode) VALUES (1, 'Browser', '10');
INSERT INTO codigos (idtype, codename, hexcode) VALUES (1, 'Display Port 1', '0a');
INSERT INTO codigos (idtype, codename, hexcode) VALUES (1, 'CMND&Play', '11');
INSERT INTO codigos (idtype, codename, hexcode) VALUES (2, 'MODO 1', '04');
INSERT INTO codigos (idtype, codename, hexcode) VALUES (2, 'MODO 2', '05');
INSERT INTO codigos (idtype, codename, hexcode) VALUES (2, 'MODO 3', '06');
INSERT INTO codigos (idtype, codename, hexcode) VALUES (2, 'MODO 4', '07');
INSERT INTO codigos (idtype, codename, hexcode) VALUES (2, 'NACK', '15');
INSERT INTO codigos (idtype, codename, hexcode) VALUES (3, 'OFF', '00');
INSERT INTO codigos (idtype, codename, hexcode) VALUES (3, 'ON', '01');
INSERT INTO codigos (idtype, codename, hexcode) VALUES (5, 'OFF', '00');
INSERT INTO codigos (idtype, codename, hexcode) VALUES (5, 'ON', '01');
INSERT INTO codigos (idtype, codename, hexcode) VALUES (6, 'OFF', '01');
INSERT INTO codigos (idtype, codename, hexcode) VALUES (6, 'ON', '02');

/* Tabla screenconfig */
INSERT INTO screenconfig (model, platform, powersavingmode, onewire) VALUES ('32BDL3550Q', 'BDL3550Q', '0x06', '0x00');
INSERT INTO screenconfig (model, platform, powersavingmode, onewire) VALUES ('43BDL4550D', 'BDL4550D', '0x06', '0x00');