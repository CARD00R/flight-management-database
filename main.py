# Flight Management Database - command-line interface
import sqlite3
import os

DB_FILE = "flights.db"                    # database reference

# --- Helper ---
def clear_screen():
    """Clears the terminal."""
    os.system("clear")

# --- Connection function ---  
def connect():
    """Open a connection to the SQLite database and return it."""
    conn = sqlite3.connect(DB_FILE)        
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row         # allows columns to be read by name
    return conn


# --- Menu Options --- 

def add_flight(conn):
    """Add a New Flight."""
    print("[add_flight] not implemeted yet")

def view_flights(conn):
    """View Flights based on input parameters (destination, status, date)."""
    print("[view_flights] not implemeted yet")

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

def print_menu():
    """Display the menu options to the user."""
    clear_screen()
    print("\n===== Flight Management System =====")
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

        if choice == "0":             # exit
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