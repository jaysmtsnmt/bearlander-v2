import re

def match_subject_prefix(string):
    pattern = r'^([A-Z]{2,3})'
    matches = re.findall(pattern, test)

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


for test in ["MA PROG", "CH(T)", "GP", "MA(H1)"]:
    prefix = match_subject_prefix(test)

    if not prefix: 
        #+ logging
        raise TypeError(f"Empty Subject Prefix | {test}")
    
    else:
        if match_subject_level(test) == 1:
            prefix = f"H{match_subject_level(test)}{prefix}"

        if is_prog(test):
            pass #search prefix for name, then return add (Program)

            

    

