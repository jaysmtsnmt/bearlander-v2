import logging
import os 
import hashlib
import pickle
from libraries import exceptionHandler as E
from libraries import paths

CACHE_PATH = paths.get_CachePath()

logging.basicConfig(
    handlers = [
        logging.FileHandler(f"{CACHE_PATH}/log.txt"),
        logging.StreamHandler()
    ],
    level = logging.INFO, #determine which level of logs to display - at info, debug isn't displayed, but everything else is.
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)

logger = logging.getLogger("User")

class Handler: 
    class User: #for storage, should not be accessed outside of Handler function. But can be returned as an object for reference. 
        """Class type frame for storing user information."""

        def __init__(self, email:str, password:str, id:str, credentials, full_name:str):
            self.email = email
            self.password = password
            self.id = id
            self.google_credentials = credentials
            self.full_name = full_name

    def __init__(self, email:str, password:str):  #login and create at the same time.
        pass

    def login(self, email:str, password:str):
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
                with open(f"{CACHE_PATH}/data/{self.id}/userdata.pickle", "rb") as file: userObject = pickle.load(file)

            except FileNotFoundError: 
                t = f"Failed to find userdata.pickle for existing user | ID:{id} E:{email}"
                logging.critical(t)
                raise E.UserHandlerError(t)
            
            #checking if password matches. 
            if password == userObject.password:
                return userObject #return user credentials
            
            else:
                t = f"Incorrect password for {email}."
                logging.info(t)
                raise E.Notification(t) #should be caught in main file.

    def create_account(self, email:str, password:str):
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
                with open(f"{CACHE_PATH}/data/{self.id}/userdata.pickle", "rb") as file: userObject = pickle.load(file)

            except FileNotFoundError: 
                t = f"Failed to find userdata.pickle for existing user | ID:{id} E:{email}"
                logging.critical(t)
                raise E.UserHandlerError(t)
            
            #checking if password matches. 
            if password == userObject.password: #if password is correct, log them in.
                return userObject #return user credentials
            
            else: #if incorrect password, redirect them to login page. 
                t = f"An account with this email already exists! Please sign in instead."
                logging.info(t)
                raise E.Notification(t) #should be caught in main file.

        else: #attempt to create an account. 
            #check if email and password combination provided matches vjc portal.
            try:
                testObject = Handler.User(
                    email = email,
                    password = password,
                    id = None, 
                    credentials = None,
                    full_name = None
                )

                from agents import Agent
                Agent(testObject).login() #attempts login, if fails, exception should be caught in main file!

            except E.IncorrectDetails as e: #should be caught in the main file
                raise E.Notification("Your login details do not match your VJC Portal Login Details. ") #pass into main file
            


            def generate_user_id(email):
                email = email.strip().lower()
                digest = hashlib.sha256(email.encode()).digest()

                # First 4 bytes = 32 bits
                user_id = int.from_bytes(digest[:4], "big")

                return f"{user_id:08X}"  # 8-character hexadecimal
            
            



#storing data in users. 
class UserOld():
    def __init__(self, email, password=None, name=None):
        self.email, self.password = email, password
        self.full_name = name
        self.credential_data = None
        

    def initialise(self):
        """__summary__
        Should be called as User(param).initialise()

        New Users:
        Initialise, create cache files. 

        Existing Users:
        Load from corresponding userdata.pickle

        returns:
        user : User 
        
        """
        email, password, name, = self.email, self.password, self.full_name
        exists = False
        with open(f"{CACHE_PATH}/users.csv", "r") as file:
            for line in file.readlines():
                cemail, id = line.strip("\n").split(",")

                if email == cemail:
                    self.id = id
                    exists = True

        if not exists:
            if password == None:
                raise E.UserError("Registration failed. No info provided.")

            def generate_user_id(email):
                email = email.strip().lower()
                digest = hashlib.sha256(email.encode()).digest()

                # First 4 bytes = 32 bits
                user_id = int.from_bytes(digest[:4], "big")

                return f"{user_id:08X}"  # 8-character hexadecimal
            
            self.id = generate_user_id(email)

            #complete checking if valid information
            try:
                from agents import Agent
                Agent(self).login() #attempts login, if fails, exception should be caught in main file!

            except E.IncorrectDetails as e:
                raise E.IncorrectDetails(e)
            
            except E.AgentError as e:
                raise E.AgentError(e)
            
            path = f"{CACHE_PATH}/data/{self.id}"
            if not os.path.exists(path):
                os.makedirs(path)

            with open(f"{CACHE_PATH}/data/{self.id}/userdata.pickle", "wb") as file: pickle.dump(self, file) #dump userdata to a pickle file.
            with open(f"{CACHE_PATH}/users.csv", "a") as file: file.write(f"{email},{self.id}\n") #dump email & id to csv file
        
            logger.info(f"Constructor | ID: {self.id} | {self.email}")

            return self

        else: #if user already exists
            with open(f"{CACHE_PATH}/data/{self.id}/userdata.pickle", "rb") as file: data = pickle.load(file)

            return data #return User object without creating new user object through loading userdata.pickle


    def setLoginDetails(self, email, password):
        self.email, self.password = email, password

    def updateGoogleCredentials(self, credential_data):
        self.credential_data = credential_data

    def getGoogleCredentials(self):
        if self.credential_data == None: return None

        else:
            pass