from agents import Agent
from dataHandler import User
import exceptionHandler as E

try:
    user = User("jaydsoh@gmail.com", "pYTHON101", "Jayden Soh Guan Shun").initialise()

    agent = Agent(user)

    timetable_path = agent.scrapeTimetable()

except E.AgentError as e:
    print("exited with error")