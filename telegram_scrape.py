from datetime import date
import json
import os
import re
import string
import sqlite3

from bs4 import BeautifulSoup
import requests
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import MessageEntityTextUrl
from telethon.sync import TelegramClient


conn = sqlite3.connect('deals.db', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
api_id = int(os.environ.get("TELEGRAM_API_ID"))
api_hash = os.environ.get("TELEGRAM_API_HASH")

phone = os.environ.get("TELEGRAM_PHONE")
username = os.environ.get("TELEGRAM_USERNAME")

client = TelegramClient(username, api_id, api_hash)
client.connect()

# Ensure you're authorized
if not client.is_user_authorized():
    client.send_code_request(phone)
    try:
        client.sign_in(phone, input('Enter the code: '))
    except SessionPasswordNeededError:
        client.sign_in(password=input('Password: '))


def get_messages():
    """
    Gets the last 30 messages from the kiasufoodies channel
    :return: iterator for the messages
    """
    kiasufoodies = client.get_entity("kiasufoodies")
    return client.iter_messages(kiasufoodies, limit=30)


def get_postal_codes(url):
    """
    Searches given URL for postal codes of food outlets
    :param url: URL to scrape from
    :return: list of postal codes
    """
    soup = BeautifulSoup(requests.get(url).text, features='html5lib')
    all_postal = soup.find_all(string=re.compile('^Singapore [0-9]{5}'))
    result = []
    for postal in all_postal:
        result.append(str(postal))

def parse_messages():
    conn.execute('DROP TABLE deals')
    conn.execute('CREATE TABLE deals (name text, enddate date, addresses text, days text, info text, timing text)')
    months = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
              "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
    year = date.today().year
    for message in get_messages():
        # print(message.entities)
        put_database = True
        address_done = False
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
                            timing = "Before {}".format(line.split(" ")[-1])
                        elif "onwards" in line:
                            timing = "After {}".format(line.split(" ")[-2])
                        elif "-" in line:
                            for word in line.split(" "):
                                if "-" in word:
                                    timing = word

            # get url that leads to info about discount
            if "Source" in line:
                info = line.split(":")[-1]

            # extract address
            if line[0] == "📍":
                if "#" in line:
                    addresses.append(line[1:])
                    address_done = True

        # parse provided link to find addresses if applicable
        if not address_done:
            for entity in message.entities:
                if type(entity) == MessageEntityTextUrl:
                    if 'goo.gl' not in entity.url:
                        addresses = get_postal_codes(entity.url)
        if put_database:
            conn.execute("INSERT INTO deals (name, enddate, addresses, info, timing) VALUES(?,?,?,?,?)", (name, last_date, json.dumps(addresses), info, timing))
    conn.commit()
    conn.close()


