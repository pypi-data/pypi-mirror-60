import os
import re

"""
A simple script for manage .env in django, is very easy, 
you just have to import this library in your manage.py
"""


def load(allow_override=False, path=""):
    try:
        env_file = open(path + ".env", "r")
        for linea in env_file.readlines():
            if linea != '\n' and not re.search(r'^(#.*)$', linea):
                variables = linea.split("=", 1)
                if allow_override or not os.environ.get(variables[0].strip()):
                    os.environ.setdefault(variables[0].strip(), variables[1].strip())
    except Exception as e:
        raise Exception('Not found .env or the file is wrong', e)
