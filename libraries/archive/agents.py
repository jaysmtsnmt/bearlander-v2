from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions as SelExceptions
import logging
import requests
import json
import pickle
from datetime import datetime
from datetime import timedelta

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

logger = logging.getLogger("Agent")

class Agent():
    load_timeout = 5

    def __init__(self, User):
        self.username, self.password = User.email, User.password
        self.user = User
        # options.add_argument("headless")
        # options.add_argument("log-level=3")
        options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(options=options) #options = options
        self.driver.get("https://portal.vjc.edu.sg/")
        #options.add_argument()
        
        logger.info(f"Agent started. | N: {User.full_name} | ID: {User.id}")
        

    def login(self):
        driver = self.driver
        driver.find_element(By.ID, "login").send_keys(self.username)
        driver.find_element(By.ID, "password").send_keys(self.password)
        driver.find_element(By.ID, "btn_submit").click()

        try: 
            WebDriverWait(driver, Agent.load_timeout).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="left-panel"]/nav/ul/li[3]/a')) #wait until left panel MyVJC is loaded
            )
        
        except SelExceptions.TimeoutException:
            try: #check for incorrect login detals
                driver.find_element(By.XPATH, '//*[@id="loginform"]/fieldset[1]/div')

                raise E.IncorrectDetails(f"{self.username}")

            except SelExceptions.NoSuchElementException:
                raise E.UnexpectedError("No Such Element.")
            
        return True
    
    def isLoggedIn(self):
        driver = self.driver

        try: driver.find_element(By.XPATH, '//*[@id="left-panel"]/nav/ul/li[3]/a')
        except SelExceptions.NoSuchElementException: return False
        return True

    def scrapeTimetable(self):
        """_summary_
        Pulls timetable from VJC portal, using initalised user. 

        returns: 
        timetable_path : str 
        """
        if not self.isLoggedIn():
            self.login()
    
        driver = self.driver

        # set cookies from selenium on requests
        session = requests.Session()
        for cookie in self.driver.get_cookies(): session.cookies.set(cookie['name'], cookie['value'])
        headers = {"User-Agent": self.driver.execute_script("return navigator.userAgent;")}
        
        startdate = "2026-06-29" #must find the monday
        id = "b90412dca0f08d6b012eca44c4a09304"
        url = f"https://portal.vjc.edu.sg/.report?id={id}&startdate={startdate}T00:00:00Z"

        # get timetable
        response = session.get(url=url, headers=headers)
        logger.info(f"Scrape | RESP {response.status_code} | URL {response.url}") #timetable stored as response.text

        with open(f"{CACHE_PATH}/response.txt", "w") as file: file.write(response.text) #dumping response

        if "var data = " in response.text:
            with open(f"{CACHE_PATH}/response.txt", "r") as file:
                for line in file.readlines():
                    if "var data =" in line:
                        raw = json.loads(line.strip("var data = ").rstrip(";\n"))
                        break

            #processing data
            def format_timetable(data):
                # Dynamically find the key that holds the lessons (e.g., 'lessons_cc07d...')
                lesson_key = next((key for key in data.keys() if key.startswith('lessons_')), None)
                
                if not lesson_key:
                    return {}

                timetable_dict = {}
                
                # Iterate through each day's data
                for day_data in data[lesson_key]:
                    weekday = day_data['weekday']
                    daily_lessons = []
                    
                    # A day can have multiple rows (e.g., parallel elective classes). 
                    # We loop through all rows and combine the lessons.
                    for row in day_data['rows']:
                        daily_lessons.extend(row['lessons'])
                        
                    timetable_dict[weekday] = daily_lessons
                    
                return timetable_dict
            
            #pull display information from HTML file/json
            timeslots = raw.get("timeslots")
            ref_startslot = timeslots[0]['start']
            ref_slotlength = timeslots[0]['end'] - timeslots[0]['start'] - 40
            ref_dates = raw.get("dates").split(",")
            logger.info(f"Pull | slot: {ref_slotlength} | {ref_dates}")

            timetable = format_timetable(raw)

            i = 0
            for day, lessons in timetable.items():
                if day == i+1: #to ensure that the lessons are mapped to the right day
                    ref_date = datetime.strptime(f"{ref_dates[i]}T{ref_startslot}", r"%Y-%m-%dT%H%M")

                    for lesson in lessons:
                        startslot, endslot = lesson['fromslot'], lesson['toslot']

                        #using timedelta to map start_time & end_time
                        start_time = ref_date + timedelta(minutes=(lesson['fromslot']-1)*ref_slotlength) 
                        end_time = ref_date + timedelta(minutes=(lesson['toslot'])*ref_slotlength)

                        lesson['start'], lesson['end'] = start_time, end_time
                        lesson['teacher'] = f"{lesson["line3"]}"
                        lesson['name'], lesson["id"] = lesson['line1'], lesson["lessons"]
                        del lesson['colour'], lesson['fromslot'], lesson['toslot'], lesson["line1"], lesson["line2"], lesson["line3"], lesson["line4"], lesson["lessons"]

                        logger.debug(f"Timetable | Processed {lesson}")
                        
                i += 1

        else: timetable = {1: []}

        date = datetime.strptime(f"{ref_dates[0]}T{ref_startslot}", r"%Y-%m-%dT%H%M")
        save_path = f"{CACHE_PATH}/data/{self.user.id}/{date.strftime(r"%m-%d-%Y")}.pickle"
        with open(save_path, "wb") as file: pass #pickle.dump(, file) 

        return save_path


class Bearlander():
    def __init__(self, user): #from user object, get loaded google calender credentials. 
        pass

    def clear(self): #clear all lessons from current week onwards.  
        pass 

    def update(self): #should check for week onwards and update by ITSELF
        pass

    def add(self, data): #data object to update -> load from save path  
        pass
