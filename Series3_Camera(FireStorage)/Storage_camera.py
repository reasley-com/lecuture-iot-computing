from picamera import PiCamera
import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from uuid import uuid4

PROJECT_ID = "raspberry-pi-7b5e2"

cred = credentials.Certificate("./serviceAccountKey.json")
default_app = firebase_admin.initialize_app(cred, {
    'storageBucket': f"{PROJECT_ID}.appspot.com"    
})
bucket = storage.bucket()

def fileUpload(file):
    blob = bucket.blob('Images/'+file)
    new_token = uuid4()
    metadata = {"firebaseStorageDownloadTokens": new_token}
    blob.metadata = metadata

    blob.upload_from_filename(filename='./Images/'+file, content_type='image/jpeg')
    print(blob.public_url)

def execute_camera():
    subtitle = "Ras"
    suffix = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + '.jpg'
    filename = "_".join([subtitle, suffix])

    camera = PiCamera()
    camera.capture('/home/pi/Images/' + filename)
    fileUpload(filename)

execute_camera()