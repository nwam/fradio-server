DROP DATABASE fradio;
CREATE DATABASE fradio;
USE fradio;

CREATE TABLE playing ( 
    playingID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    spotifyUsername VARCHAR(128), 
    spotifyTrackID VARCHAR(128),
    startTime BIGINT, 
    scrollTime BIGINT
);

CREATE TABLE user (
    spotifyUsername VARCHAR(128),
    spotifyPassword VARCHAR(128),
    PRIMARY KEY (spotifyUsername)
);
