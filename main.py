import mysql.connector
import bcrypt
import re
import datetime

import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            user='root', 
            password='ALLY_root', 
            host='127.0.0.1',
            database='Banquet_db',
            autocommit=True  # ✅ CRITICAL: Enable autocommit by default
        )
        return conn
    except Error as err:
        print(f"Database connection error: {err}")
        return None

def register_attendee():
    """Register a new attendee account"""
    db = None
    cursor = None
    try:
        db = get_db_connection()
        if not db:
            return
        cursor = db.cursor()

        print("\n" + "="*40)
        print("📝 REGISTER NEW ACCOUNT")
        print("="*40)
        
        attendee_id = input("Enter your Attendee ID: ")
        first_name = input("Enter your first name: ")
        last_name = input("Enter your last name: ")
        phone = input("Enter your phone number: ")
        address = input("Enter your address: ")
        attendee_type = input("Enter attendee type (student/staff/guest/others): ")
        organization = input("Enter organization (PolyU/SPEED/HKCC/Others): ")

        # Insert attendee
        sql = """INSERT INTO Attendees (AttendeeID, a_fname, a_lname, a_phno, a_addrs, attendee_type, a_org, registrationDate, AccountStatus) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, CURDATE(), 'Active')"""
        
        params = (attendee_id, first_name, last_name, phone, address, attendee_type, organization)
        cursor.execute(sql, params)
        db.commit()  # Explicit commit

        print("✅ Account Registration Successful!")
        print(f"📋 Your Attendee ID: {attendee_id}")
        print("💡 Please login to access banquet reservations.")

    except Error as err:
        print(f"❌ Registration Failed: {err}")
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

def login():
    """Login and return attendee_id if successful"""
    db = None
    cursor = None
    try:
        db = get_db_connection()
        if not db:
            return None
        cursor = db.cursor()

        print("\n" + "="*30)
        print("🔐 LOGIN")
        print("="*30)
        
        attendee_id = input("Enter your Attendee ID: ")
        
        cursor.execute("""
            SELECT AttendeeID, a_fname, a_lname, AccountStatus 
            FROM Attendees 
            WHERE AttendeeID = %s
        """, (attendee_id,))
        
        attendee = cursor.fetchone()
        
        if not attendee:
            print("❌ Attendee ID not found. Please register first.")
            return None
        
        if attendee[3] == 'Inactive':
            print("❌ Your account is inactive. Please contact administrator.")
            return None
        
        print(f"✅ Login successful! Welcome back, {attendee[1]} {attendee[2]}!")
        return attendee[0]  # Return attendee_id

    except Error as err:
        print(f"❌ Login failed: {err}")
        return None
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

def view_banquets():
    """View all available banquets"""
    db = None
    cursor = None
    try:
        db = get_db_connection()
        if not db:
            return
        cursor = db.cursor()

        print("\n" + "="*60)
        print("📅 AVAILABLE BANQUETS")
        print("="*60)
        
        cursor.execute("""
            SELECT BIN, Banquet_name, Date, Time, Location, current_quota, Availability
            FROM Banquets 
            WHERE Availability = 'Y'
            ORDER BY Date
        """)
        banquets = cursor.fetchall()
        
        if not banquets:
            print("❌ No available banquets at the moment.")
            return
        
        print(f"🎪 Found {len(banquets)} available banquet(s):")
        for banquet in banquets:
            print(f"\n🎪 Banquet ID: {banquet[0]}")
            print(f"   Name: {banquet[1]}")
            print(f"   Date: {banquet[2]} at {banquet[3]}")
            print(f"   Location: {banquet[4]}")
            print(f"   Available Spots: {banquet[5]}")
            print("-" * 40)

    except Error as err:
        print(f"❌ Error viewing banquets: {err}")
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

def add_to_waitlist(attendee_id, banquet_id, banquet_name, total_quota):
    """Add user to waitlist when banquet is full"""
    db = None
    cursor = None
    try:
        db = get_db_connection()
        if not db:
            return
        cursor = db.cursor()

        # Method 1: Try to detect the correct column names
        cursor.execute("SHOW COLUMNS FROM Waitlist")
        columns = [column[0] for column in cursor.fetchall()]
        
        # Determine the correct column names
        status_column = 'Status' if 'Status' in columns else 'status' if 'status' in columns else None
        position_column = 'Position' if 'Position' in columns else 'position' if 'position' in columns else 'QueuePosition' if 'QueuePosition' in columns else None
        
        # Build the query based on available columns
        if status_column and position_column:
            # Count active waitlist entries
            cursor.execute(f"SELECT COUNT(*) FROM Waitlist WHERE BIN = %s AND {status_column} IN ('Pending', 'Confirmed', 'Active')", (banquet_id,))
            waitlist_count = cursor.fetchone()[0]
            waitlist_position = waitlist_count + 1
            
            # Get next waitlist ID
            cursor.execute("SELECT COALESCE(MAX(WaitlistID), 0) + 1 FROM Waitlist")
            next_waitlist_id = cursor.fetchone()[0]
            
            # Insert with status and position
            waitlist_sql = f"""INSERT INTO Waitlist (WaitlistID, BIN, AttendeeID, WaitlistDate, {status_column}, {position_column}) 
                             VALUES (%s, %s, %s, CURDATE(), 'Pending', %s)"""
            cursor.execute(waitlist_sql, (next_waitlist_id, banquet_id, attendee_id, waitlist_position))
            
        elif position_column:
            # Count all waitlist entries (no status filter)
            cursor.execute("SELECT COUNT(*) FROM Waitlist WHERE BIN = %s", (banquet_id,))
            waitlist_count = cursor.fetchone()[0]
            waitlist_position = waitlist_count + 1
            
            # Get next waitlist ID
            cursor.execute("SELECT COALESCE(MAX(WaitlistID), 0) + 1 FROM Waitlist")
            next_waitlist_id = cursor.fetchone()[0]
            
            # Insert with position only
            waitlist_sql = f"""INSERT INTO Waitlist (WaitlistID, BIN, AttendeeID, WaitlistDate, {position_column}) 
                             VALUES (%s, %s, %s, CURDATE(), %s)"""
            cursor.execute(waitlist_sql, (next_waitlist_id, banquet_id, attendee_id, waitlist_position))
            
        else:
            # Simple insert without status or position
            cursor.execute("SELECT COUNT(*) FROM Waitlist WHERE BIN = %s", (banquet_id,))
            waitlist_count = cursor.fetchone()[0]
            waitlist_position = waitlist_count + 1
            
            cursor.execute("SELECT COALESCE(MAX(WaitlistID), 0) + 1 FROM Waitlist")
            next_waitlist_id = cursor.fetchone()[0]
            
            waitlist_sql = """INSERT INTO Waitlist (WaitlistID, BIN, AttendeeID, WaitlistDate) 
                             VALUES (%s, %s, %s, CURDATE())"""
            cursor.execute(waitlist_sql, (next_waitlist_id, banquet_id, attendee_id))
        
        db.commit()
        
        print("✅ Added to waitlist successfully!")
        print(f"📋 Waitlist ID: {next_waitlist_id}")
        print(f"🎪 Banquet: {banquet_name}")
        print(f"📊 Your position in queue: #{waitlist_position}")
        print(f"📈 Total capacity: {total_quota}")
        print("💡 We will notify you if a spot becomes available.")

    except Error as err:
        print(f"❌ Waitlist registration failed: {err}")
        # Show more details for debugging
        print("💡 Please check your Waitlist table structure.")
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()
            
def make_reservation(attendee_id):
    """Make a reservation with proper waitlist triggering"""
    db = None
    cursor = None
    
    try:
        db = get_db_connection()
        if not db:
            return
        cursor = db.cursor()

        print("\n" + "="*50)
        print("📋 MAKE RESERVATION")
        print("="*50)
        
        # Show available banquets (quota > 0)
        cursor.execute("""
            SELECT BIN, Banquet_name, Date, Time, Location, current_quota 
            FROM Banquets 
            WHERE Availability = 'Y' AND current_quota > 0
        """)
        available_banquets = cursor.fetchall()
        
        # Show full banquets (quota = 0)
        cursor.execute("""
            SELECT BIN, Banquet_name, Date, current_quota 
            FROM Banquets 
            WHERE Availability = 'Y' AND current_quota <= 0
        """)
        full_banquets = cursor.fetchall()
        
        # Display available banquets
        if available_banquets:
            print("🎪 AVAILABLE BANQUETS (IMMEDIATE RESERVATION):")
            for banquet in available_banquets:
                print(f"   ID: {banquet[0]}, Name: {banquet[1]}, Date: {banquet[2]}, Spots Left: {banquet[5]}")
        
        # Display full banquets for waitlist
        if full_banquets:
            print("\n⏳ FULL BANQUETS (WAITLIST ONLY):")
            for banquet in full_banquets:
                print(f"   ID: {banquet[0]}, Name: {banquet[1]}, Date: {banquet[2]}")
        
        if not available_banquets and not full_banquets:
            print("❌ No banquets available.")
            return
        
        banquet_id = input("\nEnter Banquet ID: ")
        
        # ✅ FIX: Use autocommit for initial check, then manual transaction for reservation
        db.autocommit = True
        
        # First check if banquet exists and get current quota
        cursor.execute("SELECT Banquet_name, current_quota, Quota FROM Banquets WHERE BIN = %s AND Availability = 'Y'", (banquet_id,))
        banquet_info = cursor.fetchone()
        
        if not banquet_info:
            print("❌ Invalid Banquet ID or banquet not available.")
            return
        
        banquet_name, current_quota, total_quota = banquet_info
        
        # Check if quota is available
        if current_quota <= 0:
            print("❌ This banquet is full!")
            join_waitlist = input("Would you like to join the waitlist? (y/n): ").lower()
            if join_waitlist == 'y':
                add_to_waitlist(attendee_id, banquet_id, banquet_name, total_quota)
            return
        
        # Show available meals
        cursor.execute("SELECT mealID, DishName, Type, Price FROM Meals WHERE BIN = %s", (banquet_id,))
        meals = cursor.fetchall()
        
        if not meals:
            print("❌ No meals available for this banquet.")
            return
        
        print(f"\n🍽️ Available Meals for {banquet_name}:")
        for meal in meals:
            print(f"   Meal ID: {meal[0]}, Dish: {meal[1]}, Type: {meal[2]}, Price: ${meal[3]}")
        
        meal_id = input("Enter Meal ID: ")
        drink_choice = input("Enter drink choice: ")
        remarks = input("Enter any remarks (or press Enter to skip): ")

        # ✅ FIX: Now start manual transaction for the actual reservation
        db.autocommit = False
        db.start_transaction()
        
        # Lock and re-check quota (to handle race conditions)
        cursor.execute("SELECT current_quota FROM Banquets WHERE BIN = %s FOR UPDATE", (banquet_id,))
        current_quota = cursor.fetchone()[0]
        
        if current_quota <= 0:
            db.rollback()
            print("❌ Sorry, this banquet just became full!")
            join_waitlist = input("Would you like to join the waitlist? (y/n): ").lower()
            if join_waitlist == 'y':
                add_to_waitlist(attendee_id, banquet_id, banquet_name, total_quota)
            return
        
        # Get next reservation ID
        cursor.execute("SELECT COALESCE(MAX(ReservationID), 0) + 1 FROM Reservation")
        next_res_id = cursor.fetchone()[0]

        # Create reservation
        reservation_sql = """INSERT INTO Reservation (ReservationID, BIN, AttendeeID, MealID, DrinkChoice, Remarks, Status, RegistrationDate) 
                            VALUES (%s, %s, %s, %s, %s, %s, 'Confirmed', CURDATE())"""
        cursor.execute(reservation_sql, (next_res_id, banquet_id, attendee_id, meal_id, drink_choice, remarks))
        
        # Decrease quota
        cursor.execute("UPDATE Banquets SET current_quota = current_quota - 1 WHERE BIN = %s", (banquet_id,))
        
        db.commit()
        db.autocommit = True  # Reset to autocommit mode

        print("✅ Reservation Successful!")
        print(f"📋 Reservation ID: {next_res_id}")
        print(f"🎪 Banquet: {banquet_name}")
        print(f"📊 Status: Confirmed")

    except Error as err:
        print(f"❌ Reservation Failed: {err}")
        try:
            if db and db.in_transaction:
                db.rollback()
                db.autocommit = True  # Ensure we reset
        except:
            pass
    finally:
        # ✅ CRITICAL: Always reset autocommit and close connection
        try:
            if db:
                db.autocommit = True
        except:
            pass
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

def view_my_reservations(attendee_id):
    """View reservations for logged-in user"""
    db = None
    cursor = None
    try:
        db = get_db_connection()
        if not db:
            return
        cursor = db.cursor()

        print("\n" + "="*60)
        print("📊 MY RESERVATIONS")
        print("="*60)
        
        cursor.execute("""
            SELECT r.ReservationID, b.Banquet_name, b.Date, b.Time, b.Location,
                   m.DishName, m.Type, m.Price, r.DrinkChoice, r.Status, r.RegistrationDate
            FROM Reservation r
            JOIN Banquets b ON r.BIN = b.BIN
            JOIN Meals m ON r.MealID = m.mealID
            WHERE r.AttendeeID = %s
            ORDER BY b.Date DESC
        """, (attendee_id,))
        
        reservations = cursor.fetchall()
        
        if not reservations:
            print("❌ You have no reservations yet.")
            print("💡 Use 'Make Reservation' to book a banquet.")
            return
        
        for i, res in enumerate(reservations, 1):
            print(f"\n🎫 Reservation #{i}")
            print(f"   📅 Reservation ID: {res[0]}")
            print(f"   🎪 Banquet: {res[1]}")
            print(f"   📅 Date: {res[2]} at {res[3]}")
            print(f"   📍 Location: {res[4]}")
            print(f"   🍽️ Meal: {res[5]} ({res[6]})")
            print(f"   💰 Price: ${res[7]}")
            print(f"   🥤 Drink: {res[8]}")
            print(f"   📊 Status: {res[9]}")
            print(f"   📝 Booked on: {res[10]}")
            print("-" * 50)

    except Error as err:
        print(f"❌ Error viewing reservations: {err}")
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()

def main_menu():
    current_user = None
    
    while True:
        print("\n" + "="*50)
        print("🏨 BANQUET MANAGEMENT SYSTEM")
        print("="*50)
        
        if current_user is None:
            print("1. Register Account")
            print("2. Login")
            print("3. Exit")
            print("="*50)
            
            choice = input("Enter your choice (1-3): ")
            
            if choice == '1':
                register_attendee()
            elif choice == '2':
                current_user = login()
            elif choice == '3':
                print("👋 Thank you for using our system! Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
                
        else:
            print(f"👋 Welcome! (User ID: {current_user})")
            print("1. View Available Banquets")
            print("2. Make Reservation")
            print("3. View My Reservations")
            print("4. Logout")
            print("5. Exit System")
            print("="*50)
            
            choice = input("Enter your choice (1-5): ")
            
            if choice == '1':
                view_banquets()
            elif choice == '2':
                make_reservation(current_user)
            elif choice == '3':
                view_my_reservations(current_user)
            elif choice == '4':
                print("✅ Logged out successfully.")
                current_user = None
            elif choice == '5':
                print("👋 Thank you for using our system! Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()