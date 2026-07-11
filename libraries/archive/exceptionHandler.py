import logging 
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

logger = logging.getLogger("ExceptionHandler")
logger.info("ExceptionHandler Started.")

class AgentError(Exception): #superclass for Error Handling Agent
    """Superclass for Error Handling Agent."""

class LoginError(AgentError): #superclass for login errors 
    """Raised during failed logins"""

class IncorrectDetails(AgentError):
    """Raised during failed logins, when incorrect details are detected."""

class UnexpectedError(AgentError):
    """Raised unexpectedly"""

class TimetableEmptyError(AgentError):
    """Raised when timetable is empty during request."""

class UserHandlerError(Exception):
    """Raised when there is a user error."""

class IncorrectPassword(UserHandlerError):
    """Raised when there is an incorrect login provided. 
    Mismatch between existing userdata & password provided."""

class Notification(Exception):
    """Raise to pass error code back into flask application."""



