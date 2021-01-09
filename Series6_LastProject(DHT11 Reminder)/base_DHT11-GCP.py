import datetime
import json
import os
import ssl
import time

import jwt
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO


# dht
import time
import board
import adafruit_dht
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import schedule


# Used pins
YELLOW_LED_PIN = 20
GREEN_LED_PIN = 17
BUTTON_PIN = 21

# GCP parameters 
project_id = 'pivotal-myth-300919'           # Your project ID.
registry_id = 'RaspberryPi'                   # Your registry name.
device_id = 'RaspberryPi'                     # Your device name.
private_key_file = 'rsa_private.pem'          # Path to private key.
algorithm = 'RS256'                           # Authentication key format.
cloud_region = 'asia-east1'                   # Project region.
ca_certs = 'roots.pem'                        # CA root certificate path.
mqtt_bridge_hostname = 'mqtt.googleapis.com'  # GC bridge hostname.
mqtt_bridge_port = 8883                       # Bridge port.
message_type = 'event'                        # Message type (event or state).

def create_jwt(project_id, private_key_file, algorithm):
    # Create a JWT (https://jwt.io) to establish an MQTT connection.
    token = {
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        'aud': project_id
    }
    with open(private_key_file, 'r') as f:
        private_key = f.read()
    print('Creating JWT using {} from private key file {}'.format(
        algorithm, private_key_file))
    return jwt.encode(token, private_key, algorithm=algorithm)


def error_str(rc):
    # Convert a Paho error to a human readable string.
    return '{}: {}'.format(rc, mqtt.error_string(rc))


class Device(object):
    # Device implementation.
    def __init__(self):
        self.connected = False
        self.led1 = False
        self.led2 = False
        
        # Pins setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(YELLOW_LED_PIN,GPIO.OUT)
        GPIO.setup(GREEN_LED_PIN,GPIO.OUT)
        GPIO.setup(BUTTON_PIN,GPIO.IN)
        GPIO.setup(18,GPIO.IN)

    def update_led_state(self):
        if self.led1:
            GPIO.output(YELLOW_LED_PIN,GPIO.HIGH)
        else:
            GPIO.output(YELLOW_LED_PIN,GPIO.LOW)
        if self.led2:
            GPIO.output(GREEN_LED_PIN,GPIO.HIGH)
        else:
            GPIO.output(GREEN_LED_PIN,GPIO.LOW)

    def wait_for_connection(self, timeout):
        # Wait for the device to become connected.
        total_time = 0
        while not self.connected and total_time < timeout:
            time.sleep(1)
            total_time += 1

        if not self.connected:
            raise RuntimeError('Could not connect to MQTT bridge.')

    def on_connect(self, unused_client, unused_userdata, unused_flags, rc):
        # Callback on connection.
        print('Connection Result:', error_str(rc))
        self.connected = True

    def on_disconnect(self, unused_client, unused_userdata, rc):
        # Callback on disconnect.
        print('Disconnected:', error_str(rc))
        self.connected = False

    def on_publish(self, unused_client, unused_userdata, unused_mid):
        # Callback on PUBACK from the MQTT bridge.
        print('Published message acked.')

    def on_subscribe(self, unused_client, unused_userdata, unused_mid,
                     granted_qos):
        # Callback on SUBACK from the MQTT bridge.
        print('Subscribed: ', granted_qos)
        if granted_qos[0] == 128:
            print('Subscription failed.')

    def on_message(self, unused_client, unused_userdata, message):
        # Callback on a subscription.
        payload = message.payload.decode('utf-8')
        print('Received message \'{}\' on topic \'{}\' with Qos {}'.format(payload, message.topic, str(message.qos)))
        
        if not payload:
            return
        # Parse incoming JSON.
        data = json.loads(payload)
        if data['led1'] != self.led1:
            self.led1 = data['led1']
            if self.led1:
                print('Led1 is on')
            else:
                print('Led1 is off')

        if data['led2']!=self.led2:
            self.led2 = data['led2']
            if self.led2:
                print('Led2 is on')
            else:
                print('Led2 is off')

def getDHT11(dhtDevice):
    print('start')
    temperature_c = dhtDevice.temperature
    temperature_f = temperature_c * (9 / 5) + 32
    humidity = dhtDevice.humidity
    print("Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
            temperature_f, temperature_c, humidity))


    db = firestore.client()
    doc_ref = db.collection(u'data')                
    data = {
        u'Humidity': humidity,
        u'Temperature': temperature_c,
        u'Timestamp': 1609665807643
    }
    doc_ref.add(data)
    print('success')

           
def main():
    client = mqtt.Client(
        client_id='projects/{}/locations/{}/registries/{}/devices/{}'.format(
            project_id,
            cloud_region,
            registry_id,
            device_id))
    client.username_pw_set(
        username='unused',
        password=create_jwt(
            project_id,
            private_key_file,
            algorithm))
    client.tls_set(ca_certs=ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

    device = Device()

    client.on_connect = device.on_connect
    client.on_publish = device.on_publish
    client.on_disconnect = device.on_disconnect
    client.on_subscribe = device.on_subscribe
    client.on_message = device.on_message
    client.connect(mqtt_bridge_hostname, mqtt_bridge_port)
    client.loop_start()

    mqtt_telemetry_topic = '/devices/{}/events'.format(device_id)
    mqtt_config_topic = '/devices/{}/config'.format(device_id)

    # Wait up to 5 seconds for the device to connect.
    device.wait_for_connection(5)

    client.subscribe(mqtt_config_topic, qos=1)
    
    num_message = 0

    dhtDevice = adafruit_dht.DHT11(board.D18)
    if not firebase_admin._apps:
        cred = credentials.Certificate('serviceAccountKey.json')
        default_app = firebase_admin.initialize_app(cred)
    try:        
        while True:
            getDHT11(dhtDevice)
            device.update_led_state()
            # If button was pressed - send message.
            if not GPIO.input(BUTTON_PIN):   
                currentTime = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                num_message += 1
                # Form payload in JSON format.
                data = {
                    'num_message' : num_message,
                    'led1': device.led1,
                    'led2': device.led2,
                    'message': "Hello",
                    'time' : currentTime
                }
                payload = json.dumps(data, indent=4)
                print('Publishing payload', payload)
                client.publish(mqtt_telemetry_topic, payload, qos=1)
                # Make sure that message was sent once on press.
                while not GPIO.input(BUTTON_PIN):
                    time.sleep(0.1)   
            time.sleep(3)     



    except KeyboardInterrupt:
        # Exit script on ^C.
        pass
        GPIO.output(GREEN_LED_PIN,GPIO.LOW)
        GPIO.output(YELLOW_LED_PIN,GPIO.LOW)
        GPIO.cleanup()
        client.disconnect()
        client.loop_stop()
        print('Exit with ^C. Goodbye!')

if __name__ == '__main__':
    main()