"""
Domio Challenge: Price Notification Service
Author: Lena Zhao
Date: Dec 1, 2019

Assumptions:
1. API is always up and running (i.e. returns some data)
2. Sender's email credentials are valid
3.
"""

import sqlite3
import requests
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import schedule, time
from DatabaseManager import DatabaseManager
from Property import Property
from PropertyType import PropertyType


# TO DO:
# 1.setup a config file to read database name, sender's email address, password and list of recipients
# 2.setup a list of recipients email address

# database name
sqlite_name = 'properties_db.sqlite'
# Sender Email address
senderEmail = 'from@gmail.com'
# Sender Email password
senderPassword = 'examplepassword'
# Receipt Email address
recipientEmail = 'to@gmail.com'


'''
Main Function
'''
def main() -> None:
    # setup db
    db_setup(sqlite_name)

    # schedule to run the job for every 5 seconds
    schedule.every(5).seconds.do(job)

    while True:
        schedule.run_pending()
        time.sleep(0.1)


'''
Helper Method - Job to run tasks
'''
def job() -> None:

    # TO DO:
    # 1.Create an API call/connection to confirm that the server is up and running before requesting for a response
    # 2.Put the API endpoint a config file

    # API endpoint
    url = "https://interview.domio.io/properties/"

    # get the response in JSON format
    responseJson = getResponse(url)

    # add to database and send notifications if necessary
    process_request(sqlite_name, responseJson)


'''
Helper Method - Setup the database and creates all the necessary tables
'''
def db_setup(db_name: str) -> None:
    try:
        # access db
        with DatabaseManager(db_name) as db:
            # create a table for storing property data
            db.execute("""CREATE TABLE IF NOT EXISTS properties(
                        id TEXT NOT NULL PRIMARY KEY, 
                        type_id INTEGER NOT NULL, 
                        dynamic_display_price REAL, 
                        base_price REAL,
                        price_timestamp DATE NOT NULL DEFAULT (datetime('Now', 'localtime')))""")

            # create a table for tracking property type
            db.execute("""CREATE TABLE IF NOT EXISTS property_type(
                       id INTEGER NOT NULL PRIMARY KEY,
                       type TEXT)""")

            # insert data for property types
            db.execute("""INSERT OR IGNORE INTO property_type VALUES (1, 'apartment'), (2, 'home')""")

    except sqlite3.Error as e:
        print("db_setup Error: %s" % e.args[0])

    print("------ Finish Database Setup -------")


'''
Helper Method - Get the response from API endpoint and returns a dictionary object
'''
def getResponse(url: str) -> dict:

    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as err:
        print("getResponse() Error: %s" % err)
        sys.exit(1)


'''
Save the property data to database and send notification if conditions met
'''
def process_request(db_name: str, response: dict) -> None:
    with DatabaseManager(db_name) as db:

        # get the property list
        properties = response['properties']
        # stores a list of properties
        propList = []
        # insert to database flag
        insertDB = False
        #
        for prop in properties:
            # get property type
            propertyType = 0;

            if prop['type'].lower() == PropertyType.apartment.name:
                propertyType = PropertyType.apartment.value
            if prop['type'].lower() == PropertyType.home.name:
                propertyType = PropertyType.home.value

            # set property attributes
            id = prop['id']
            dynamicDisplayPrice = prop['dynamicDisplayPrice']
            basePrice = prop['basePrice']

            # check the current property exists in database
            db.execute("SELECT dynamic_display_price FROM properties WHERE id = ?", (id,))
            # get dynamic display price from database
            ddp = db.fetchone()

            # create a new Property object
            currProp = Property(id, propertyType, dynamicDisplayPrice, basePrice)

            # property doesn't exists, prepare to add to database
            if ddp is None:

                # add to property list
                propList.append(currProp.toTuple())
                # enable the insertion flag
                insertDB = True;

            # dynamic display price has changed
            elif ddp[0] != dynamicDisplayPrice:
                # update the existing property with new ddp
                db.execute("""UPDATE properties
                            SET dynamic_display_price = ?, 
                            price_timestamp = datetime('Now', 'localtime')
                            WHERE id = ?""", (dynamicDisplayPrice, id))

                # Requirement #2 - if condition met, send notification email
                if currProp.condition(propertyType):
                    # notify admin via email about updated ddp
                    notify(senderEmail, senderPassword, recipientEmail, currProp, ddp[0])


        # add non-existing properties to database
        if insertDB:
            db.executemany(""" INSERT OR IGNORE INTO properties(id, type_id, dynamic_display_price, base_price) 
                            VALUES(?, ?, ?, ?)""", propList)

        print("------ Finish Processing Request -------")

'''
Helper Method - Notify the admin via email with HTML message
'''
def notify(user: str, pwd: str, recipient: str, property: Property, prevDDP: int) -> list:

    # Create message container
    msg = MIMEMultipart('alternative')
    msg['Subject']= "[Dynamic Display Price] Change Notification"
    msg['From'] = user
    msg['To'] = recipient

    # Create the body of the message (an HTML version)
    html = """\
    <html>
        <head></head>
        <body>
            <p>Alert!<br>
                The Dynmaic Display Price for the following property has changed: <br><br>
                <b>ID:</b> """ + str(property.id) + """<br>
                <b>Type:</b> """ + str(PropertyType(property.typeId).name) + """<br>
                <b>Base Price:</b> $""" + str(property.basePrice) + """<br>
                <b>Previous DDP:</b> $""" + str(prevDDP) + """<br>
                <b>New DDP:</b> $""" + str(property.dynamicDisplayPrice) + """
            </p>
        </body>
    </html>"""

    # Record the MIME type of text/html
    part = MIMEText(html, 'html')
    # Attach part into message container
    msg.attach(part)


    # Send the message via local SMTP server
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(user, recipient, msg.as_string())
        server.close()
        print ('Successfully sent the email')
    except ConnectionError:
        print('Failed to send email')


if __name__ == '__main__':
    main()
