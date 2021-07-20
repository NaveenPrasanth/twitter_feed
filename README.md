## Twitter feed app 
This is a simple application to get twitter feed of a user and see them realtime. 
The user can search for words from the tweets and will be able to filter and sort tweets 
based on timestamp. After a login, the user's tweets will be periodically synced to the db to circumvent api limits.

#### Usage instructions
Requirements:
- Python 3.6 or above
- venv
- docker 
- twitter developer account (API access keys) 

##### Steps
* Clone the project
* Install dependecies with pip

    ```pip install -r requirements.txt```
* Set environmental variables
    ```
    export FLASK_APP=main_app
    export OAUTHLIB_INSECURE_TRANSPORT=1
    ```
* To run 

    ```./venv/bin/flask run``` 

##### Running in docker
  
###### Build image
docker build . -t flask_image

###### Run Image
docker run -d --name flask_container -p 80:80 flask_image 

#### Live demo at
http://52.66.208.89