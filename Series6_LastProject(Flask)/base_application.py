from flask import Flask, render_template, request
import sys
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


application = Flask(__name__)


@application.route("/")
def hello():
    cred = credentials.Certificate('./serviceAccount.json')
    firebase_admin.initialize_app(cred)

    db = firestore.client()
    doc_ref = db.collection(u'TestCollection').document(u'TestDocument')
    doc = doc_ref.get()
    print(doc.to_dict())

    return render_template('index.html')


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=int(sys.argv[1]))
