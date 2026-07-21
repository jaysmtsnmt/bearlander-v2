class LogicError(Exception): #to catch your own mistakes
    pass

class BearlanderError(Exception):
    pass

class MissingCredentialsError(BearlanderError): 
    pass