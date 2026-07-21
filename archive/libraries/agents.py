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

from libraries.paths import *
from libraries.user import * 

CACHE_PATH = get_CachePath()

logging.basicConfig(
    handlers = [
        logging.FileHandler(f"{CACHE_PATH}/log.txt"),
        logging.StreamHandler()
    ],
    level = logging.INFO, #determine which level of logs to display - at info, debug isn't displayed, but everything else is.
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)

logger = logging.getLogger("Agent")

class AgentError(Exception):
    pass

class LoginError(AgentError):
    pass

class LogicError(Exception): #to catch your own mistakes
    pass

class BearlanderError(Exception):
    pass


class Agent:
    load_timeout = 5

    def __init__(self, User):
        self.user = User

        options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("https://portal.vjc.edu.sg")

        logger.info(f"Initialised Agent | ID: {self.user.id} E:{self.user.email}")

    def login(self) -> bool: 
        """_summary_
        Logs in into VJC portal.

        returns: 
        True - Logged in
        False - Not logged in.
        """

        driver = self.driver
        user = self.user

        driver.find_element(By.ID, "login").send_keys(user.email)
        driver.find_element(By.ID, "password").send_keys(user.password)
        driver.find_element(By.ID, "btn_submit").click()

        try: 
            WebDriverWait(driver, Agent.load_timeout).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="left-panel"]/nav/ul/li[3]/a')) #wait until left panel MyVJC is loaded
            )

        except SelExceptions.TimeoutException:
            try: 
                driver.find_element(By.XPATH, '//*[@id="loginform"]/fieldset[1]/div')
                return False #since incorrect box was found
        
            except SelExceptions.NoSuchElementException:
                t = f"Page not loaded. Neither incorrect box nor panel was found. | ID: {user.id}"
                logger.critical(t)
                raise LoginError(t)
            
        return True
    
    def isLoggedIn(self):
        driver = self.driver
        
        try: driver.find_element(By.XPATH, '//*[@id="left-panel"]/nav/ul/li[3]/a')
        except SelExceptions.NoSuchElementException: return False
        return True


    def pull_student_data(self) -> dict:
        if not self.isLoggedIn():
            raise LogicError("Called pull_student_data before login.")
        
        #set session cookies for request
        session = requests.Session()
        for cookie in self.driver.get_cookies(): session.cookies.set(cookie['name'], cookie['value'])
        headers = {"User-Agent": self.driver.execute_script("return navigator.userAgent;")}

        student_data = {
            "name" : None,
            "portalID" : None,
            "subjects" : [],
            "class" : None 
        }

        ### Pull Student Name & ID 
        url = "https://portal.vjc.edu.sg/.do?action=chart&obj=Student_GetSharedFiles"
        response = session.get(url=url, headers=headers)
        
        student_data["portalID"] = response.json()["data"]["id"]
        student_data["name"] = response.json()["data"]["name"]

        ### Pull Student Class
        url = f"https://portal.vjc.edu.sg/.do?action=get&obj=Student&id={student_data['portalID']}"
        response = session.get(url=url, headers=headers)

        student_data["class"] = response.json()["data"]["cg_name"]

        ### Pull Student Classes
        url = "https://portal.vjc.edu.sg/.do?action=chart&obj=StudentSubject_ByStudent"
        response = session.get(url=url, headers=headers)

        subjects = response.json()["data"]

        for subject in subjects:
            name = subject["subject_name"]
            code = subject["subject_code"]
            prefix = subject["subject_sgprefix"]
            
            student_data["subjects"].append({
                "name" : name,
                "code" : code,
                "prefix" : prefix
            })

        logger.info(f"Sucessfully Pulled Student Data. | {student_data["name"]} | {student_data["class"]} | {len(student_data["subjects"])} Subjects")

        return student_data

    def scrapeTimetable(self, dateObject:datetime) -> tuple: 
        """_summary_
        Pulls timetable from VJC portal, using initalised user. 

        returns: 
        timetable_path : str 
        """

        if not self.isLoggedIn():
            raise LogicError("Called scrapeTimetable before login.")
        
        driver = self.driver

        # set cookies from selenium on requests
        session = requests.Session()
        for cookie in self.driver.get_cookies(): session.cookies.set(cookie['name'], cookie['value'])
        headers = {"User-Agent": self.driver.execute_script("return navigator.userAgent;")}

        startdate = dateObject.strftime(r"%Y-%m-%d")
        id = "b90412dca0f08d6b012eca44c4a09304"
        url = f"https://portal.vjc.edu.sg/.report?id={id}&startdate={startdate}T00:00:00Z"

        # get timetable
        response = session.get(url=url, headers=headers)
        logger.info(f"Scrape | RESP {response.status_code} | URL {response.url}") #timetable stored as response.text

        with open(f"{CACHE_PATH}/response.txt", "w") as file: file.write(response.text) #dumping response

        # ### New Method
        # url = f"https://portal.vjc.edu.sg/.do?action=chart&obj=Lesson_StudentTimetable&monday={startdate}T00:00:00Z"
        # response = session.get(url=url, headers=headers)
        # logger.info(f"Scrape | RESP {response.status_code} | URL {response.url}")
        
        # raw = response.json()["data"]
        # timeslots = raw.get("timeslots")

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

            subjects = self.user.subjects

            for day, lessons in timetable.items():
                if lessons != []: #to ensure that the lessons are mapped to the right day
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

        return (timetable, save_path)

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class Bearlander:
    def __init__(self, user: Handler.User):
        self.user = user    
        credentials = user.get_credentials()

        if not credentials:
            t = f"Called Bearlander before ensuring credentials were loaded."
            logger.critical(t)
            raise LogicError(t)
        
        else:
            self.service = build('calendar', 'v3', credentials=credentials)

        logger.info(f"Initalised Bearlander | ID: {user.id} E: {user.email}")

    def get_calendar_id(self) -> str:
        all_calendars = self.all_calendars = self.service.calendarList().list().execute().get('items', [])
        all_cal_names = [calendar["summary"] for calendar in all_calendars]

        if "Bearlander" not in all_cal_names: #create a new calendar
            calendar = {
                'summary' : "Bearlander",
                'timeZone' : 'Singapore'
            }

            calendar = self.service.calendars().insert(body=calendar).execute() #return a calendar data

        else:
            calendar = all_calendars[all_cal_names.index("Bearlander")] #return existing calendar data

        logger.info(f"Returning Calendar ID {calendar["id"]} | ID: {self.user.id} E: {self.user.email}")

        return calendar["id"]

    def clear(self, dateObj: datetime):
        """
        Clears the calendar after a specific date. 
        """
        cal_id = self.get_calendar_id()

        compiled = []
        events = self.service.events().list(calendarId=cal_id).execute()
        compiled = compiled + events["items"]
        while True: #to make sure that all events are fetched.
            # print(len(events.get("items", [])))
            token = events.get("nextPageToken")
            if not token:
                break

            events = self.service.events().list(
                calendarId=cal_id,
                pageToken=token
            ).execute()

            compiled = compiled + events["items"]

        batch = self.service.new_batch_http_request()
        i=0

        def callback(request_id, response, exception):
            if exception:
                t = f"Failed to clear event from calendar! | ID: {self.user.id} E: {self.user.email}"
                logger.critical(t)
                raise BearlanderError(t)

        logger.debug(events)
        for event in compiled:
            start = event["start"]

            if "dateTime" in start:
                event_date = datetime.fromisoformat(
                    start["dateTime"].replace("Z", "+00:00")
                ).date()

                if event_date >= dateObj.date():
                    batch.add(
                        self.service.events().delete(
                            calendarId=cal_id, 
                            eventId = event["id"]
                        ),
                        callback = callback
                    ) 

                    i+=1

        batch.execute()
        logger.info(f"Cleared {i} events. | ID: {self.user.id} E: {self.user.email}")
        return i #number of events deleted

    def save(self, *timetables):
        batch = self.service.new_batch_http_request()
        cal_id = self.get_calendar_id()

        def callback(request_id, response, exception):
            if exception:
                t = f"Failed to add event to calendar! | ID: {self.user.id} E: {self.user.email}"
                logger.critical(t)
                raise BearlanderError(t)
            
        n = 0
        #compress timetable dictionaries into a single batch of events. 
        import libraries.subject_filters as filters
        for timetable in timetables:
            for day, lessons in timetable.items():
                for lesson in lessons:
                    lesson_name = filters.get_lesson_name(
                        lesson=lesson["name"],
                        subjects=self.user.subjects
                    )

                    if lesson_name:
                        event = {
                            "summary" : lesson_name , 
                            "start" : {
                                "dateTime" : lesson["start"].isoformat(),
                                "timeZone" : "Asia/Singapore",
                            }, 
                            "end" : {
                                "dateTime" : lesson["end"].isoformat(),
                                "timeZone" : "Asia/Singapore"
                            },
                        }

                        batch.add(
                            self.service.events().insert(
                                calendarId=cal_id, 
                                body=event
                            ),
                            callback = callback
                        )
                        n += 1
        
        batch.execute()

        logger.info(f"Added {n} events | ID: {self.user.id} E: {self.user.email}")
        return n #number of events added
        
