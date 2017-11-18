CREATE DATABASE fradio;
USE fradio;

CREATE TABLE playing ( 
    spotifyUsername VARCHAR(128), 
    spotifyTrackID VARCHAR(128),
    startTime DATETIME, 
    scrollTime TIME
);

CREATE TABLE user (
    spotifyUsername VARCHAR(128),
    spotifyPassword VARCHAR(128),
    PRIMARY KEY (spotifyUsername)
);
