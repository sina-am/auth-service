# Simple Authentication Microservice
***
<a name="installation"></a>
## Installation
### Obtaning the code
```
    $ git clone https://github.com/sina-am/auth-service
    $ cd auth-service 
```
### For A quick test you can run all the applications using docker-compose:
```
$ docker-compose -f docker-compose-full.yml up --build
```
And access the APIs docs from [here](http://127.0.0.1:8000/docs).

## Connecting to external services
The project uses following services:
- `RabitMQ` as a message broker.
- `MongoDB` as a main database.
- `Redis` as a caching system.

For running services on your local machine you need
Docker and Docker Compose installed on your system
along with a DockerHub account.

This will run all the necessery services
```
    $ docker-compose up -d --build
```

After running external services you're ready to 
run the main application.
```
    $ python -m venv .venv
    $ source .venv/bin/activate # For linux
    (.venv)$ pip install -r requirements.txt
    (.venv)$ cp .env.dev .env
```

To create an admin user:
```
    (.venv)$ python manager.py create-admin
```
Running the server
```
    (.venv)$ uvicorn app.main:app --reload
```
***

