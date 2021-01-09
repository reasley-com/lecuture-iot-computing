import time
import board
import adafruit_dht

dhtDevice = adafruit_dht.DHT11(board.D18)
while True:
    try:
        temperature_c = dhtDevice.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dhtDevice.humidity
        print("Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
                temperature_f, temperature_c, humidity))
 
    except RuntimeError as error:
        time.sleep(2.0)
        continue
 
    time.sleep(2.0)