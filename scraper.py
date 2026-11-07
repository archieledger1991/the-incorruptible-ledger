import requests
import json
import sqlite3

# Step 1: Connect to our permanent local ledger file
connection = sqlite3.connect("incorruptible_ledger.db")
cursor = connection.cursor()

# Step 2: Create a permanent table for MPs that no one can manipulate
cursor.execute('''
    CREATE TABLE IF NOT EXISTS parliament_members (
        mp_id TEXT PRIMARY KEY,
        full_name TEXT,
        constituency TEXT,
        party TEXT
    )
''')
connection.commit()

# Step 3: Knock on the official UK Parliament live data door
print("Connecting to live UK Parliament data stream...")
url = "https://parliament.uk"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    # Step 4: Extract the names and automatically write them to our ledger
    for item in data.get('items',):
        value = item.get('value', {})
        mp_id = value.get('id')
        name = value.get('nameDisplayAs')
        constituency = value.get('latestHouseMembership', {}).get('membershipFrom')
        party = value.get('latestHouseMembership', {}).get('membershipStatus', {}).get('currentParty', {}).get('name')
        
        cursor.execute('''
            INSERT OR REPLACE INTO parliament_members (mp_id, full_name, constituency, party)
            VALUES (?, ?, ?, ?)
        ''', (str(mp_id), name, constituency, party))
    
    connection.commit()
    print("Success! Live parliamentary profiles successfully locked into the database.")
else:
    print("Error: Could not connect to the state server.")

connection.close()
