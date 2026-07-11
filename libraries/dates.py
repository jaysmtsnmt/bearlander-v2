from datetime import datetime
from datetime import timedelta
import logging
from libraries.paths import *

CACHE_PATH = get_CachePath()

### RETURNS IN DATETIME OBJECTS
logging.basicConfig(
    handlers = [
        logging.FileHandler(f"{CACHE_PATH}/log.txt"),
        logging.StreamHandler()
    ],
    level = logging.INFO, #determine which level of logs to display - at info, debug isn't displayed, but everything else is.
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)

logger = logging.getLogger("Dates")

class LogicError(Exception):
    pass

def get_today() -> datetime:
    return datetime.now()

def get_start_of_this_week() -> datetime:
    return datetime.now() - timedelta(days=datetime.now().weekday())

def get_start_of_next_week() -> tuple:
    return get_start_of_this_week() + timedelta(days=7)

def get_period(start:int, end:int) -> tuple:
    """
    start & end: number of weeks from the start of this week.
        (-1 -> week before this week)
        (0 -> start of this week)
        (1 -> start of next week)

    end > start
    """

    if end <= start:
        raise LogicError(f"get_period | end:{end} <= start:{start}")
    
    else:
        reference = datetime.now() - timedelta(days=datetime.now().weekday())
        dates = []

        while start <= end:
            if start == 0: 
                dates.append(reference)

            else: 
                dates.append(reference + timedelta(days=7*start))

            start += 1

        return dates
    
