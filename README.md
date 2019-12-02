# Price Notification Service (Domio Challenge)

#### Pre-requisites:
- python 3
- `schedule` package
- read and write permission on the application folder: 'domio-challenge'

To check your python 3 version:

`python3 --version`

to install `schedule` package:

`pip install schedule`

### To run web application:

Add/update the following lines in `main.py` 

- (line 31) senderEmail
- (line 33) senderPassword
- (line 35) recipientEmail

If you are in python terminal, run the following command:

`./main.py`

If you are in any command terminal, run the following command: 

`python main.py`


## Description

#### Part 1 & 2
This program built with `Python` as back-end, and `Sqlite3`as a local relational database. It save to database. 
I created a `DatabaseManager` class manage all database related tasks. It uses the build-in `schedule` package to 
schedule tasks to read the API for every 5 seconds. Notification emails are using `email` package to send a simple email
message in HTML format. For properties, I created a `Property` class and `PropertyType` enum class to handle reading and 
writing these objects to database. There are some "TO DO"s for creating a configuration file to store all the 
static data (e.g. database name, email addresses and password etc) and write unit tests. (Manually ran and tested
for now)

#### Part 3
If there are dozens of different property types over time with their own messaging rules and platform, my design is 
flexible and easy enough to add new property types (e.g. add additional types in the `propertyType` table) and this 
won't impact the existing property types. To support different messaging ways, I would create a `messagingChannel` class
and extend to different types (such as email, sms or push) of rules and platform to handle all the different cases. 
But right now for simplicity, we will keep it as just email notifications.