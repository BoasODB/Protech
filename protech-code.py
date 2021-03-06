#import stuff
import RPi.GPIO as GPIO
import os
import sys
import email, smtplib, ssl
from picamera import PiCamera
from time import sleep
from datetime import datetime
from os import path
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#basic selections
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

camera = PiCamera()

#e-mail info
subject = "Je pakket is bezorgd!"
body = "Protech heeft een pakket in je kluis gedetecteerd! -sent from Python"
sender_email = "SENDER@gmail.com"
receiver_email = "RECEIVER@gmail.com"
password = "PASSWORD"

timestamp = datetime.now().strftime("%Y_%m_%d-%I.%M.%S_%p")
filename = timestamp + '.jpg'

#select GPIO pins
GPIO.setup(29, GPIO.IN) #PIR
GPIO.setup(38, GPIO.OUT) #LED1
GPIO.setup(40, GPIO.OUT) #LED2
#SWITCH, we use an intern pull-down resistor to prevent short circuits
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#startup
#the PIR needs some time to adjust, the dots are just for fun
print("starting up")
sleep(1)
print(".")
sleep(1)
print(".")
sleep(1)
print(".")
sleep(1)
print("starting up PIR")
sleep(1)
print(".")
sleep(1)
print(".")
sleep(1)
print(".")
sleep(1)
print("adjusting PIR to surrounding infra-red")
sleep(1)
print(".")
sleep(1)
print(".")
sleep(1)
print(".")
sleep(1)

print("STARTUP TEST: flashing LED 2x")

#starting up, flashing LED 2x
count=0
while(count<2):
    count += 1
    GPIO.output(38, False)
    sleep(1)
    GPIO.output(38, True)
    sleep(1)

#start loop
while(1):

    #LED off
    GPIO.output(38, False)

    #don't run if there already is a package
    switch = GPIO.input(7)
    while(switch == 1):
        GPIO.output(40, True)
        sleep(0.1)
        GPIO.output(40, False)
        sleep(0.9)
        switch = GPIO.input(7)

    #LED off
    GPIO.output(38, False)
    GPIO.output(40, False)

    #read PIR
    print("monitoring PIR...")
    sleep(1)
    print("flashing LED until detection")

    pir = GPIO.input(29)
    while(pir == 0):
        GPIO.output(38, True)
        sleep(0.1)
        GPIO.output(38, False)
        sleep(0.9)
        pir = GPIO.input(29)

    #detection
    print("movement detected, taking picture...")

    #take picture
    camera.resolution = (2592, 1944)
    camera.framerate = 15
    camera.rotation = 180

    sleep(3)
    camera.capture(filename)

    print("made photo")

    #LED on
    GPIO.output(38, True)

    #loop until PIR = 0
    print("waiting until movement stops...")
    pir = GPIO.input(29)
    while(pir == 1):
        sleep(1)
        pir = GPIO.input(29)

    #look for package
    print("no movement, checking switch...")
    sleep(1)

    #LED off
    GPIO.output(38, False)

    #read switch
    print("reading switch...")
    switch = GPIO.input(7)
    sleep(1)
    print("package detected: " , switch)
    sleep(1)

    #if there is a package (switch = 1), send e-mail
    switch = GPIO.input(7)
    if(switch == 1):

        #turn red LED on (locked)
        GPIO.output(40, True)

        #send e-mail
        print("sending e-mail")

        #Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message["Bcc"] = receiver_email

        #Add body to email
        message.attach(MIMEText(body, "plain"))

        # Open  file in binary mode
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )

        # Add attachment to message and convert message to string
        message.attach(part)
        text = message.as_string()

        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, text)

        print("e-mail sent!")

    else:
        print("no e-mail sent")
        GPIO.output(40, False)

    sleep(1)

    #delete photo
    print("removing file: ", filename)
    os.remove(filename)

GPIO.cleanup()
