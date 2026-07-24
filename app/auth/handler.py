import hashlib
import logging

from app.auth.exceptions import *
from app.common.paths import *
from app.common.flaskerrorexceptions import * 
from app.common.variables import *
from app.query.query import query, Tables, Query

logging.basicConfig(
    handlers = [
        logging.FileHandler(f"{PATH_LOGTXT}"),
        logging.StreamHandler()
    ],
    level = logging.INFO, #determine which level of logs to display - at info, debug isn't displayed, but everything else is.
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)

logger = logging.getLogger("Handler")

class Handler: 
    def __init__(self, email:str, password:str): #should always have an email or password.
        self.email, self.password = email, password

    def get_user_object(self):
        results = query(
            table=Tables.USERS,
            operation=Query.SELECT,
            email = self.email
        )

        if results:
            id = results[0].get("id")
            data = query(
                table=Tables.USERDATA_DATABASE,
                operation=Query.SELECT,
                id = id
            )

            if data:
                data = data[0]
                from app.auth.user import User
                user = User()
                userObject = user.load_from_query_dictionary(data)

                return userObject
            
            else:
                return None
            
        else:
            return None

    def login(self):
        email, password = self.email, self.password 
        userObject = self.get_user_object()

        if userObject: #checking if password matches. 
            if password == userObject.password:
                if ON_LOGIN_SYNC_PORTAL:
                    from app.agents.portal.agent import Agent
                    agent = Agent(userObject)
                    if agent.login():
                        userObject.update_student_data(agent)
                    
                    else:
                        t = f"Incorrect password for {email}. Please use your VJC Portal Login Details. "
                        logger.info(t)
                        raise FlaskNotification(t) #should be caught in main file. 

                return userObject #return user credentials
            
            else:
                t = f"Incorrect password for {email}."
                logger.info(t)
                raise FlaskNotification(t) #should be caught in main file. 

        else:
            t = f"User not in database. | ID:{self.id} E:{self.email}"
            logger.critical(t)
            raise HandlerError(t)


    def create_account(self):
        """__summary__
        Attempts to create an account with email & password passed in constructor. 

        returns: Handler.User object
        errors: LoginErrorNotification, HandlerError (critical)
        """

        email, password = self.email, self.password

        userObject = self.get_user_object()

        if userObject:
            if password == userObject.password: #if password is correct, log them in.
                logger.info(f"Existing user found. | ID:{userObject.id} E:{userObject.email}")
                return userObject #return user credentials
            
            else: #if incorrect password, redirect them to login page. 
                t = f"An account with this email already exists! Please sign in instead."
                logger.info(t)
                raise FlaskNotification(t) #should be caught in main file.

        else: #attempt to create an account. 
            #check if email and password combination provided matches vjc portal.
            from app.auth.user import User
            testObject = User()
            testObject = testObject.pseudo(email, password)

            from app.agents.portal.agent import Agent
            agent = Agent(testObject)
            if not agent.login(): #attempts login
                raise FlaskNotification("Your login details do not match your VJC Portal Login Details. ") #code will exit here
            
            def generate_user_id(email):
                email = email.strip().lower()
                digest = hashlib.sha256(email.encode()).digest()

                # First 4 bytes = 32 bits
                user_id = int.from_bytes(digest[:4], "big")

                return f"{user_id:08X}"  # 8-character hexadecimal

            id = generate_user_id(email)
            user = User(
                email = email, 
                password = password, 
                id = id
            )

            user.update_data_file()
            user.update_student_data(agent)

            query(
                table=Tables.USERS,
                operation=Query.INSERT,
                values = {
                    "email" : email,
                    "id" : id
                    }
            )

            logger.info(f"Successful creation of user | ID:{user.id} E:{user.email}")
            return user
        
    def delete_account(self):
        userObject = self.get_user_object()

        if userObject:
            query(
                table=Tables.USERDATA_DATABASE, 
                operation=Query.DELETE,
                email = userObject.email, 
                id = userObject.id
            )

            query(
                table=Tables.USERS, 
                operation=Query.DELETE,
                email = userObject.email
            )

            logger.info(f"Successful deletion of user | ID:{userObject.email}")

        else:
            t = f"Failed to delete User: Does not exist. No error raised. | E: {self.email}"
            logger.critical(t)