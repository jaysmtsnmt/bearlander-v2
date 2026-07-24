import logging 
import os 
import hashlib
import pickle
from google.auth.transport.requests import Request

from app.common.paths import *
from app.auth.exceptions import *

logging.basicConfig(
    handlers = [
        logging.FileHandler(f"{PATH_LOGTXT}"),
        logging.StreamHandler()
    ],
    level = logging.INFO, #determine which level of logs to display - at info, debug isn't displayed, but everything else is.
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)

logger = logging.getLogger("User")

class User:
    def __init__(self, **kwargs):
        self.email, self.password = kwargs.get("email"), kwargs.get("password")
        self.full_name = kwargs.get("full_name")
        self.credentials = kwargs.get("credentials")
        self.cls = kwargs.get("cls")
        self.portalID = kwargs.get("portalID")
        self.id = kwargs.get("id")
        self.subjects = kwargs.get("subjects")

    def pseudo(self, email:str, password:str):
        self.email, self.password = email, password

        return self

    def load_from_query_dictionary(self, result:dict):
        self.email, self.password = result.get("email"), result.get("password")
        self.full_name = result.get("name")
        self.credentials = result.get("credentials")
        self.cls = result.get("class")
        self.portalID = result.get("portalid")
        self.id = result.get("id")
        self.subjects = result.get("subjects")

        return self

    def update_data_file(self):
        from app.query.query import query, Query, Tables
        
        query(
            table=Tables.USERDATA_DATABASE,
            operation=Query.INSERT,
            values = {
                "email" : self.email,
                "name" : self.full_name,
                "credentials" : self.credentials,
                "class" : self.cls,
                "portalid" : self.portalID,
                "id" : self.id,
                "subjects" : self.subjects, 
                "password" : self.password
            }
        )
    
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
        if agent.is_logged_in():
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
        

class User_Discontinued: #for storage, should not be accessed outside of Handler function. But can be returned as an object for reference. 
    """Class type frame for storing user information.
    
    args: email, password
    **kwargs : full_name, credentials, cls (class), portalID, id, subjects
    """
    def __init__(self, email:str, password:str, **kwargs):
        self.email, self.password = email, password
        self.full_name = kwargs.get("full_name")
        self.credentials = kwargs.get("credentials")
        self.cls = kwargs.get("cls")
        self.portalID = kwargs.get("portalID")
        self.id = kwargs.get("id")
        self.subjects = kwargs.get("subjects")
        

    def update_data_file(self):
        with open(f"{PATH_USER_DATA}/{self.id}/userdata.pickle", "wb") as file: pickle.dump(self, file) #dump userdata to a pickle file.
        with open(f"{PATH_USER_DATA}/users.csv", "a") as file: file.write(f"{self.email},{self.id}\n") #dump email & id to csv file

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
        if agent.is_logged_in():
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
        
