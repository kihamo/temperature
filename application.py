#! /usr/bin/python

from flask import Flask, render_template, send_from_directory
from flask.ext.restful import Api, Resource, fields, marshal_with
import subprocess
import os

app = Flask(__name__)

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
    value = subprocess.check_output(['owget', '-s', '3660', '/28.2950AF030000/temperature10']).strip()
    return {
      'temperature': float(value)
    }

class TemperatureList(Resource):
  def get(self):
    return []

api.add_resource(Temperature, '/now')
api.add_resource(TemperatureList, '/history')

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
