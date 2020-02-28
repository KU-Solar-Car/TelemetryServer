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
DATABASE_FORMAT = 'database_format.json'
TJSON = './dataToCar.json'





def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        return os.stat(file_path)


@app.route('/update', methods=['GET', 'POST'])
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
    #while int(file_size(TJSON)) < 10:
    #    i = 0
    time.sleep(30)
    with open(TJSON) as json_data:
        fromCar = json.load(json_data)
        buffer['telemetry'].update(fromCar)

    try:
        print("Updating buffer")
        COL_TELEMETRY.document(timestampStr).update(buffer['telemetry'])
        print("Data was successfully uploaded")
        return update()
    except Exception as e:
        return f"An Error Occured: {e}"


@app.route('/', methods=['GET','POST'])
def create():
    """
        create() : Add document to Firestore collection with request body
        Ensure you pass a custom ID as part of json body in post request
        e.g. json={'id': '1', 'title': 'Write a blog post'}
    """
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%Y-%m-%d")
    if not COL_TELEMETRY.document(timestampStr).get().exists:
        buffer = dict()
        
        try:
            COL_TELEMETRY.document(timestampStr).set(buffer)
            print("====Document created====")
            return update()
        except Exception as e:
            return f"An Error Occured: {e}"
    else:
        return update()


        


@app.route('/get', methods=['GET'])
def read():
    """
        read() : Fetches documents from Firestore collection as JSON
        todo : Return document that matches query ID
        all_todos : Return all documents
    """
    try:
        # Check if ID was passed to URL query
        buffer_id = request.args.get('id')    
        if buffer_id:
            data = COL_BUFFER.document(buffer_id).get()
            return jsonify(data.to_dict()), 200
        else:
            all_data = [doc.to_dict() for doc in COL_BUFFER.stream()]
            return jsonify(all_data), 200
    except Exception as e:
        return f"An Error Occured: {e}"





@app.route('/delete', methods=['GET', 'DELETE'])
def delete():
    """
        delete() : Delete a document from Firestore collection
    """
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%Y-%m-%d")
    try:
        # Check for ID in URL query

        COL_TELEMETRY.document(timestampStr).delete()
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"
port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)