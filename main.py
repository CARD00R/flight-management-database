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
    """Print flight rows. Handles the empty case."""
    if not rows:
        print("\nNo flights found.") # Handle no matching flights
        return
    for r in rows:
        print(f"\n{r['flightNumber']} | {r['status']}")
        print(f"  Departs: {r['departureTime']:<20} | Aircraft: {r['model']}") # Pad to 20 characters wide to the right (left-aligned)
        print(f"  Arrives: {r['arrivalTime']:<20} | To: {r['city']}")          # Pad to 20 characters wide to the right (left-aligned)

def print_pilot_schedule(pilot_name, rows):
    """Print the flights a specific pilot is assigned to. Handles the empty case."""
    clear_screen()

    if not rows:
        print(f"\n{pilot_name} has no assigned flights.") # Handle pilot with no assigned flights
        return
    print(f"\nSchedule for {pilot_name}:")
    for r in rows:
        print(f"\n  {r['flightNumber']} | Role: {r['role']}")
        print(f"    Departs: {r['departureTime']:<20} | To: {r['city']}") # Pad to 20 characters wide to the right (left-aligned)
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
    """Open a connection to the SQL database and return it."""
    conn = sqlite3.connect(DB_FILE)        
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row         # allows columns to be read by their column name
    return conn


# --- Menu Options --- 

def add_flight(conn):
    """Add a New Flight."""

    clear_screen()
    print("Add a new flight\n")

    flight_number = input("Enter Flight number (e.g. BA123): ").strip()

    # Departure time input loop
    while True:
        departure = input("Enter Departure time (YYYY-MM-DD HH:MM): ").strip()
        if valid_datetime(departure):
            break
        print("  Invalid format, try again.") # Handles invalid input

    # Arrival time input loop
    while True:
        arrival = input("Enter Arrival time (YYYY-MM-DD HH:MM): ").strip()
        if valid_datetime(arrival):
            break
        print("  Invalid format, try again.") # Handles invalid input

    # Status input loop
    allowedStatuses = ("Scheduled", "Delayed", "Cancelled")
    while True:
        status = input("Enter Status (Scheduled / Delayed / Cancelled): ").strip()
        if status in allowedStatuses:
            break
        print("  Invalid status, try again.") # Handles invalid input

    # Destinations input loop
    print("\nDestinations:")
    # List destinations
    for location in conn.execute("SELECT destinationID, city FROM Destination ORDER BY destinationID"):
        dest_id = location['destinationID']
        city = location['city']
        print(f"  {dest_id}. {city}")
    # User Input Handling
    destination_id = input("Enter Destination ID: ").strip()
    if conn.execute("SELECT 1 FROM Destination WHERE destinationID = ?", (destination_id,)).fetchone() is None: # Existence Check
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
    if conn.execute("SELECT 1 FROM Aircraft WHERE aircraftID = ?", (aircraft_id,)).fetchone() is None: # Existence Check
        print("No aircraft with that ID.")
        return

    # Insert the new flight using user specified parameters
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

    # BaseQuery is shared by all filters
    # JOIN Destination for 'city' and Aircraft for 'model' FROM Flight,
    # so flights show names instead of raw foreign-key IDs.
    baseQuery = """
        SELECT flightNumber, departureTime, arrivalTime, status, city, model
        FROM Flight
        JOIN Destination ON Flight.destinationID = Destination.destinationID
        JOIN Aircraft    ON Flight.aircraftID    = Aircraft.aircraftID
    """

    # Update each query depending on user's choice.
    # Using a parameterised query to prevent SQL injection (security reasons)
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
        # DepartureTime is stored as "YYYY-MM-DD HH:MM", LIKE with "%" (wild card) matches the date prefix and ignores the time
        newQuery = baseQuery + " WHERE departureTime LIKE ? ORDER BY departureTime"
        rows = conn.execute(newQuery, (date + "%",)).fetchall()

    elif choice == "4":
        newQuery = baseQuery + " ORDER BY departureTime"
        rows = conn.execute(newQuery).fetchall()

    else:
        print("\nInvalid option.")
        return                          # leave the function, go back to main menu

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

def delete_flight(conn):
    """Delete a flight and its crew assignments."""

    clear_screen()
    print("Delete a flight\n")

    # List ALL flights with IDs
    flights = conn.execute("""
        SELECT flightID, flightNumber, departureTime, status, city
        FROM Flight
        JOIN Destination ON Flight.destinationID = Destination.destinationID
        ORDER BY flightID
    """).fetchall()
    for flight in flights:
        print(f"  {flight['flightID']}. {flight['flightNumber']} | {flight['departureTime']} | To: {flight['city']} | {flight['status']}")

    # Specify flight to delete
    flight_id = input("\nEnter the flight ID to delete: ").strip()
    if conn.execute("SELECT 1 FROM Flight WHERE flightID = ?", (flight_id,)).fetchone() is None:
        print("No flight found under that ID.")
        return

    # Confirm deletion
    confirm = input("Are you sure? (y/n): ").strip().lower()
    if confirm != "y":
        print("\nDeletion cancelled.")
        return

    # Remove crew assignments, then flight (FlightCrew rows reference flight so flightcrew rows must be deleted first)
    conn.execute("DELETE FROM FlightCrew WHERE flightID = ?", (flight_id,))
    conn.execute("DELETE FROM Flight WHERE flightID = ?", (flight_id,))

    conn.commit()
    print("\nFlight deleted.")

def assign_pilot(conn):
    """Assign a Pilot to a Flight by writing to the FlightCrew junction table."""

    clear_screen()
    print("Assign a pilot to a flight\n")

    # Note: Wasn't sure about ordering: flight first, then pilot. Or pilot first, then flight. Justify decision in report.

    # List ALL flights with IDs
    flights = conn.execute("""
        SELECT flightID, flightNumber, departureTime, status, city
        FROM Flight
        JOIN Destination ON Flight.destinationID = Destination.destinationID
        ORDER BY flightID
    """).fetchall()
    for flight in flights:
        print(f"  {flight['flightID']}. {flight['flightNumber']} | {flight['departureTime']} | To: {flight['city']} | {flight['status']}")

    # Ask which flight to assign the unspecified pilot to
    flight_id = input("\nEnter the flight ID: ").strip()
    if conn.execute("SELECT 1 FROM Flight WHERE flightID = ?", (flight_id,)).fetchone() is None:
        print("No flight found under that ID.")
        return

    # List ALL pilots with IDs
    print("\nPilots:")
    pilots = conn.execute(
        "SELECT pilotID, firstName, lastName, rank FROM Pilot ORDER BY pilotID"
    ).fetchall()
    for pilot in pilots:
        print(f"  {pilot['pilotID']}. {pilot['firstName']} {pilot['lastName']} ({pilot['rank']})")

    # Pick the pilot
    pilot_id = input("\nEnter the pilot ID: ").strip()
    if conn.execute("SELECT 1 FROM Pilot WHERE pilotID = ?", (pilot_id,)).fetchone() is None:
        print("No pilot found under that ID.")
        return

    # Pick the role
    allowed = ("Captain", "First Officer")
    while True:
        role = input("Enter role (Captain / First Officer): ").strip()
        if role in allowed:
            break
        print("  Invalid role, try again.")

    # Try to insert specified Pilot (PilotID, FlightID and role) into FlightCrew 
    # Compoisite primary key (flightID, pilotID) stops any duplication errors as it returns an integrity error
    try:
        conn.execute(
            "INSERT INTO FlightCrew (flightID, pilotID, role) VALUES (?, ?, ?)",
            (flight_id, pilot_id, role)
        )
        conn.commit()
        print("\nPilot assigned to flight.")
    except sqlite3.IntegrityError:
        print("\nThat pilot is already assigned to this flight.")

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
    """View all destinations and update a destination's name, city, or country."""

    clear_screen()
    print("Destination information\n")

    # List ALL destinations 
    destinations = conn.execute(
        "SELECT destinationID, airportCode, airportName, city, country "
        "FROM Destination ORDER BY destinationID"
    ).fetchall()
    for destination in destinations:
        print(f"  {destination['destinationID']}. {destination['airportCode']} - {destination['airportName']}")
        print(f"     {destination['city']}, {destination['country']}")

    # User Input choice
    print("\n  1. Update a destination")
    print("   2. Return to menu")
    choice = input("\nSelect an option (1-2): ").strip()
    if choice != "1":
        return

    # Get desired destination to update
    destination_id = input("\nEnter the destination ID to update: ").strip()
    match = conn.execute("SELECT 1 FROM Destination WHERE destinationID = ?", (destination_id,)).fetchone()
    if match is None:
        print("No destination found under that ID.")
        return

    # Print the selected destination's details
    clear_screen()
    selected = conn.execute(
        "SELECT destinationID, airportCode, airportName, city, country "
        "FROM Destination WHERE destinationID = ?", (destination_id,)).fetchone()
    
    print("Selected destination:\n")
    print(f"{selected['destinationID']}. {selected['airportCode']} - {selected['airportName']}")
    print(f"   {selected['city']}, {selected['country']}")

    # Choose which field to update
    print("\nWhat would you like to update?")
    print("  1. Airport name")
    print("  2. City")
    print("  3. Country")
    choice = input("\nSelect an option (1-3): ").strip()

    # Update Airport name loop
    if choice == "1":
        while True:
            airport_name = input("Enter new airport name: ").strip()
            if airport_name:
                break
            print("  Value cannot be empty, try again.")
        conn.execute("UPDATE Destination SET airportName = ? WHERE destinationID = ?",
                     (airport_name, destination_id))

    # Update City loop
    elif choice == "2":
        while True:
            city = input("Enter new city: ").strip()
            if city:
                break
            print("  Value cannot be empty, try again.")
        conn.execute("UPDATE Destination SET city = ? WHERE destinationID = ?",
                     (city, destination_id))

    # Update Country loop
    elif choice == "3":
        while True:
            country = input("Enter new country: ").strip()
            if country:
                break
            print("  Value cannot be empty, try again.")
        conn.execute("UPDATE Destination SET country = ? WHERE destinationID = ?",
                     (country, destination_id))

    else:
        print("\nInvalid option.")
        return

    conn.commit()
    print("\nDestination updated.")

def view_summaries(conn):
    """Show summary reports: number of flights per destination and per pilot."""

    clear_screen()
    print("Summary reports\n")

    # Summarise number of flights to each destination:
    # COUNT(*) counts the flights in each group
    # GROUP BY collapses the flight rows into one row PER destination.
    print("Flights per destination:\n")
    per_destination = conn.execute("""
        SELECT city, COUNT(*) AS flight_count
        FROM Flight
        JOIN Destination ON Flight.destinationID = Destination.destinationID
        GROUP BY Destination.destinationID
        ORDER BY flight_count DESC
    """).fetchall()
    for row in per_destination:
        print(f"  {row['city']}: {row['flight_count']}")

    # Summarise number of flights assigned to each pilot:
    # COUNT(*) counts the assignments for each pilot
    # GROUP BY collapses the FlightCrew rows into one row PER pilot
    # Warning: Inner JOIN means pilots with zero assignments do not appear
    print("\nFlights per pilot:\n")
    per_pilot = conn.execute("""
        SELECT firstName, lastName, COUNT(*) AS flight_count
        FROM FlightCrew
        JOIN Pilot ON FlightCrew.pilotID = Pilot.pilotID
        GROUP BY Pilot.pilotID
        ORDER BY flight_count DESC
    """).fetchall()
    for row in per_pilot:
        print(f"  {row['firstName']} {row['lastName']}: {row['flight_count']}")

# --- Menu Definitions --- 

# Menu Dictionary
MENU = {
#   Key: Label String,                     Function object     
    "1": ("Add a New Flight",              add_flight),
    "2": ("View Flights by Criteria",      view_flights),
    "3": ("Update Flight Information",     update_flight),
    "4": ("Delete a Flight",               delete_flight),
    "5": ("Assign Pilot to Flight",        assign_pilot),
    "6": ("View Pilot Schedule",           view_pilot_schedule),
    "7": ("View / Update Destination",     manage_destination),
    "8": ("View Summary Reports",          view_summaries),
}

def print_banner():
    """Display the menu banner to  user."""
    
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
    for key in MENU:                      # Iterate through menu dictionary keys
        label = MENU[key][0]              # Label = first item of (label string, function) tuple
        print(f"  {key}. {label}")
    print("  0. Exit")

def main():
    """Program entry point: open the DB, loop on the menu until the user exits."""
    conn = connect()                  # Create and store connection

    while True:                       
        print_menu()
        choice = input("\nSelect an option: ").strip()   # Read input and remove leading and trailing spaces

        if choice == "0":             # Exit case
            print("Closing.")
            break                     

        action = MENU.get(choice)     # Look up the inputed number (choice), returns None if invalid
        if action is None:            # Error: User inputed invalid number
            input("\nInvalid option. Press Enter to try again...")
            continue                  

        func = action[1]              # Get function (2nd item of [label, function] tuple)
        func(conn)                    # Call matching menu option, passing the stored connection
        input("\nPress Enter to return to the menu...")   # Pause so output stays readable
 
    conn.close()   # Close   connection

if __name__ == "__main__": # Run main() only when file is executed directly (as opposed to imported)
    main()

    