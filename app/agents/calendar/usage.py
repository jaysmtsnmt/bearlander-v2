### The Bearlander Class
from app.agents.calendar.agent import Bearlander
from app.agents.calendar.exceptions import *

### Initialise ###
## Accessed: user.email, user.id, user.credentials / user.getCredentials()
instance = Bearlander(user)


### Functions ###

# Get Calendar ID #
## Returns String.
## Creates a new calendar "Bearlander" if does not exist.
instance.get_calendar_id() 

# Clear #
## Requires (datetimeObject) : object representing date to clear from. (>=)
## Returns integer : number of events deleted
## If batch execute fails, raises BearlanderError()
instance.clear(datetimeObject)

# Save #
## Requires (*timetables) : 1. Pass single timetable | 2. Pass *list (unpacked) of timetables
## Returns integer : number of events added
## If batch execute fails, raises BearlanderError()
instance.save(*timetables)
instance.save(timetable)

### Exception Handling
# 1. Missing Credentials
raise MissingCredentialsError("")
