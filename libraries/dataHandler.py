import logging
import os 
import hashlib
import pickle
import exceptionHandler as E

logging.basicConfig(
    handlers = [
        logging.FileHandler("Bearlander/cache/log.txt"),
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

        exists = False
        with open("Bearlander/cache/users.csv", "r") as file:
            for line in file.readlines():
                cemail, id = line.strip("\n").split(",")

                if email == cemail:
                    self.id = id
                    exists = True

        if not exists:
            def generate_user_id(email):
                email = email.strip().lower()
                digest = hashlib.sha256(email.encode()).digest()

                # First 4 bytes = 32 bits
                user_id = int.from_bytes(digest[:4], "big")

                return f"{user_id:08X}"  # 8-character hexadecimal
            
            self.id = generate_user_id(email)

            #complete checking if valid information
            from agent import Agent
            Agent(self).login() #attempts login, if fails, exception should be caught in main file!
            
            path = f"Bearlander/cache/data/{self.id}"
            if not os.path.exists(path):
                os.makedirs(path)

            with open(f"Bearlander/{path}/userdata.pickle", "wb") as file: pickle.dump(self, file) #dump userdata to a pickle file.
            with open(f"Bearlander/cache/users.csv", "a") as file: file.write(f"{email},{self.id}\n") #dump email & id to csv file
        
            logger.info(f"Constructor | ID: {self.id} | {self.email}")

        else: #if user already exists
            with open(f"Bearlander/{path}/userdata.pickle", "rb") as file: data = pickle.load(file)

            return data #return User object without creating new user object through loading userdata.pickle

    def setLoginDetails(self, email, password):
        self.email, self.password = email, password