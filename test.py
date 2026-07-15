from libraries.user import *
from libraries.agents import *
from libraries import dates

email, password = ("jaydsoh@gmail.com", "pYTHON101")

try:
    handler = Handler(email, password)
    user = handler.login()

    agent = Agent(user)
    if agent.login(): #if login was successful
        list_of_dates = dates.get_period(0, 1)

        bearlander = Bearlander(user)
        bearlander.clear(list_of_dates[0])

        timetables = [agent.scrapeTimetable(date)[0] for date in list_of_dates]
        bearlander.save(*timetables) #use *timetables to unpack timetables. 

    else:
        print(f"Incorrect Password")

except LoginErrorNotification as e:
    print(e)

except LoginError as e:
    print(e)

except BearlanderError as e:
    print(e)

