# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['explain']

# %% ../nbs/00_core.ipynb 3
from hugchat import hugchat
from hugchat.exceptions import ModelOverloadedError
from hugchat.login import Login
from IPython.core.magic import register_cell_magic, needs_local_scope
from IPython.display import display, Markdown
from time import sleep

import logging
import os
import traceback

# %% ../nbs/00_core.ipynb 4
def _login(user: str = None, # username of the huggingchat account that is going to be used to send the messages. If None, it will be infered from possible json files in the working directory or requested to the user.
          password: str = None, # in plain-text, the password of that account. Not necessary if there exist a credentials file. Requested to the user otherwise.
          credentials_dir: str = "." # the path where the credentials file is. The working directory will be selected by default.
         ):
    """
    Logs the user into the huggingface chat using the user + password or the user + credentials json.
    """
    try:
        cookies = None
        json_file = [f for f in os.listdir() if ".json" in f]
        
        if not user and json_file:
            user = json_file[0].split(".")[0]

        sign: Login = Login(user, password)
        cookies = sign.loadCookiesFromDir(credentials_dir)
    except:
        logging.critical("Credentials file cannot be found. Requesting credentials...")
        
        if user:
            logging.info(f"Username infered from command line: {user}")
        else:
            user = input("Username: ")
        
        if not password:
            password = input("Password: ")

        confirm = input("Do you want to save your credentials? (y/n)")
        
        sign: Login = Login(user, password)
        cookies = sign.login()
        
        if confirm == "y":
            path = sign.saveCookiesToDir(credentials_dir)
            print(f"Your credentials file has been saved at: {path}")

    finally:
        return cookies
    
def _explain_exception(cookies, # cookies used in the connection.
                      exception_message, # error message sent to the model.
                      wait = 0 # number of seconds to wait until sending the message.
                     ):
    if not wait:
        logging.info("Conecting with hugchat to obtain the information about the exception.")
    else:
        sleep(wait)

    chatbot = hugchat.ChatBot(cookies = cookies.get_dict())
    user_confirmation = None
    
    try:
        while user_confirmation != "n":
            logging.warning("Be careful, the following response has been generated automatically by a Natural Language Processing Model, so the answer may be incorrect or false.")
            response = chatbot.chat(f"I was coding with Python and I have found this exception message: {exception_message}. How can I solve it?", temperature=0.85) # https://huggingface.co/spaces/huggingchat/chat-ui/discussions/170
            display(Markdown("## Huggingchat response [(online version)](https://huggingface.co/chat):"))
            display(Markdown(response))
            display(Markdown("---"))
            user_confirmation = input("\nDo you need another answer? (y/n)")
    except ModelOverloadedError as e:
        logging.warning(f"Model is overloaded, trying again in {wait + 5} seconds...")
        _explain_exception(cookies, exception_message, wait + 5)
    
@register_cell_magic
@needs_local_scope
def explain(line, # additional information added to the execution of the magic command. If provided, it will be trated as the username.
            cell, # cell that potentially raised the exception.
            local_ns # infered from the decorator. The local variables (needed to catch the imports).
           ):
    try:
        exec(cell, globals(), local_ns)
    except Exception as e:
        exception_message = traceback.format_exc()
        logging.critical(exception_message)
        
        user = line if line else None
        cookies = _login(user)
        
        _explain_exception(cookies, exception_message)
        
        raise e
