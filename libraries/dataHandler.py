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

#storing data in users. 
class User():
    def __init__(self, email, password=None, name=None):
        self.email, self.password = email, password
        self.full_name = name

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