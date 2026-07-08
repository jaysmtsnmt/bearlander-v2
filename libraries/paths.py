"""
Handles the path finding for the different libaries
"""

import os
 
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) #Bearlander folder with static

def get_CachePath():
    target = "cache"

    for root, dirs, files in os.walk(ROOT):
        if target in dirs:
            return os.path.join(root, target)


def get_StaticsPath():
    target = "statics"

    for root, dirs, files in os.walk(ROOT):
        if target in dirs:
            return os.path.join(root, target)

def get_ResourcesPath():
    target = "resources"

    for root, dirs, files in os.walk(ROOT):
        if target in dirs:
            return os.path.join(root, target)
