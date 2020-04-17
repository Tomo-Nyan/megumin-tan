CREATE DATABASE dbMegumin;
USE dbMegumin;
CREATE TABLE tblGuilds (serverID varchar(18) UNIQUE NOT NULL,serverOptionsID int,disableRandom bool DEFAULT 1,disableGreetings bool DEFAULT 1, PRIMARY KEY (serverID));
CREATE TABLE tblGuildSettings (gsID int AUTO_INCREMENT PRIMARY KEY,serverID varchar(18),channelGreet varchar(18),FOREIGN KEY (serverID) REFERENCES tblGuilds(serverID)) AUTO_INCREMENT=1;
CREATE OR REPLACE USER megumin@'localhost' IDENTIFIED BY 'password' WITH MAX_USER_CONNECTIONS 1;
GRANT SELECT,INSERT,UPDATE,DELETE ON tblGuilds TO 'megumin'@'localhost';
GRANT SELECT,INSERT,UPDATE,DELETE ON tblGuildSettings TO 'megumin'@'localhost';
