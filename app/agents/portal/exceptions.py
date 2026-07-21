class AgentError(Exception):
    pass

class LoginError(AgentError):
    pass

class LogicError(Exception): #to catch your own mistakes
    pass