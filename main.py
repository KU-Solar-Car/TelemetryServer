# app.py
# Required Imports
import os
from flask import Flask, request, jsonify, render_template
from firebase_admin import credentials, firestore, initialize_app
import json
from collections import OrderedDict
from datetime import datetime, timedelta, date
import time
import sys
# Initialize Flask App
app = Flask(__name__)
# Initialize Firestore DB
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()
COL_TELEMETRY = db.collection('telemetry')
COL_BUFFER = db.collection('buffer')
DATABASE_FORMAT = open('database_format.json', 'r')
BUFFER = open('d.json', 'r')
TJSON = './dataToCar.json'

db_json = json.load(DATABASE_FORMAT)
buffer_json = json.load(BUFFER)

SENSORS = ["battery_voltage", "battery_current", "battery_temperature", "bms_fault", "gps_time", "gps_lat","gps_lon",
"gps_velocity_east", "gps_velocity_north", "gps_velocity_up", "gps_speed", "solar_voltage", "solar_current", "motor_speed"]


def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        return os.stat(file_path)


@app.route('/document/<date>', methods=['PUT'])
def update(date):
    """
        update() : Update document in Firestore collection with request body
        Ensure you pass a custom ID as part of json body in post request
        e.g. json={'id': '1', 'title': 'Write a blog post today'}
    """
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%Y-%m-%d")
    collections = COL_TELEMETRY.document(date).collections()
    try:
        print("Updating buffer")
        for col, sensor in zip(collections, SENSORS):
            data_per_collection = dict()
            for sec in buffer_json.keys():
                data_per_collection[sec] = buffer_json[sec][sensor]["value"]
            col.document("0").update({
                "seconds":
                    data_per_collection
                
            })
        print("Data was successfully uploaded")
        return "Success", 202
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return f"An Error Occured: {e}", 400


@app.route('/document', methods=['POST'])
def create():
    """
        create() : Add document to Firestore collection with request body
        Ensure you pass a custom ID as part of json body in post request
        e.g. json={'id': '1', 'title': 'Write a blog post'}
    """
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%Y-%m-%d")
    if not COL_TELEMETRY.document(timestampStr).get().exists:
        try:
            COL_TELEMETRY.document(timestampStr).set({"Date": timestampStr})
            for sensor in db_json.keys():
                COL_TELEMETRY.document(timestampStr).collection(sensor).document("0").set({"seconds":{}})
            return "Documents Created", 201
        except Exception as e:
            return f"An Error Occured: {e}", 400
    return "Document already exists", 200


@app.route('/document/<date>', methods=['GET'])
def read(date):
    """
        read() : Fetches documents from Firestore collection as JSON
        todo : Return document that matches query ID
        all_todos : Return all documents
    """
    dateFormat = "%Y-%m-%d"

    try:
        # datetime.strptime(date, dateFormat)
        data = dict()
        
        collections = COL_TELEMETRY.document(date).collections()
        for col, sensor in zip(collections, db_json.keys()):
            for doc in col.stream():
                data[sensor] = doc.to_dict()
        return jsonify(data), 200
    except Exception as e:
        return f"An Error Occured: {e}", 404


@app.route('/document', methods=['DELETE'])
def delete():
    """
        delete() : Delete a document from Firestore collection
    """
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%Y-%m-%d")
    try:
        COL_TELEMETRY.document(timestampStr).delete()
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"
port = int(os.environ.get('PORT', 8080))


if __name__ == '__main__':
    app.run(debug=True, port=8080)