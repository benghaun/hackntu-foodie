import json
import sqlite3

from flask import Flask
from flask import request, jsonify, render_template

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/list', methods=['GET'])
def deal_list():
    return render_template('list.html')


@app.route('/getdeals', methods=['GET'])
def getdeals():
    conn = sqlite3.connect('deals.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    cur = conn.execute('SELECT * FROM DEALS')
    rows = cur.fetchall()
    output = []
    for row in rows:
        addresses = None
        days = None
        if row[2] is not None:
            addresses = json.loads(row[2])
        if row[3] is not None:
            days = json.loads(row[3])
        output.append({"name": row[0],
                       "enddate": row[1],
                       "addresses": addresses,
                       "days": days,
                       "timing": row[4]})
    response = jsonify(output)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
