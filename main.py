#!/usr/bin/env python3

import sys
import time
import socket

try:
    from machine import Pin, PWM, ADC  # @UnresolvedImport
    from network import WLAN, STA_IF  # @UnusedImport

    d1 = Pin(5, Pin.OUT)
    pwm1 = PWM(d1)
    pwm1.freq(50)

    SERVO_MIN = 25
    SERVO_MAX = 136

    def servo(n):
        pwm1.duty(int(SERVO_MIN + n * (SERVO_MAX - SERVO_MIN)))

    adc = ADC(0)

    def read_adc():
        return adc.read()

    real = True

    Timeout = OSError

except:

    def servo(n):
        print("Set servo to", n)

    def read_adc():
        return 600

    Timeout = socket.timeout

    real = False

# The address of the server to contact.
server = ""

# The angle of the server.
angle = 0.5


def read_angle():
    global angle

    try:
        with open("angle.txt", "r") as f:
            angle = float(f.read())
    except:
        pass


def write_angle():

    with open("angle.txt", "w") as f:
        f.write(str(angle))


def set_angle(a):
    global angle

    servo(a)

    if angle != a:
        angle = a
        write_angle()


def lock():
    if angle <= .22:
        return

    if read_adc() < 500:
        return

    time.sleep(.5)

    if read_adc() < 500:
        return

    set_angle(.22)


def force_lock():
    set_angle(.22)


def unlock():
    set_angle(.50)


def tick():
    time.sleep(.5)
    servo(angle + .05)
    time.sleep(.2)
    servo(angle)


def command(cmd):
    if cmd == b'lock':
        lock()
    elif cmd == b'unlock':
        unlock()
    elif cmd == b'force_lock':
        force_lock()
    elif cmd.startswith("network"):
        network_config(*cmd.split()[:1])
    else:
        print("Unknown command:", repr(cmd))


def network_config(ssid, password, server):
    with open("network.txt", "w") as f:
        f.write(ssid + "\n")
        f.write(password + "\n")
        f.write(server + "\n")

    start_network()


def start_network():

    global server

    with open("network.txt", "r") as f:
        ssid = f.readline()[:-1]
        password = f.readline()[:-1]
        server = f.readline()[:-1]

    print("SSID:", ssid, "PASSWORD:", password, "SERVER:", server)

    if not real:
        return

    sta = WLAN(STA_IF)
    sta.active(True)
    sta.connect(ssid, password)

    while not sta.isconnected():
        time.sleep(1)


def get_address():

    while True:
        try:
            return socket.getaddrinfo(server, 44444)[0][-1]
        except:
            print("Not getting address - trying again.")
            time.sleep(1)


def set_name(name):
    with open("name.txt", "wb") as f:
        f.write(name)


def main():

    with open("name.txt", "rb") as f:
        name = f.read()

    read_angle()
    servo(angle)

    start_network()
    tick()
    print("Started network.")

    addr = get_address()
    tick()
    print("Got address", addr)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(2.0)

    while True:
        print("Sending...")

        message = b"name=%s angle=%.2f adc=%d" % (name, angle, read_adc())
        s.sendto(message, addr)

        try:
            data, addr = s.recvfrom(1024)
        except Timeout:
            continue

        print("Received", repr(data), repr(addr))
        command(data)

        time.sleep(2.0)


if __name__ == "__main__":
    main()
