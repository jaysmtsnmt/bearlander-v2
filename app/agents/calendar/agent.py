from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from datetime import datetime
from datetime import timedelta

import logging
from app.common.paths import *
from app.agents.calendar.exceptions import *

logging.basicConfig(
    handlers = [
        logging.FileHandler(f"{PATH_LOGTXT}"),
        logging.StreamHandler()
    ],
    level = logging.INFO, #determine which level of logs to display - at info, debug isn't displayed, but everything else is.
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)

logger = logging.getLogger("Agent")

class Bearlander:
    def __init__(self, user):
        self.user = user    
        credentials = user.get_credentials()

        if not credentials:
            t = f"Missing Credentials! | ID: {user.id} E: {user.email}"
            logger.critical(t)
            raise MissingCredentialsError(t)
        
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
        import filters
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