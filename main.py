# Flight Management Database - command-line interface
import sqlite3
import os

DB_FILE = "flights.db"                    # database reference

# --- Helper ---
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
    print("[add_flight] not implemeted yet")

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
    """Update Flight Information (such as departure time or status)."""
    print("[update_flight] not implemeted yet")

def assign_pilot(conn):
    """Assign a Pilot to a Flight which writes to the FlightCrew junction table."""
    print("[assign_pilot] not implemeted yet")

def view_pilot_schedule(conn):
    """View the flights the given pilot is assigned to."""
    print("[view_pilot_schedule] not implemeted yet")

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

    