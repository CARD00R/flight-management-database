-- Flight Management Database schema

-- Required to enforce foreign key constraints
PRAGMA foreign_keys = ON;

-- Pilot table: airline pilots
CREATE TABLE Pilot (
    pilotID         INTEGER PRIMARY KEY,
    firstName       TEXT NOT NULL,
    lastName        TEXT NOT NULL,
    licenceNumber   TEXT NOT NULL UNIQUE,
    rank            TEXT,
    hireDate        DATE
);

-- Destination table: airports flights arrive at
CREATE TABLE Destination (
    destinationID   INTEGER PRIMARY KEY,
    airportCode     TEXT NOT NULL UNIQUE,
    airportName     TEXT NOT NULL,
    city            TEXT,
    country         TEXT
);

-- Aircraft table: aeroplanes in the fleet
CREATE TABLE Aircraft (
    aircraftID      INTEGER PRIMARY KEY,
    registration    TEXT NOT NULL UNIQUE,
    model           TEXT,
    capacity        INTEGER
);

-- Flight table: scheduled flights (one destination, one aircraft each)
CREATE TABLE Flight (
    flightID        INTEGER PRIMARY KEY,
    flightNumber    TEXT NOT NULL,
    departureTime   DATETIME,
    arrivalTime     DATETIME,
    status          TEXT,
    destID          INTEGER NOT NULL,
    aircraftID      INTEGER NOT NULL,
    FOREIGN KEY (destID)     REFERENCES Destination(destinationID),
    FOREIGN KEY (aircraftID) REFERENCES Aircraft(aircraftID)
);

-- FlightCrew: links flights to their assigned pilots (junction table)
CREATE TABLE FlightCrew (
    flightID        INTEGER NOT NULL,
    pilotID         INTEGER NOT NULL,
    role            TEXT NOT NULL CHECK (role IN ('Captain', 'First Officer')), -- reject all roles that are not 'Captain' or 'First Officer'
    PRIMARY KEY (flightID, pilotID),
    FOREIGN KEY (flightID) REFERENCES Flight(flightID),
    FOREIGN KEY (pilotID)  REFERENCES Pilot(pilotID)
);

