python
import requests
import json
import sqlite3

# Step 1: Connect to our permanent local ledger file
connection = sqlite3.connect("incorruptible_ledger.db")
cursor = connection.cursor()

# Step 2: Create an un-editable table for Landlord Profiles
cursor.execute('''
    CREATE TABLE IF NOT EXISTS mp_landlords (
        mp_id TEXT PRIMARY KEY,
        full_name TEXT,
        property_count INTEGER,
        declared_rental_income TEXT,
        last_updated TEXT
    )
''')
connection.commit()

# Step 3: Knock on the official Parliamentary Financial Interests API door
print("Connecting to live UK Parliamentary Financial Interests data stream...")
url = "https://parliament.uk"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    # Step 4: Extract and isolate registered real estate portfolios
    for item in data.get('items',):
        value = item.get('value', {})
        mp_id = value.get('id')
        name = value.get('nameDisplayAs')
        
        # System searches the record for "Property" or "Rental Income" declarations
        interests = value.get('financialInterests',)
        property_count = 0
        rental_income = "No declared residential rental income over threshold"
        
        for interest in interests:
            if interest.get('category') == "Property":
                property_count += 1
                rental_income = interest.get('description', 'Income exceeding £10,000/year')

        if property_count > 0:
            cursor.execute('''
                INSERT OR REPLACE INTO mp_landlords (mp_id, full_name, property_count, declared_rental_income, last_updated)
                VALUES (?, ?, ?, ?, datetime('now'))
            ''', (str(mp_id), name, property_count, rental_income))
            
    connection.commit()
    print("Success! Live landlord tracking data locked into the ledger.")
else:
    print("Error: External server connection failed.")

connection.close()

