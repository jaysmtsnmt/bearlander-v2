from libraries.user import *
from libraries.agents import *
from libraries.dates import *

email, password = ("email", "password")

### Instance Loading 
# always use a try except function in your main file. 
try: 
    # load the Handler object with the email and password
    handler = Handler(email, password)

    # for logins, use handler.login()
    user = handler.login() #returns Handler.User Object

    # for creating new accounts, use handler.create_account()
    user = handler.create_account() #returns Handler.User Object    

    # Load an instance of Agent with user parameters by passing with user object
    agent = Agent(user)
    if agent.login(): # must always run login BEFORE executing Agent functions

        date = get_start_of_next_week() #from dates.py returns datetime object
        timetable = agent.scrapeTimetable(date)

        if not user.get_credentials(): #check if user has credentials
            # Load an instance of Bearlander with user parameters by passing user object.
            # Will raise "LogicError" if instance is loaded before user has credentials / linked their google account
            bearlander = Bearlander(user)

        else:
            print(f"Please link your google account first!")

    else:
        print(f"Incorrect Password")


### ERROR HANDLING
# Errors will be reserved solely for unexpected cases or webpage notifications. 
# All other cases should be caught by NoneType or boolean checks. 
# LoginErrorNotificaiton -> pass back to login page in flask (have a dedicated flask.notify for errors)
except LoginErrorNotification as e: 
    print(e)

# LoginError -> VJC portal completely not loaded or Xpath cannot be found! 
except LoginError as e:
    print(e)

