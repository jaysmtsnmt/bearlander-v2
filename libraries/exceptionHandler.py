import logging 

logging.basicConfig(
    handlers = [
        logging.FileHandler("Bearlander/cache/log.txt"),
        logging.StreamHandler()
    ],
    level = logging.INFO, #determine which level of logs to display - at info, debug isn't displayed, but everything else is.
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)

logger = logging.getLogger("ExceptionHandler")
logger.info("ExceptionHandler Started.")

class AgentError(Exception): #superclass for Error Handling Agent
    """Superclass for Error Handling Agent."""
    logger = logging.getLogger("Agent")

class LoginError(AgentError): #superclass for login errors 
    """Raised during failed logins"""

class IncorrectDetails(AgentError):
    """Raised during failed logins, when incorrect details are detected."""
   
    def __init__(self, username, password):
        logger = AgentError.logger
        logger.info(f"Incorrect Login Details | U:{username}")

class UnexpectedError(AgentError):
    """Raised unexpectedly"""

    def __init__(self):
        logger = AgentError.logger
        logger.info(f"Unexpected Error Occured.")

class TimetableEmptyError(AgentError):
    """Raised when timetable is empty during request."""

    def __init__(self):
        logger = AgentError.logger
        logger.info(f"Timetable was empty, writing anyway.")

