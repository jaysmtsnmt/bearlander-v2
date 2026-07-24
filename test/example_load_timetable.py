from app.agents.calendar.agent import Bearlander
from app.agents.portal.agent import Agent
from app.auth.user import User
from app.auth.handler import Handler
from app.common.dates import *


email = input("Email: ")
password = input("Password: ")

print("Start Test\n")

handler = Handler(email, password)
user = handler.create_account()

agent = Agent(user)
if agent.login():
    dates = get_period(0, 2)

    print(dates)
    
