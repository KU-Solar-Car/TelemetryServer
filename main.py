# app.py
# Required Imports
import os
from flask import Flask, request, jsonify, render_template
from firebase_admin import credentials, firestore, initialize_app
import json
from collections import OrderedDict
from threading import Timer
from datetime import datetime, timedelta, date
import time
import sys
# Initialize Flask App
app = Flask(__name__)
# Initialize Firestore DB
cred = credentials.Certificate('key.json')
f = open('headerKey.json', 'r')
headerKey = json.load(f)
default_app = initialize_app(cred)
db = firestore.client()
COL_TELEMETRY = db.collection('telemetry')
buffer = dict()
lastRead = dict()

dateTimeObj = datetime.now()
timestampStr = dateTimeObj.strftime("%Y-%m-%d")

SENSORS = ["battery_current", "battery_temperature", "battery_voltage", "bms_fault", "gps_lat","gps_lon", "gps_speed", "gps_time",
"gps_velocity_east", "gps_velocity_north", "gps_velocity_up", "motor_speed", "solar_current", "solar_voltage"]


def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        return os.stat(file_path)


def writeToFireBase():
    """
    This function will write to Firebase with the given buffer.
    """
    try:
        collections = COL_TELEMETRY.document(timestampStr).collections()
        for col, sensor in zip(collections, SENSORS):
            for sec in buffer.keys():
                data_per_timeframe = int(buffer[sec][sensor])
                print(data_per_timeframe)
                col.document("0").update({
                    str(sec) : data_per_timeframe
                })
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)




@app.route('/', methods=["GET"])
def default():
    """default endpoint with info for server"""
    return """KU Solar Car Telemetry Server
    \n/car - Main endpoint to use for sending from Arduino, requires an authentication header.
    \n/get/<date in YYYY-MM-DD format> - get data for a certain day.
    \n/create - create a table with correct fields for all the sensors.
    \n/recent - Get the most recent datapoints from the buffer
    """, 200


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
            for sensor in SENSORS:
                COL_TELEMETRY.document(timestampStr).collection(sensor).document("0").set({})
            return "Documents Created", 201
        except Exception as e:
            return f"An Error Occured: {e}", 400
    return "Document already exists", 200


@app.route('/car', methods=['GET', 'POST'])
def fromCar():
    countdownToBufferClear.start()
    auth = request.headers['Authentication']
    if auth != headerKey["Authentication"]:
        return f"An Error Occured: Authentication Failed", 401
    
    req_body = request.get_json()
    nowInSeconds = round((now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())
    if not COL_TELEMETRY.document(timestampStr).get().exists:
        create()
    collections = COL_TELEMETRY.document(timestampStr).collections()
    try:
        buffer[nowInSeconds] = {}
        for col, sensor in zip(collections, SENSORS):
            if sensor in req_body.keys():
                buffer[nowInSeconds][sensor] = req_body[sensor]
                lastRead[sensor] = req_body[sensor]
        if len(buffer) > (15*12) : #check buffer size and if it is greater than threshold
            writeToFireBase()
            countdownToFireBase.cancel()
            buffer.clear()
            return "Success, buffer limit reached but data uploaded, buffer cleared", 202
        return "Success, data added to buffer", 202
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return f"An Error Occured: {e}", 400


@app.route('/get/<date>', methods=['GET'])
def read(date):
    """
        read() : Fetches documents from Firestore collection as JSON
        todo : Return document that matches query ID
        all_todos : Return all documents
    """
    # dateFormat = "%Y-%m-%d"
    try:
        data = dict()
        collections = COL_TELEMETRY.document(date).collections()
        for col, sensor in zip(collections, SENSORS):
            for doc in col.stream():
                data[sensor] = doc.to_dict()
        return jsonify(data), 200
    except Exception as e:
        return f"An Error Occured: {e}", 404

@app.route("/recent", methods=["GET"])
def recentData():
    """
    Return the most recent data set that was sent from the car
    """
    try:
        data = dict()
        for sensor in lastRead.keys():
            data[sensor] = lastRead[sensor]            
        return jsonify(data), 200
    except Exception as e:
        return f"An Error Occured: {e}", 404




if __name__ == '__main__':
    app.run(debug=True, port=8080)