**Google Maps, driven by Google Fusion Table**

The aim is to build a _single page app_ with a full viewport map on top and a list of addresses below based on Django 1.9.

A click at any location on the map: validate that this has a real address and it’s not some wood/mountain/ocean, etc.
If valid: save it to a simple db table with lat, lon, address (can be single string) and also to google fusion tables (decide what data).
Have a marker appear instantly after the click on the map based on the google fusion table data.
Update the list of addresses underneath the map with the location where you clicked.
Duplicates on google fusion table are not allowed.
Reset all data on google fusion tables and the database and start fresh


Set up and start the application:

Python2 (2.7)
 - `virtualenv .ve && source .ve/bin/activate && pip install -r requirements.txt && python manage.py migrate && python manage.py runserver`)
 
 
Python3 (3.6)
 - `virtualenv -p python3 .ve3 && source .ve3/bin/activate && pip3 install -r requirements.txt && python3 manage.py migrate && python3 manage.py runserver`


Open in a browser:
 - `http://127.0.0.1:8000/`


Issues / todos (to be resolved!):
 - google-api-python-client doesn't seem to properly urlencode addresses which contain single quotes, which causes an error
 - duplicate addresses are handled at the django model save level, which in theory should propogate up to the browser level.
 - double clicks are prevented through flags, which should prevent accidental duplicates (and thus errors)
 - the project is lacking tests, as integration tests take time to get right (time was lacking)
 - DEBUG = True is on
 - api_key and json credentials are placed in a zip (for limited protection from bots), and restricted to local browser use
 - consider using django-braces for various CBV mixins
 - make tests.py a module, and separate tests (and write more) into model, view, integration etc type tests
 - separate requirements into base, prod, test and dev 

