import logging 
import os 
import hashlib
import pickle
from libraries.paths import *
from google.auth.transport.requests import Request

CACHE_PATH = get_CachePath()

logging.basicConfig(
    handlers = [
        logging.FileHandler(f"{CACHE_PATH}/log.txt"),
        logging.StreamHandler()
    ],
    level = logging.INFO, #determine which level of logs to display - at info, debug isn't displayed, but everything else is.
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)

logger = logging.getLogger("User")

class HandlerError(Exception):
    pass

class LoginErrorNotification(Exception): 
    """To be used to pass errors back to the webpage. Catch in webpage."""
    pass

class Handler: 
    class User: #for storage, should not be accessed outside of Handler function. But can be returned as an object for reference. 
        """Class type frame for storing user information."""
        def __init__(self, email:str, password:str, id:str, full_name=None, credentials=None, cls=None, subjects=None, portalID=None):
            self.email = email
            self.password = password
            self.id = id
            self.credentials = credentials
            self.full_name = full_name
            self.cls = cls #class
            self.portalID = portalID
            self.subjects = subjects

        def update_data_file(self):
            with open(f"{CACHE_PATH}/data/{self.id}/userdata.pickle", "wb") as file: pickle.dump(self, file) #dump userdata to a pickle file.
            with open(f"{CACHE_PATH}/users.csv", "a") as file: file.write(f"{self.email},{self.id}\n") #dump email & id to csv file

        def valid_credentials(self):
            return self.credentials != None
        
        def update_credentials(self, credentials):
            self.credentials = credentials
            self.update_data_file()

        def get_credentials(self):
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                    self.update_data_file()
                    return self.credentials
                
                elif self.credentials and self.credentials.expired:
                    logger.critical(f"Unable to refresh credentials! | ID:{self.id} E:{self.email}")
                    return None
                
                else:
                    logger.critical(f"No Google Account Linked! | ID:{self.id} E:{self.email}")
                    return None
            
            else:
                return self.credentials
            
        def clear_credentials(self):
            self.credentials = None
            self.update_data_file()

        def update_student_data(self, agent):
            if agent.isLoggedIn():
                student_data = agent.pull_student_data()

                self.full_name = student_data["name"]
                self.portalID = student_data["portalID"]
                self.subjects = student_data["subjects"]
                self.cls = student_data["class"]

                self.update_data_file()

            else:
                t = f"Called Update Student Data before logging in!"
                logger.critical(t)
                raise HandlerError(t)
            

    def __init__(self, email:str, password:str): #should always have an email or password.
        self.email, self.password = email, password

    def login(self):
        exists = False
        id = None
        email, password = self.email, self.password 

        with open(f"{CACHE_PATH}/users.csv", "r") as file: #if it exists, load the id, if not, don't load the id. 
            for line in file.readlines():
                cemail, cid = line.strip("\n").split(",")

                if email == cemail:
                    id = cid
                    exists = True
        
        if exists: #check if it is a valid log in
            try: #attempt to load user data of existing user 
                with open(f"{CACHE_PATH}/data/{id}/userdata.pickle", "rb") as file: userObject = pickle.load(file)

            except FileNotFoundError: 
                t = f"Failed to find userdata.pickle for existing user | ID:{id} E:{email}"
                logging.critical(t)
                raise HandlerError(t)
            
            #checking if password matches. 
            if password == userObject.password:
                # from libraries.agents import Agent
                # agent = Agent(userObject)
                # agent.login()
                # userObject.update_student_data(agent)
                return userObject #return user credentials
            
            else:
                t = f"Incorrect password for {email}."
                logging.info(t)
                raise LoginErrorNotification(t) #should be caught in main file. 

    def create_account(self):
        """__summary__
        Attempts to create an account with email & password passed in constructor. 

        returns: Handler.User object
        errors: LoginErrorNotification, HandlerError (critical)
        """

        email, password = self.email, self.password

        #checks if it is an existing account. 
        exists = False
        id = None
        with open(f"{CACHE_PATH}/users.csv", "r") as file: #if it exists, load the id, if not, don't load the id. 
            for line in file.readlines():
                cemail, cid = line.strip("\n").split(",")

                if email == cemail:
                    id = cid
                    exists = True
        
        if exists: #check if it is a valid log in
            try: #attempt to load user data of existing user 
                with open(f"{CACHE_PATH}/data/{id}/userdata.pickle", "rb") as file: userObject = pickle.load(file)

            except FileNotFoundError: 
                t = f"Failed to find userdata.pickle for existing user | ID:{id} E:{email}"
                logging.critical(t)
                raise HandlerError(t)
            
            #checking if password matches. 
            if password == userObject.password: #if password is correct, log them in.
                logging.info(f"Existing user found. | ID:{userObject.id} E:{userObject.email}")
                return userObject #return user credentials
            
            else: #if incorrect password, redirect them to login page. 
                t = f"An account with this email already exists! Please sign in instead."
                logging.info(t)
                raise LoginErrorNotification(t) #should be caught in main file.

        else: #attempt to create an account. 
            #check if email and password combination provided matches vjc portal.
            testObject = Handler.User(
                email = email,
                password = password,
                id = None, 
                credentials = None,
                full_name = None
            )

            from libraries.agents import Agent
            agent = Agent(testObject)
            if not agent.login(): #attempts login
                raise LoginErrorNotification("Your login details do not match your VJC Portal Login Details. ") #code will exit here
            

            def generate_user_id(email):
                email = email.strip().lower()
                digest = hashlib.sha256(email.encode()).digest()

                # First 4 bytes = 32 bits
                user_id = int.from_bytes(digest[:4], "big")

                return f"{user_id:08X}"  # 8-character hexadecimal

            user = Handler.User(
                email = email, 
                password = password, 
                id = generate_user_id(email),
                credentials = None,
                full_name = None
            )

            path = f"{CACHE_PATH}/data/{user.id}"
            if not os.path.exists(path):
                os.makedirs(path)

            user.update_data_file()
            user.update_student_data(agent)

            logging.info(f"Successful creation of user | ID:{user.id} E:{user.email}")
            return user

