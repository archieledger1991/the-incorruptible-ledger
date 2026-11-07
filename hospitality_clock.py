python
import requests
import json
import sqlite3

# Step 1: Connect to our permanent local ledger file
connection = sqlite3.connect("incorruptible_ledger.db")
cursor = connection.cursor()

# Step 2: Create a permanent table for Gifts and Hospitality Tracking
cursor.execute('''
    CREATE TABLE IF NOT EXISTS mp_hospitality (
        mp_id TEXT,
        full_name TEXT,
        donor_identity TEXT,
        gift_value_gbp REAL,
        gift_description TEXT,
        date_received TEXT,
        last_updated TEXT,
        PRIMARY KEY (mp_id, donor_identity, date_received)
    )
''')
connection.commit()

# Step 3: Connect to the official Parliamentary Open Data registry for Gifts and Benefits
print("Connecting to live UK Parliament Gifts and Hospitality registry...")
url = "https://parliament.uk"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    
    # Step 4: Scan and isolate corporate hospitality packages
    for item in data.get('items', []):
        value = item.get('value', {})
        mp_id = value.get('id')
        name = value.get('nameDisplayAs')
        
        interests = value.get('financialInterests', [])
        
        for interest in interests:
            # Look specifically for Category 3: Gifts, benefits and hospitality from UK sources
            category = interest.get('category', '')
            if "Gifts" in category or "Hospitality" in category or "Benefits" in category:
                donor = interest.get('donorName', 'Unknown Corporate Donor')
                value_gbp = interest.get('valueAmount', 0.0)
                description = interest.get('description', '')
                date_rec = interest.get('dateReceived', 'Date Not Logged')
                
                cursor.execute('''
                    INSERT OR REPLACE INTO mp_hospitality 
                    (mp_id, full_name, donor_identity, gift_value_gbp, gift_description, date_received, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                ''', (str(mp_id), name, donor, float(value_gbp), description, date_rec))
                
    connection.commit()
    print("Success! Corporate gifts, benefits, and hospitality logs successfully locked into the ledger.")
else:
    print("Error: Could not establish a connection to the Westminster database.")

connection.close()
