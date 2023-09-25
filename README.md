# Open-AI Integrated Django Project
Implementation of a chat-bot application by using the Open-AI's LLM models.

## Setup
* Create a virtual environment ```$ virtualenv venv```
* Install required packages ```$ pip install -r requirements.txt```
* ```.env``` variables:
  ```
  > DEBUG
  > SECRET_KEY
  > DB_PORT
  > DB_NAME
  > DB_USER
  > DB_PASSWORD
  > DB_HOST_SERVER
  > OPENAI_API_KEY
  ```
* Initial migration ```$ python manage.py migrate```
* Create super-user ```$ python manage.py createsuperuser```
* Runserver ```$ python manage.py runserver```
* Login to the Django admin site ```http://localhost:8000/admin/``` and create instances of AI Model with the details of the required Open AI's LLM models.
* Make use of the Swagger setup ```http://localhost:8000/swagger/``` to test-out the APIs.
