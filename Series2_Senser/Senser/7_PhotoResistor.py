import spidev, time

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1350000

try:
    while True:
        r = spi.xfer2([1, (8 + 0) << 4, 0])
        adc_out = ((r[1]&3) << 8) + r[2]

        voltage = adc_out * 3.3 / 1024
        print("Reading=%d\tVoltage=%f" % (adc_out, voltage))
        time.sleep(1)
        
except KeyboardInterrupt:
    pass
    print('Exit with ^C. Goodbye!')
    GPIO.cleanup()
    exit()