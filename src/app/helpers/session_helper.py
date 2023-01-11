from functools import wraps
from flask import request, make_response, current_app, redirect, session

def session_check(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if "mber_sn" in session:
            return func(*args, **kwargs)
        else:
            return redirect('/login')
    return wrap

def session_clear(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        print("session")
        for key in session.keys():
            print("[{}]={}".format(key, session[key]))
        print("removed")
        session.clear()
        return func(*args, **kwargs)
    return wrap

def load_menu(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if "mber_sn" in session:
            return func(*args, **kwargs)
        else:
            return redirect('/login')
    return wrap
