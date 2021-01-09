from flask import Flask, render_template, request
import datetime
import sys
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


application = Flask(__name__)


@application.route("/")
def hello():
    if not firebase_admin._apps:
        cred = credentials.Certificate('./serviceAccount.json')
        default_app = firebase_admin.initialize_app(cred)

    db = firestore.client()
    doc_ref = db.collection(u'data')
    docs = doc_ref.stream()

    current_time = datetime.datetime.now()

    Humidity = []
    Temperature = []
    Timestamp = []
    for doc in docs:
        Humidity.append(doc.to_dict()['Humidity'])
        Temperature.append(doc.to_dict()['Temperature'])
        Timestamp.append(doc.to_dict()['Timestamp'])

    return render_template('index.html', Humidity=Humidity, Temperature=Temperature, Timestamp=Timestamp)


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=80)
