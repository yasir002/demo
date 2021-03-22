
### Open cmd or terminal and set the following environment variables to your local machine
##### 1. Replace <your_connection_string> with your azure storage connection string
   `setx AZURE_STORAGE_CONNECTION_STRING "<your_connection_string>"`

##### 2. Replace <storage_account_url> with your your azure storage account url 
   `setx CONTAINER_CLIENT "<storage_account_url>"`

##### 3. Replace <liftoff_username> with your liftoff username(or account code)
   `setx LIFTOFF_USERNAME "<liftoff_username>"`

##### 4. Replace <liftoff_password> with your liftoff password(or API key)
   `setx LIFTOFF_PASSWORD "<liftoff_password>"`
    
### Create following four containers in your storage account and set the access level to be public
1. `new-orders`
2. `updated-orders`
3. `completed-orders`
4. `deleted-orders`


### Clone or download the github Repository
`git clone git@github.com:triplek-tech/bcaa-launchpad.git`

### cd in to that directory
`cd bcaa-launchpad`


### Create and activate the virtual environment
`virtualenv venv`<br/>
`.\venv\scripts\activate`

### Install the requirements
`pip install -r requirements.txt`

### Runserver
`python manage.py runserver`
