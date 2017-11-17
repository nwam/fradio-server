CREATE DATABASE fradio;
USE fradio;

CREATE TABLE playing ( 
    username VARCHAR(64), 
    spotifyTrackID VARCHAR(64),
    start_time DATETIME, 
    scroll_time TIME
);

CREATE TABLE user (
    username VARCHAR(64),
    passwordHash VARCHAR(128),
    spotifyUsername VARCHAR(128),
    spotifyPassword VARCHAR(128),
    lastFmUsername VARCHAR(128),
    lastFmPassword VARCHAR(128),
    PRIMARY KEY (username)
);
