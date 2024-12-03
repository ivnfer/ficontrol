/* ficontrol v2.6 sql */

CREATE TABLE IF NOT EXISTS screenconfig(
    id integer primary key autoincrement,
    model text NOT NULL,
    platform text NOT NULL,
    powersavingmode text,
    onewire text
);

CREATE TABLE IF NOT EXISTS idgroups(
    id integer primary key autoincrement,
    name text NOT NULL
);

CREATE TABLE IF NOT EXISTS hexcodes(
    id integer primary key autoincrement,
    idtype integer NOT NULL,
    codename text,
    hexcode text,
    foreign key (idtype) references idgroups(id)
);

CREATE TABLE IF NOT EXISTS history_status(
    history_id integer primary key autoincrement,
    modelname text,
    serialnumber text,
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

/* INSERTS */
/* idgroups*/
INSERT INTO idgroups (id, name) VALUES (1, 'inputvalue');
INSERT INTO idgroups (id, name) VALUES (2, 'energymodevalue');
INSERT INTO idgroups (id, name) VALUES (3, 'onewirevalue');
INSERT INTO idgroups (id, name) VALUES (4, 'volumevalue');
INSERT INTO idgroups (id, name) VALUES (5, 'mutevalue');
INSERT INTO idgroups (id, name) VALUES (6, 'powervalue');

/* hexcodes */
INSERT INTO hexcodes (idtype, codename, hexcode) VALUES (1, 'HDMI 1', '0d');
INSERT INTO hexcodes (idtype, codename, hexcode) VALUES (1, 'HDMI 2', '06');
INSERT INTO hexcodes (idtype, codename, hexcode) VALUES (1, 'HDMI 3', '0f');
INSERT INTO hexcodes (idtype, codename, hexcode) VALUES (1, 'VGA', '05');
INSERT INTO hexcodes (idtype, codename, hexcode) VALUES (1, 'Browser', '10');
INSERT INTO hexcodes (idtype, codename, hexcode) VALUES (1, 'Display Port 1', '0a');
INSERT INTO hexcodes (idtype, codename, hexcode) VALUES (1, 'CMND&Play', '11');
INSERT INTO hexcodes (idtype, codename, hexcode) VALUES (1, 'NACK', '15');
INSERT INTO hexcodes (idtype, codename, hexcode) VALUES (2, '1', '04');
INSERT INTO hexcodes (idtype, codename, hexcode) VALUES (2, '2', '05');
INSERT INTO hexcodes (idtype, codename, hexcode) VALUES (2, '3', '06');
INSERT INTO hexcodes (idtype, codename, hexcode) VALUES (2, '4', '07');
INSERT INTO hexcodes (idtype, codename, hexcode) VALUES (2, 'NACK', '15');
INSERT INTO hexcodes (idtype, codename, hexcode) VALUES (3, 'OFF', '00');
INSERT INTO hexcodes (idtype, codename, hexcode) VALUES (3, 'ON', '01');
INSERT INTO hexcodes (idtype, codename, hexcode) VALUES (3, 'NACK', '15');
INSERT INTO hexcodes (idtype, codename, hexcode) VALUES (5, 'OFF', '00');
INSERT INTO hexcodes (idtype, codename, hexcode) VALUES (5, 'ON', '01');
INSERT INTO hexcodes (idtype, codename, hexcode) VALUES (5, 'NACK', '15');
INSERT INTO hexcodes (idtype, codename, hexcode) VALUES (6, 'OFF', '01');
INSERT INTO hexcodes (idtype, codename, hexcode) VALUES (6, 'ON', '02');
INSERT INTO hexcodes (idtype, codename, hexcode) VALUES (6, 'NACK', '15');

/* screenconfig */
INSERT INTO screenconfig (model, platform, powersavingmode, onewire) VALUES ('32BDL3550Q', 'BDL3550Q', '0x06', '0x00');
INSERT INTO screenconfig (model, platform, powersavingmode, onewire) VALUES ('43BDL4550D', 'BDL4550D', '0x06', '0x00');