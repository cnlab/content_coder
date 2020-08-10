# Megameta Content Analysis Coder

## Installation and Setup

----

#### HISTORY

* 2/24/20 mbod - initial setup instructions for CentOS linux 

----


## Setup

* The coder is a Python based web app using Flask, Mongodb and Bootstrap

### Installation

* __Mongodb__
    * For linux VM follow: https://docs.mongodb.com/manual/tutorial/install-mongodb-on-red-hat/
      1. Create a ``/etc/yum.repos.d/mongodb-org-4.2.repo` file so that you can install MongoDB directly using yum:      
      ```
          [mongodb-org-4.2]
          name=MongoDB Repository
          baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/4.2/x86_64/
          gpgcheck=1
          enabled=1
          gpgkey=https://www.mongodb.org/static/pgp/server-4.2.asc    
```
     2. Install mongodb-org package:  
        ```
        sudo yum install -y mongodb-org
        ```
     3. Start mongodb service
        ```
        sudo systemctl start mongod.service
        ```
    
* __Python virtual environment__
    1. Create a new virtual env based on latest version of Python 
```
            cd server_rev
            python3.7 -m venv env
          
    ```
    2. Activate the environment source env/bin/activate
```
            source env/bin/activate
            
        ``` 

    3. Install Python module requirememts
       * Modules
        - Flask 
        - pymongo 
        - pandas 
        - flask_cors 
        - flask-user 
        - Flask-MongoEngine
       * (will add a `requirements.txt`)
       
    4. Open firewall port for Flask server (default port is 5000)
       ```
       sudo firewall-cmd --zone=public --add-port=5000/tcp 
       ```

    
