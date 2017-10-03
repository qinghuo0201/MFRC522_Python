#!/usr/bin/env python

import RPi.GPIO as GPIO
import MFRC522
import signal

# Create an instance of class MFRC522
RFID_RC522 = MFRC522.MFRC522()

while True:
    # Scan for cards
    (requestStatus,RFIDType) = RFID_RC522.MFRC522_Request(RFID_RC522.PICC_REQIDL)

    # If a card is found, get card ID
    if requestStatus == RFID_RC522.MI_OK:
        (readIDStatus,cardID) = RFID_RC522.MFRC522_Anticoll()
        print "cardID: " + str(cardID)
        print " "

        # If readStatus is correct, select and authenticate the cardID
        if readIDStatus == RFID_RC522.MI_OK:
            blockAddress = RFID_RC522.MFRC522_SelectTag(cardID)
            print "Block Address: " + str(blockAddress)
            print " "

            # [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF] is Rraspberry Pi SPI Key
            authenticationStatus = RFID_RC522.MFRC522_Auth(RFID_RC522.PICC_AUTHENT1A, blockAddress, [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF], cardID)

            if authenticationStatus == RFID_RC522.MI_OK:
                (readDatastatus, blockAddress, blockData) = RFID_RC522.MFRC522_Read(blockAddress)
                RFID_RC522.MFRC522_StopCrypto1()
                if readDatastatus == RFID_RC522.MI_OK:
                    print "Block Data:  " + str(blockData)
                    print " "
                    print "Authentication Completed\n\n"
                else:
                    print "Authentication Error\n\n"
            else:
                print "Authentication Failed\n\n"

        else:
            print "Read Card ID Failed\n\n"
