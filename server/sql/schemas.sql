DROP DATABASE fradio;
CREATE DATABASE fradio;
USE fradio;

CREATE TABLE broadcast( 
    broadcastID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    spotifyUsername VARCHAR(64), 
    spotifyTrackID VARCHAR(128),
    isPlaying INTEGER NOT NULL DEFAULT -1,
    startTime BIGINT NOT NULL DEFAULT 0,
    scrollTime BIGINT NOT NULL DEFAULT 0,
    trackLength BIGINT NOT NULL DEFAULT 0
);

CREATE TABLE user (
    spotifyUsername VARCHAR(64),
    listening VARCHAR(64),
    ipAddress VARCHAR(32),
    PRIMARY KEY (spotifyUsername)
);

CREATE TABLE track (
    spotifyTrackID VARCHAR(128),
    artist VARCHAR(128),
    album VARCHAR(128),
    title VARCHAR(128),
    art_url VARCHAR(256),
    art_thumb_url VARCHAR(256),
    PRIMARY KEY (spotifyTrackID)
);

CREATE TABLE token (
    value VARCHAR(128), 
    expire BIGINT NOT NULL DEFAULT 0
);
INSERT INTO token (value, expire) VALUES("", 0);
