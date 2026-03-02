import sqlite3


def create_database():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    # -----------------------------
    # Users Table
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0,
        active INTEGER DEFAULT 1
    )
    """)

    # -----------------------------
    # Memberships Table
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memberships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        contact_name TEXT NOT NULL,
        contact_address TEXT NOT NULL,
        adhar_card_no TEXT NOT NULL UNIQUE,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        membership_type TEXT CHECK(
            membership_type IN ('Six Months', 'One Year', 'Two Years')
        ),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # -----------------------------
    # Books / Movies Table
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT CHECK(category IN ('Book', 'Movie')),
        quantity INTEGER DEFAULT 1,
        status INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

    print("Database and all tables created successfully!")


# -----------------------------
# Add Membership Function
# -----------------------------
def add_membership(first_name, last_name, contact_name,
                   contact_address, adhar_card_no,
                   start_date, end_date, membership_type):

    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO memberships
        (first_name, last_name, contact_name, contact_address,
         adhar_card_no, start_date, end_date, membership_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (first_name, last_name, contact_name,
          contact_address, adhar_card_no,
          start_date, end_date, membership_type))

    conn.commit()
    conn.close()

    print("Membership added successfully!")

    


# -----------------------------
# Run Database Setup
# -----------------------------
if __name__ == "__main__":
    create_database()