import re

from app.agents.calendar.subjectdatabase import *

def match_subject_prefix(string):
    pattern = r'^([A-Z]{2,3})'
    matches = re.findall(pattern, string)

    if len(matches) > 0: return matches[0]
    else: return None

def match_subject_level(string):
    pattern = r'\(H([0-9])\)'
    matches = re.findall(pattern, string)

    if len(matches) > 0: return int(matches[0])
    else: return None

def match_lesson_type(string):
    pattern = r'\(([A-Z])\)'
    matches = re.findall(pattern, string)

    if len(matches) > 0: return matches[0]
    else: return None

def is_prog(string):
    return "PROG" in string

def get_lesson_name(lesson:str, subjects:list):
    prefix = match_subject_prefix(lesson)
    level = match_subject_level(lesson)

    prefix = f"{prefix}{level}" if level else f"{prefix}"

    subjects = default_database + subjects 
    
    for subject in subjects:
        if prefix in subject["prefix"]:
            if not is_prog(lesson): return subject["name"]
            else: return f"{subject["name"]} (Program)"


# if __name__ == "__main__":
#     subjects = [{'name': 'Economics H2', 'code': 'H2ECONS', 'prefix': 'EC2'}, {'name': 'Chemistry H2', 'code': 'H2CHEM', 'prefix': 'CH2'}, {'name': 'Computing H2', 'code': 'H2CP', 'prefix': 'CP2'}, {'name': 'Physical Education', 'code': 'PE', 'prefix': 'PE'}, {'name': 'Project Work', 'code': 'PW', 'prefix': 'PW'}, {'name': 'General Paper H1', 'code': 'H1GP', 'prefix': 'GP'}, {'name': 'Mathematics H2', 'code': 'H2MATH', 'prefix': 'MA2'}]

#     for test in ["MA PROG", "CH(T)", "GP", "MA(H1)"]:
#         print(get_lesson_name(test, subjects))
        

