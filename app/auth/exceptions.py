class HandlerError(Exception):
    pass

class LoginErrorNotification(Exception): 
    """To be used to pass errors back to the webpage. Catch in webpage."""
    pass
