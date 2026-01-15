import wocabee
import datetime
import traceback
import threading
from time import sleep
from selenium.webdriver.common.by import By
import getpass
import os
import json

def load_credentials():
    if os.path.exists("credentials.json"):
        with open("credentials.json", "r") as f:
            creds = json.load(f)
            return [(u, p) for u, p in creds.items()]
    return []

def save_credentials(username, password):
    all_creds = {}
    if os.path.exists("credentials.json"):
        with open("credentials.json", "r") as f:
            all_creds = json.load(f)
    all_creds[username] = password
    with open("credentials.json", "w") as f:
        json.dump(all_creds, f)

users = load_credentials()
def vsetky_baliky(woca):
    while woca.get_packages(woca.DOPACKAGE):
        woca.pick_package(0,woca.get_packages(woca.DOPACKAGE))
        while True:
            try:
                woca.do_package()
            except Exception as e:
                print(traceback.format_exception(e))
            else:
                break
        sleep(2)
        if woca.exists_element(woca.driver,By.ID,"continueBtn"):
            woca.get_element(By.ID,"continueBtn").click()
        try:
            woca.wait_for_element(5,By.ID,"backBtn")
            if woca.get_element_text(By.ID,"backBtn") in ["Uložiť a odísť", "Save and exit", "Save and leave"]:
                woca.get_element(By.ID,"backBtn").click()
        except:
            exit(0)

def do_wocabee(user):
    woca = wocabee.wocabee(user)
    woca.init()
    print(woca.name)
    for x in range(len(woca.get_classes())):
        woca.pick_class(x,woca.get_classes())
        vsetky_baliky(woca)
        woca.leave_class()
    woca.quit()

#while True:
    #if datetime.datetime.now().weekday() == 0 or 6: # if today is monday or sunday
if not users:
    username = input("username:")
    password = getpass.getpass("password:")
    save_credentials(username, password)
    users.append((username,password))
for x in users:
    print(x[0]) # display username
    thread = threading.Thread(target=do_wocabee,args=(x,))
    thread.start()
thread.join()
