# Populates the Flight Management Database with realistic sample data.
# The sample data values (pilot names, airports, aircraft, flights) were
# generated with AI assistance, as permitted under the assignment's Type A categorisation.

import sqlite3

conn = sqlite3.connect("flights.db")
conn.execute("PRAGMA foreign_keys = ON")
cur = conn.cursor()

# Clear existing data
cur.execute("DELETE FROM FlightCrew")
cur.execute("DELETE FROM Flight")
cur.execute("DELETE FROM Aircraft")
cur.execute("DELETE FROM Destination")
cur.execute("DELETE FROM Pilot")

# Pilots
pilots = [
    ("James", "Carter", "UK10234", "Captain", "2012-03-15"),
    ("Sarah", "Khan", "UK10876", "Captain", "2014-07-22"),
    ("David", "OConnor", "UK11458", "Captain", "2010-11-03"),
    ("Emma", "Lewis", "UK12031", "Captain", "2016-01-19"),
    ("Daniel", "Patel", "UK12677", "First Officer", "2018-05-30"),
    ("Olivia", "Murphy", "UK13044", "First Officer", "2019-09-12"),
    ("Thomas", "Nguyen", "UK13599", "First Officer", "2020-02-25"),
    ("Sophie", "Walsh", "UK14122", "First Officer", "2021-06-08"),
    ("Michael", "Reid", "UK14788", "Captain", "2013-04-17"),
    ("Hannah", "Clarke", "UK15233", "First Officer", "2022-08-14"),
    ("Robert", "Singh", "UK15890", "Captain", "2011-10-29"),
    ("Grace", "Bennett", "UK16455", "First Officer", "2023-03-01"),
]
cur.executemany(
    "INSERT INTO Pilot (firstName, lastName, licenceNumber, rank, hireDate) "
    "VALUES (?, ?, ?, ?, ?)", pilots
)


# Destinations
destinations = [
    ("JFK", "John F. Kennedy International", "New York", "USA"),
    ("CDG", "Charles de Gaulle", "Paris", "France"),
    ("DXB", "Dubai International", "Dubai", "UAE"),
    ("SIN", "Changi", "Singapore", "Singapore"),
    ("JNB", "O. R. Tambo International", "Johannesburg", "South Africa"),
    ("LAX", "Los Angeles International", "Los Angeles", "USA"),
    ("HND", "Haneda", "Tokyo", "Japan"),
    ("FCO", "Leonardo da Vinci", "Rome", "Italy"),
    ("SYD", "Kingsford Smith", "Sydney", "Australia"),
    ("GRU", "Guarulhos International", "Sao Paulo", "Brazil"),
    ("HKG", "Hong Kong International", "Hong Kong", "Hong Kong"),
    ("FRA", "Frankfurt Airport", "Frankfurt", "Germany"),
]
cur.executemany(
    "INSERT INTO Destination (airportCode, airportName, city, country) "
    "VALUES (?, ?, ?, ?)", destinations
)


# Aircraft
aircraft = [
    ("G-XLEA", "Airbus A380-800", 469),
    ("G-STBA", "Boeing 777-300ER", 396),
    ("G-ZBKA", "Boeing 787-9", 216),
    ("G-EUUA", "Airbus A320-200", 180),
    ("G-EUYB", "Airbus A321-200", 220),
    ("G-VWOO", "Boeing 787-9", 264),
    ("G-VLIP", "Boeing 747-400", 455),
    ("G-TTNA", "Airbus A320neo", 188),
    ("G-NEOP", "Airbus A321neo", 235),
    ("G-CIVA", "Boeing 777-200ER", 280),
]
cur.executemany(
    "INSERT INTO Aircraft (registration, model, capacity) "
    "VALUES (?, ?, ?)", aircraft
)

# Store IDs created
dest_ids = [r[0] for r in cur.execute(
    "SELECT destinationID FROM Destination ORDER BY destinationID").fetchall()]
aircraft_ids = [r[0] for r in cur.execute(
    "SELECT aircraftID FROM Aircraft ORDER BY aircraftID").fetchall()]
pilot_ids = [r[0] for r in cur.execute(
    "SELECT pilotID FROM Pilot ORDER BY pilotID").fetchall()]

#Flights
flights = [
    ("BA117",  "2026-06-10 08:30", "2026-06-10 11:15", "Scheduled", 0, 1),
    ("BA306",  "2026-06-10 09:00", "2026-06-10 11:20", "Scheduled", 1, 3),
    ("BA107",  "2026-06-10 13:45", "2026-06-11 00:05", "Scheduled", 2, 0),
    ("BA011",  "2026-06-11 21:10", "2026-06-12 17:30", "Scheduled", 3, 2),
    ("BA055",  "2026-06-11 19:40", "2026-06-12 07:55", "Delayed",   4, 6),
    ("BA269",  "2026-06-12 11:00", "2026-06-12 14:25", "Scheduled", 5, 5),
    ("BA005",  "2026-06-12 14:20", "2026-06-13 10:40", "Scheduled", 6, 1),
    ("BA552",  "2026-06-13 07:15", "2026-06-13 11:05", "Scheduled", 7, 4),
    ("BA015",  "2026-06-13 20:00", "2026-06-14 19:45", "Scheduled", 8, 0),
    ("BA247",  "2026-06-14 22:30", "2026-06-15 06:15", "Cancelled", 9, 9),
    ("BA027",  "2026-06-14 12:50", "2026-06-15 08:30", "Scheduled", 10, 5),
    ("BA902",  "2026-06-15 06:40", "2026-06-15 09:20", "Scheduled", 11, 7),
]
for fn, dep, arr, status, di, ai in flights:
    cur.execute(
        "INSERT INTO Flight (flightNumber, departureTime, arrivalTime, status, destID, aircraftID) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (fn, dep, arr, status, dest_ids[di], aircraft_ids[ai])
    )

flight_ids = [r[0] for r in cur.execute(
    "SELECT flightID FROM Flight ORDER BY flightID").fetchall()]

# FlightCrew (each flight must have one Captain and one a First Officer)
captains = [0, 1, 2, 3, 8, 10]
first_officers = [4, 5, 6, 7, 9, 11]

for i, fid in enumerate(flight_ids):
    # cycle through the pilot lists
    cap = pilot_ids[captains[i % len(captains)]]
    # cycle through the first officer lists
    fo = pilot_ids[first_officers[i % len(first_officers)]]
    
    cur.execute("INSERT INTO FlightCrew (flightID, pilotID, role) VALUES (?, ?, ?)",
                (fid, cap, "Captain"))
    cur.execute("INSERT INTO FlightCrew (flightID, pilotID, role) VALUES (?, ?, ?)",
                (fid, fo, "First Officer"))

conn.commit()

# Confirmation prompt
for t in ["Pilot", "Destination", "Aircraft", "Flight", "FlightCrew"]:
    count = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"{t}: {count} rows")

conn.close()