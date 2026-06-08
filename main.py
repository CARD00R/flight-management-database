# Flight Management Database - command-line interface

#imports
import sqlite3
import os
from datetime import datetime

DB_FILE = "flights.db"                    # database reference

# --- Helper Funfctions---
def clear_screen():
    """Clears the terminal."""
    os.system("clear")

def print_flights(rows):
    """Print flight rows in a readable format. Handles the empty case."""
    if not rows:
        print("\nNo flights found.") # error catching
        return
    for r in rows:
        print(f"\n{r['flightNumber']} | {r['status']}")
        print(f"  Departs: {r['departureTime']:<20} | Aircraft: {r['model']}") # pad to 20 characters wide to the right (left-aligned)
        print(f"  Arrives: {r['arrivalTime']:<20} | To: {r['city']}")          # pad to 20 characters wide to the right (left-aligned)

def print_pilot_schedule(pilot_name, rows):
    """Print the flights a pilot is assigned to. Handles the empty case."""
    clear_screen()

    if not rows:
        print(f"\n{pilot_name} has no assigned flights.")
        return
    print(f"\nSchedule for {pilot_name}:")
    for r in rows:
        print(f"\n  {r['flightNumber']} | Role: {r['role']}")
        print(f"    Departs: {r['departureTime']:<20} | To: {r['city']}")
        print(f"    Status:  {r['status']}")

def valid_datetime(text):
    """Return True if text matches the 'YYYY-MM-DD HH:MM' format, else False."""
    try:
        datetime.strptime(text, "%Y-%m-%d %H:%M")   # try to parse, throws exception if wrong format, otherwise return tru
        return True
    except ValueError:                              
        return False

# --- Connection function ---  
def connect():
    """Open a connection to the SQLite database and return it."""
    conn = sqlite3.connect(DB_FILE)        
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row         # allows columns to be read by their name
    return conn


# --- Menu Options --- 

def add_flight(conn):
    """Add a New Flight."""

    clear_screen()
    print("Add a new flight\n")

    flight_number = input("Enter Flight number (e.g. BA123): ").strip()

    # Interesting challenge worth noting in report

    # Departure time input loop
    while True:
        departure = input("Enter Departure time (YYYY-MM-DD HH:MM): ").strip()
        if valid_datetime(departure):
            break
        print("  Invalid format, try again.")

    # Arrival time input loop
    while True:
        arrival = input("Enter Arrival time (YYYY-MM-DD HH:MM): ").strip()
        if valid_datetime(arrival):
            break
        print("  Invalid format, try again.")

    # Status input loop
    allowed = ("Scheduled", "Delayed", "Cancelled")
    while True:
        status = input("Enter Status (Scheduled / Delayed / Cancelled): ").strip()
        if status in allowed:
            break
        print("  Invalid status, try again.")

    # Destinations input loop
    print("\nDestinations:")
    # Print destinations
    for location in conn.execute("SELECT destinationID, city FROM Destination ORDER BY destinationID"):
        dest_id = location['destinationID']
        city = location['city']
        print(f"  {dest_id}. {city}")
    # Input Handling
    destination_id = input("Enter Destination ID: ").strip()
    if conn.execute("SELECT 1 FROM Destination WHERE destinationID = ?", (destination_id,)).fetchone() is None:
        print("No destination with that ID.")
        return

    # Aircraft input loop
    print("\nAircraft:")
    # Print destinations
    for plane in conn.execute("SELECT aircraftID, model FROM Aircraft ORDER BY aircraftID"):
        plane_id = plane['aircraftID']
        model = plane['model']
        print(f"  {plane_id}. {model}")
    # Input Handling
    aircraft_id = input("Aircraft ID: ").strip()
    if conn.execute("SELECT 1 FROM Aircraft WHERE aircraftID = ?", (aircraft_id,)).fetchone() is None:
        print("No aircraft with that ID.")
        return

    # Insert the new flight
    conn.execute("""
        INSERT INTO Flight (flightNumber, departureTime, arrivalTime, status, destinationID, aircraftID)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (flight_number, departure, arrival, status, destination_id, aircraft_id))

    conn.commit()                  # push change into database
    print(f"\nFlight {flight_number} added.")

def view_flights(conn):
    """View Flights based on input parameters (destination, status, date)."""

    clear_screen()

    # View Flights' sub-menu
    print("\nView flights by:")
    print("  1. City")
    print("  2. Status")
    print("  3. Departure date")
    print("  4. Show ALL flights")
    choice = input("\nSelect an option: ").strip()

    # Interesting challenge worth noting in report
    # Join Destination and Aircraft to Flight to get access to city and model (instead of ID numbers)
    # Select columns flightNumber, departureTime, arrivalTime, status, city, model
    baseQuery = """
        SELECT flightNumber, departureTime, arrivalTime, status, city, model
        FROM Flight
        JOIN Destination ON Flight.destinationID = Destination.destinationID
        JOIN Aircraft    ON Flight.aircraftID    = Aircraft.aircraftID
    """

    # Update each query depending on user's choice.
    # Using a parameterised query to prevent SQL injection (safety reasons)
    if choice == "1":
        city = input("Enter destination city: ").strip()
        newQuery = baseQuery + " WHERE city = ? ORDER BY departureTime"
        rows = conn.execute(newQuery, (city,)).fetchall() 

    elif choice == "2":
        status = input("Enter status (Scheduled / Delayed / Cancelled): ").strip()
        newQuery = baseQuery + " WHERE status = ? ORDER BY departureTime"
        rows = conn.execute(newQuery, (status,)).fetchall()

    elif choice == "3":
        date = input("Enter departure date (e.g. 2026, 2026-06, or 2026-06-13): ").strip()
        # departureTime is stored as "YYYY-MM-DD HH:MM", LIKE with "%" (wild card) matches the date prefix and ignores the time
        newQuery = baseQuery + " WHERE departureTime LIKE ? ORDER BY departureTime"
        rows = conn.execute(newQuery, (date + "%",)).fetchall()

    elif choice == "4":
        newQuery = baseQuery + " ORDER BY departureTime"
        rows = conn.execute(newQuery).fetchall()

    else:
        print("\nInvalid option.")
        return                          # leave the function, back to main menu

    print_flights(rows)

def update_flight(conn):
    """Update Flight Information (departure time, status, or aircraft)."""

    clear_screen()
    print("Update flight information\n")

    # Get ALL flights and information with ID
    flights = conn.execute("""
        SELECT flightID, flightNumber, departureTime, arrivalTime, status, city, model
        FROM Flight
        JOIN Destination ON Flight.destinationID = Destination.destinationID
        JOIN Aircraft    ON Flight.aircraftID    = Aircraft.aircraftID
        ORDER BY flightID
    """).fetchall()
    
    # Print ALL flights and information with ID
    for flight in flights:
        print(f"\n{flight['flightID']}. {flight['flightNumber']} | {flight['status']}")
        print(f"   Departs: {flight['departureTime']:<20} | Aircraft: {flight['model']}")
        print(f"   Arrives: {flight['arrivalTime']:<20} | To: {flight['city']}")

    # Ask which flight to update
    flight_id = input("\nEnter the flight ID to update: ").strip()
    if conn.execute("SELECT 1 FROM Flight WHERE flightID = ?", (flight_id,)).fetchone() is None:
        print("No flight with that ID.")
        return
    
    clear_screen()
    # Print the selected flight's details
    clear_screen()
    flight = conn.execute("""
        SELECT flightID, flightNumber, departureTime, arrivalTime, status, city, model
        FROM Flight
        JOIN Destination ON Flight.destinationID = Destination.destinationID
        JOIN Aircraft    ON Flight.aircraftID    = Aircraft.aircraftID
        WHERE flightID = ?
    """, (flight_id,)).fetchone()

    print("Selected flight:\n")
    print(f"{flight['flightID']}. {flight['flightNumber']} | {flight['status']}")
    print(f"   Departs: {flight['departureTime']:<20} | Aircraft: {flight['model']}")
    print(f"   Arrives: {flight['arrivalTime']:<20} | To: {flight['city']}")
    
    # Update Flight: Sub-menu
    print("\nWhat would you like to update?")
    print("  1. Departure time")
    print("  2. Arrival time")
    print("  3. Status")
    print("  4. Destination")
    print("  5. Aircraft")
    choice = input("\nSelect an option (1-5): ").strip()

    # Departure-time input loop
    if choice == "1":
        while True:
            departure = input("Enter new departure time (YYYY-MM-DD HH:MM): ").strip()
            if valid_datetime(departure):
                break
            print("  Invalid format, try again.")
        conn.execute("UPDATE Flight SET departureTime = ? WHERE flightID = ?",
                     (departure, flight_id))
    
    # Arrival-time input loop
    elif choice == "2":
        while True:
            arrival = input("Enter new arrival time (YYYY-MM-DD HH:MM): ").strip()
            if valid_datetime(arrival):
                break
            print("  Invalid format, try again.")
        conn.execute("UPDATE Flight SET arrivalTime = ? WHERE flightID = ?",
                     (arrival, flight_id))

    # Status input loop
    elif choice == "3":
        allowed = ("Scheduled", "Delayed", "Cancelled")
        while True:
            status = input("Enter new status (Scheduled / Delayed / Cancelled): ").strip()
            if status in allowed:
                break
            print("  Invalid status, try again.")
        conn.execute("UPDATE Flight SET status = ? WHERE flightID = ?",
                     (status, flight_id))
        
    # Destination input loop
    elif choice == "4":
        # Print destinations with IDs
        print("\nDestinations:")
        for location in conn.execute("SELECT destinationID, city FROM Destination ORDER BY destinationID"):
            print(f"  {location['destinationID']}. {location['city']}")

        destination_id = input("Enter new destination ID: ").strip()
        if conn.execute("SELECT 1 FROM Destination WHERE destinationID = ?", (destination_id,)).fetchone() is None:
            print("No destination found under that ID.")
            return
        conn.execute("UPDATE Flight SET destinationID = ? WHERE flightID = ?",
                     (destination_id, flight_id))

    # Aircraft input loop
    elif choice == "5":
        # Print aircrafts with IDs
        print("\nAircraft:")
        for plane in conn.execute("SELECT aircraftID, model FROM Aircraft ORDER BY aircraftID"):
            print(f"  {plane['aircraftID']}. {plane['model']}")

        aircraft_id = input("Enter new aircraft ID: ").strip()
        if conn.execute("SELECT 1 FROM Aircraft WHERE aircraftID = ?", (aircraft_id,)).fetchone() is None:
            print("No aircraft found under that ID.")
            return
        conn.execute("UPDATE Flight SET aircraftID = ? WHERE flightID = ?",
                     (aircraft_id, flight_id))

    else:
        print("\nInvalid option.")
        return

    conn.commit()                # Push the change to the database
    print("\nFlight updated.")

def assign_pilot(conn):
    """Assign a Pilot to a Flight which writes to the FlightCrew junction table."""
    print("[assign_pilot] not implemeted yet")

def view_pilot_schedule(conn):
    """View the flights the given pilot is assigned to."""

    clear_screen()

    # List all pilots so user can view IDs
    pilots = conn.execute(
        "SELECT pilotID, firstName, lastName FROM Pilot ORDER BY pilotID"
    ).fetchall()
    print("Pilots:")
    for pilot in pilots:
        print(f"  {pilot['pilotID']}. {pilot['firstName']} {pilot['lastName']}")

    pilot_id = input("\nEnter pilot ID: ").strip()

    # Check requested pilot ID exists
    pilot = conn.execute(
        "SELECT firstName, lastName FROM Pilot WHERE pilotID = ?",
        (pilot_id,)
    ).fetchone()
    if pilot is None:                       # no row returned = no pilot found
        print(f"\nNo pilot found under ID: {pilot_id}.")
        return
    

    # Interesting challenge worth noting in report
    # Find every flight the pilot crews by following their relationships:
    # Pilot links to FlightCrew (the junction table holding each pilot's flights and role), 
    # FlightCrew links to Flight (via flightID), and Flight links to Destination (via destinationID) 
    # and is joined so we can show the city, not just its ID.
    query = """
        SELECT flightNumber, role, departureTime, status, city,
               firstName, lastName
        FROM Pilot
        JOIN FlightCrew  ON Pilot.pilotID        = FlightCrew.pilotID
        JOIN Flight      ON FlightCrew.flightID  = Flight.flightID
        JOIN Destination ON Flight.destinationID = Destination.destinationID
        WHERE Pilot.pilotID = ?
        ORDER BY departureTime
    """
    rows = conn.execute(query, (pilot_id,)).fetchall()

    # Build the pilot's name for the heading (from the first row, or fall back).
    if rows:
        name = f"{rows[0]['firstName']} {rows[0]['lastName']}"
    else:
        name = f"Pilot {pilot_id}"

    print_pilot_schedule(name, rows)

def manage_destination(conn):
    """View or update Destination information."""
    print("[manage_destination] not implemeted yet")

def view_summaries(conn):
    """Aggregate reports (flights per destination, flights per pilot)."""
    print("[view_summaries] not implemeted yet")

# --- Menu Definitions --- 

# Menu Struct
MENU = {
#   key: label String,                     function object     
    "1": ("Add a New Flight",              add_flight),
    "2": ("View Flights by Criteria",      view_flights),
    "3": ("Update Flight Information",     update_flight),
    "4": ("Assign Pilot to Flight",        assign_pilot),
    "5": ("View Pilot Schedule",           view_pilot_schedule),
    "6": ("View / Update Destination",     manage_destination),
    "7": ("View Summary Reports",          view_summaries),
}

def print_banner():
    """Display the manu banner to  user."""
    
    #ASCII Art
    print("                  |            ")
    print("              ___/'\___        ")
    print("  .   __________/ o \__________")
    print("__|__    *   *  \___/  *   *   ")
    print("\___/ ")
    print(" | |   Flight Management System")
    print(" | |")
    print("_|_|_____________________________")
    print("              /   |   \ ")
    print("            */    |    \*")
    print("            /     |     \ ")
    print("          */      |      \* ")

def print_menu():
    """Display the menu options to user."""
    clear_screen()
    print_banner()
    print("\n")
    for key in MENU:                      # iterate through keys 1,2,3...
        label = MENU[key][0]              # label = first item of (label string, function) tuple
        print(f"  {key}. {label}")
    print("  0. Exit")

def main():
    """Program entry point: open the DB, loop on the menu until the user exits."""
    conn = connect()                  # Create and store connection

    while True:                       
        print_menu()
        choice = input("\nSelect an option: ").strip()   # read input and remove leading and trailing spaces

        if choice == "0":             # exit case
            print("Goodbye.")
            break                     

        action = MENU.get(choice)     # look up the inputed number (choice), returns None if invalid
        if action is None:            # Error: User inputed invalid number
            input("\nInvalid option. Press Enter to try again...")
            continue                  

        func = action[1]              # get function (2nd item of [label, function] tuple)
        func(conn)                    # call matching menu option, passing the stored connection
        input("\nPress Enter to return to the menu...")   # pause so output stays readable
 
    conn.close()   # close  database connection

if __name__ == "__main__": # Run main() only when file is executed directly (not when imported)
    main()

    