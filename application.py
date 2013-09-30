#!/usr/bin/env python

from flask import Flask, g, render_template, send_from_directory
from flask.ext.restful import Api, Resource 

from datetime import datetime
from email.utils import formatdate
from calendar import timegm

import subprocess
import os
import sqlite3

app = Flask(__name__)

'''
Database
'''
DATABASE = os.path.join(app.root_path, 'database.db')

def get_db():
  if not hasattr(g, '_database'):
    g._database = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES) 

  return g._database

@app.teardown_appcontext
def close_connection(exception):
  if hasattr(g, '_database'):
    g._database.close()

def query_db(query, args=(), one=False):
  cursor = get_db().execute(query, args)
  result = cursor.fetchall()
  cursor.close()
  return (result[0] if result else None) if one else result

'''
View
'''

@app.route('/')
def show_stats():
  return render_template('stats.html')

@app.route('/favicon.ico')
def favicon():
  return send_from_directory(os.path.join(app.root_path, 'static'),
         'favicon.ico',
         mimetype='image/vnd.microsoft.icon')

'''
API
'''
api = Api(app)

class Temperature(Resource):
  def get(self, **kwargs):
    row = query_db('select * from temperatures order by id desc limit 1', one=True)
    return {
      'date': formatdate(timegm(row[1].utctimetuple())),
      'temperature': row[2]
    }

class TemperatureNow(Resource):
  def get(self):
    value = subprocess.check_output(['owget', '-s', '3660', '/28.2950AF030000/temperature10']).strip()
    value = float(value)
    date = datetime.now()
 
    db = get_db()
    db.execute('insert into temperatures (date, value) values (?, ?)', [date, value])
    db.commit()

    return {
      'date': formatdate(timegm(date.utctimetuple())),
      'temperature': value
    }

class TemperatureList(Resource):
  def get(self):
    result = []

    for row in query_db('select * from temperatures'):
      result.append({
        'date': formatdate(timegm(row[1].utctimetuple())),
        'temperature': row[2]
      })

    return result 

  def post(self):
    value = subprocess.check_output(['owget', '-s', '3660', '/28.2950AF030000/temperature10']).strip()

    db = get_db()
    db.execute('insert into temperatures (date, value) values (?, ?)',
               [datetime.now(), float(value)]
    )
    db.commit()

    return '', 201 

api.add_resource(Temperature, '/last')
api.add_resource(TemperatureNow, '/now')
api.add_resource(TemperatureList, '/history')

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5000, debug=True)
