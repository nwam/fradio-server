DROP DATABASE fradio;
CREATE DATABASE fradio;
USE fradio;

CREATE TABLE broadcast( 
    broadcastID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    spotifyUsername VARCHAR(128), 
    spotifyTrackID VARCHAR(128),
    isPlaying INTEGER,
    startTime BIGINT, 
    scrollTime BIGINT,
    trackLength BIGINT
);

CREATE TABLE user (
    spotifyUsername VARCHAR(128),
    listening VARCHAR(32),
    ipAddress VARCHAR(32),
    PRIMARY KEY (spotifyUsername)
);
