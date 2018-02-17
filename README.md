# Stock App 

### Introduction:

This application is created as an exercise to download BSE bhavcopy from its site to parse and save in redis. There is also a celerybeat 
and worker component that run daily at 4PM (IST) to check for the latest version of copy. If found, it saves the new data in redis and 
deletes the old one.

### Technology Stack:

- Python 2.7
- CherryPy
- Redis
- VueJS for frontend
- Docker


### Backend

##### Prerequisites:
- Docker should be installed on your machine
- Latest version of docker-compose or version that supports docker-compose.yml version 2.1

##### Building and Running:

This application is docker friendly. Use below command to build and run this app after cloning the repo on your machine:

```
$ docker-compose up -d
```

#### Frontend

This repo has frontend code, however, it is not served through cherrypy. If you want to run frontend locally, use below commands
```
$ cd frontend
$ python -m SimpleHTTPServer .
```
Make sure to update API baseURL in `js/stock.js`. If everything goes well, you should be able to see this on your browser:
![UI-Screenshot](https://s3.ap-south-1.amazonaws.com/abhishek-bhavcopy/static/ui-screenshot.png)