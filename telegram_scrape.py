from datetime import date
import json
import os
import string
import sqlite3
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError

conn = sqlite3.connect('deals.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
conn.execute('DROP TABLE deals')
conn.execute('CREATE TABLE deals (name text, enddate date, addresses text, days text, info text, timing text)')
api_id = int(os.environ.get("TELEGRAM_API_ID"))
api_hash = os.environ.get("TELEGRAM_API_HASH")

phone = '+6585717316'
username = 'benghaun'

# (2) Create the client and connect
client = TelegramClient(username, api_id, api_hash)
client.connect()

# Ensure you're authorized
if not client.is_user_authorized():
    client.send_code_request(phone)
    try:
        client.sign_in(phone, input('Enter the code: '))
    except SessionPasswordNeededError:
        client.sign_in(password=input('Password: '))

months = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
          "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
year = date.today().year
kiasufoodies = client.get_entity("kiasufoodies")
for message in client.iter_messages(kiasufoodies, limit=30):
    # print(message.entities)
    addresses = []
    days = []
    text = message.message
    if text is None:
        continue
    lines = text.splitlines()
    name = ""
    for char in lines[0]:
        if char in string.printable:
            name += char
    name = name.strip()
    first_tick = True
    last_date = date(year, 12, 31)
    info = ""
    timing = ""
    for line in lines:
        put_database = True
        if len(line) == 0:
            continue
        if line[0] == "✅":
            # information about discount (eg 1 for 1 milk tea)
            if first_tick:
                name += line[1:]
                first_tick = False
            else:
                # extract end date
                for month in months:
                    if month in line:
                        month_num = months[month]
                        day = None
                        print(line)
                        if "Until" in line:
                            day = int(line.split(" ")[2])
                        elif "-" in line:
                            words = line.split(" ")
                            for i in range(len(words)):
                                word = words[i]
                                if "-" in word:
                                    day = int(word.split("-")[-1])
                                    month_num = months[words[i+1][:3]]
                                    break
                        if day is not None:
                            last_date = date(year, month_num, day)
                            if last_date < date.today():
                                put_database = False
                        break

                # extract timings
                if "am" in line or "pm" in line:
                    if "Before" in line:
                        timing = "bef {}".format(line.split(" ")[-1])
                    elif "onwards" in line:
                        timing = "aft {}".format(line.split(" ")[-2])
                    elif "-" in line:
                        for word in line.split(" "):
                            if "-" in word:
                                timing = word

        # get url that leads to info about discount
        if "Source" in line:
            info = line.split(":")[-1]

        # extract address TODO parse website
        if line[0] == "📍":
            if "#" in line:
                addresses.append(line[1:])
    if put_database:
        conn.execute("INSERT INTO deals (name, enddate, addresses, info, timing) VALUES(?,?,?,?,?)", (name, last_date, json.dumps(addresses), info, timing))

conn.commit()
conn.close()