import urllib
import json
import sqlite3

conn = sqlite3.connect('airqual.sqlite3')
cur = conn.cursor()

#Main table is values, additional tables for state, county, year, measure & units

cur.execute('''CREATE TABLE IF NOT EXISTS State (
            id INTEGER NOT NULL PRIMARY KEY UNIQUE,
            state TEXT UNIQUE
)''')

cur.execute('''CREATE TABLE IF NOT EXISTS County (
            id INTEGER NOT NULL PRIMARY KEY UNIQUE,
            county TEXT UNIQUE
)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Year (
            id INTEGER NOT NULL PRIMARY KEY UNIQUE,
            year INTEGER UNIQUE
)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Measure (
            id INTEGER NOT NULL PRIMARY KEY UNIQUE,
            measure TEXT UNIQUE,
            units TEXT UNIQUE
)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Airquality (
            id INTEGER NOT NULL PRIMARY KEY UNIQUE,
            Sample INTEGER,
            Airquality INTEGER,
            State_ID INTEGER,
            County_ID INTEGER,
            Year_ID INTEGER,
            Measure_ID INTEGER
)''')

url = 'https://data.cdc.gov/api/views/cjae-szjv/rows.json?accessType=DOWNLOAD'

response = urllib.urlopen(url)#open('rows.json')

data = json.load(response)

for item in data['data']:
    measurecode = item[8]
    ID = float(measurecode)

    if ID == 83 or ID == 85 or ID == 87:
        sample = item[0]
        measure = item[9]
        state = item[13]
        county = item[15]
        year = item[16]
        value = item[17]
        units = item[18]

        cur.execute("SELECT Sample FROM Airquality WHERE Sample= ?", (sample, ))
        
        try:
            data = cur.fetchone()[0]
            print "Found in database ",sample
            continue
        except:
            pass

        cur.execute('''INSERT OR IGNORE INTO State (state) VALUES (?)''', (state, ))
        cur.execute('SELECT id FROM State WHERE state = ? ', (state, ))
        State_ID = cur.fetchone()[0]

        cur.execute('''INSERT OR IGNORE INTO County (county) VALUES (?)''', (county, ))
        cur.execute('SELECT id FROM County WHERE county = ? ', (county, ))
        County_ID = cur.fetchone()[0]

        cur.execute('''INSERT OR IGNORE INTO Year (year) VALUES (?)''', (year, ))
        cur.execute('SELECT id FROM Year WHERE year = ? ', (year, ))
        Year_ID = cur.fetchone()[0]

        cur.execute('''INSERT OR IGNORE INTO Measure (measure, units) VALUES (?, ?)''', (measure, units))
        cur.execute('SELECT id FROM Measure WHERE measure = ? ', (measure, ))
        Measure_ID = cur.fetchone()[0]

        cur.execute('''INSERT OR REPLACE INTO Airquality (
                    Sample,
                    Airquality,
                    State_ID,
                    County_ID,
                    Year_ID,
                    Measure_ID)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                    (sample, value, State_ID, County_ID, Year_ID, Measure_ID))
conn.commit()
