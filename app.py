# app.py
# Required Imports
import os
from flask import Flask, request, jsonify, render_template
from firebase_admin import credentials, firestore, initialize_app
import json
from collections import OrderedDict
from datetime import datetime, timedelta, date
import time
# Initialize Flask App
app = Flask(__name__)
# Initialize Firestore DB
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()
COL_TELEMETRY = db.collection('telemetry')
COL_BUFFER = db.collection('buffer')
DATABASE_FORMAT = open('database_format.json', 'r')
TJSON = './dataToCar.json'
sensors = ["battery_current", "battery_voltage"]

db_json = json.load(DATABASE_FORMAT)
 




def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        return os.stat(file_path)


@app.route('/document', methods=['PUT'])
def update():
    """
        update() : Update document in Firestore collection with request body
        Ensure you pass a custom ID as part of json body in post request
        e.g. json={'id': '1', 'title': 'Write a blog post today'}
    """
    buffer = dict()
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%Y-%m-%d")
    buffer = {"telemetry":{}}
    with open(TJSON) as json_data:
        fromCar = json.load(json_data)
        buffer['telemetry'].update(fromCar)
    try:
        print("Updating buffer")
        COL_TELEMETRY.document(timestampStr).update(buffer['telemetry'])
        print("Data was successfully uploaded")
    except Exception as e:
        return f"An Error Occured: {e}"


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
        datetime.strptime(date, dateFormat)
        # Check if ID was passed to URL query  

        
        data = COL_TELEMETRY.document(date).collection("battery_current").stream()

        return jsonify(data.to_dict), 200
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
    app.run(threaded=True, host='0.0.0.0', port=port)