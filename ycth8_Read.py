#!/usr/bin/env python

import RPi.GPIO as GPIO
import MFRC522Py
import signal

# Capture SIGINT for cleanup when the script is aborted
def endProgramHandler(signal,frame):
    print "End program"
    RFID_RC522.MFRC522_Destruct()

# Create an instance of class MFRC522
RFID_RC522 = MFRC522Py.MFRC522Py()

# Hook the SIGINT
signal.signal(signal.SIGINT, endProgramHandler)

while True:
    # Scan for cards
    (requestStatus,RFIDType) = RFID_RC522.MFRC522_Request(0x26)

    # If a card is found, get card ID
    if requestStatus == RFID_RC522.flag_ok:
        (readIDStatus,cardID) = RFID_RC522.MFRC522_Anticoll()
        print "cardID: " + str(cardID)
        print " "
        print " "
