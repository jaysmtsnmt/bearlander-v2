### The Agent Class
from app.agents.portal.agent import Agent
from app.agents.portal.exceptions import *

### Initialise ### 
## Accessed: user.id, user.email, user.password
## Creates a new selenium driver
agent = Agent(user)


### Functions ###

# Log In #
## Returns Bool : True (Successful Log In) False (Unsuccessful Log In)
## If Page was not loaded and unsuccessful log in box was not detected, raises LoginError()
agent.login()

# Is Logged In #
## Returns Bool : True (is logged in) False (not logged in)
## Uses driver.find_element()
agent.is_logged_in()

# Release # 
## Releases and destroys self.driver / closes selenium window
agent.release()

# Pull Student Data #
## Returns dictionary : Student Data
agent.pull_student_data()

student_data = {
    "name" : str, #Computing H2
    "code" : str, #COMPUTING
    "prefix" : str, #H2CP ## This is used to filter relevant classes using regex
}

# Scrape Timetable #
## Parameters: dateObject:datetime - start date for pulling data (does not have to be monday)
## You should be passing a monday date for compatibility issues. 
## Returns dictionary : timetable dictionary
## If empty: returns {1: []}
## If not logged in, raises LogicError()
timetable = {
    1 : [ #day
        { #lesson
            "start" : datetimeObject,
            "end" : datetimeObject,
            "teacher" : str,
            "name" : str,
            "id" : str #it is unused so far because no correlation can be found between id and actual lesson id
        }
    ],

    2: [
        {

        }
    ]
}
