import argparse
import logging
try:
    from colorama import init as color_init, Fore, Style
    color_init()
except Exception:
    class _D:
        RED = GREEN = YELLOW = CYAN = MAGENTA = ""
    class _S:
        RESET_ALL = ""
    Fore = _D()
    Style = _S()

class ColorFormatter(logging.Formatter):
    def format(self, record):
        lvl = record.levelname
        c = {
            "INFO": Fore.CYAN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED,
            "DEBUG": Fore.MAGENTA,
        }.get(lvl, "")
        msg = super().format(record)
        return f"{c}{msg}{Style.RESET_ALL}"
from selenium.webdriver.common.by import By
from time import sleep
import getpass
from wocabee import wocabee
import traceback
import signal
import sys

woca = None
_exiting = False
logger = logging.getLogger("main")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = ColorFormatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def signal_handler(sig, frame):
    global _exiting
    if _exiting:
        return
    _exiting = True
    logger.info("Exiting gracefully...")
    try:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
    except Exception:
        pass
    if woca:
        try:
            woca.quit()
        except:
            pass
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)






def leaderboard():

    end = ""
    leaderboard = woca.get_leaderboard()
    
    first_place = leaderboard[0]
    first_place_points = 0    
    try:
        first_place_points = int(first_place["points"])
    except:
        print(first_place)
    for x in leaderboard:
        end+=(f"#{x['place']:<2}: {x['name']:<20} ({'🟢' if x['online'] else '🔴'}) {x['points']:<5} (diff to #1 = {int(first_place_points)-int(x['points']):>5}) {x['packages']}\n")
    print(end)
    woca.quit()


def miesto(miesto:int):
    leaderboard = woca.get_leaderboard()
    nplace = leaderboard[miesto-1]
    ourpoints = [x["points"] for x in leaderboard if x["name"] == woca.name][0]
    if nplace["name"] != woca.name:
        if int(nplace["points"]) > int(ourpoints):
            target_points = int(nplace["points"]) - int(ourpoints)
            woca.pick_package(0,woca.get_packages(woca.PRACTICE))
            print(f"{woca.name} bude mať {nplace['points']} (#{miesto})")
            woca.get_points(f"+{target_points}")
            
def bodiky(body: int):
    logger.info(f"[#] Doing {body} wocapoints for {woca.name}")
    woca.get_points(f"+{body}")
    woca.quit()


def chybajuce_baliky(trieda: str,komu: str):
    packages = woca.get_packages(woca.GETPACKAGE)
    end = []
    for package in packages:
        items = package.items()
        for name,playable in items:         
            if playable:
                end.append(name)
    woca.quit()
    print(end)
    return end
                
    
def zrob_balik(package):
    woca.pick_package(package,woca.get_packages(woca.DOPACKAGE))
    while True:
        try:
            woca.do_package()
        except Exception as e:
            print(traceback.format_exception(e))
        else:
            break

def nauc_balik(trieda: str,komu: str):
    pass

def vsetky_baliky():
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

parser = argparse.ArgumentParser(
                    prog='WocaBot',
                    description='Multi-purpose bot for wocabee',
                    epilog='I am not responsible for your teachers getting angry :)')

parser.add_argument("--practice",action='store_true',dest="practice",required=False)
parser.add_argument("--points",dest="target_points",required=False)
parser.add_argument("--class",dest="classid",required=False)
parser.add_argument("--package",dest="package",help="Index or Name of the package to work on",required=False)
parser.add_argument("--do-package",action='store_true',dest="do_package",help="Start doing the specified package",required=False)
parser.add_argument("--learn-all",action="store_true",dest="learnall",required=False)
parser.add_argument("--get-classes","--classes",action="store_true",dest="getclasses",required=False)
parser.add_argument("--get-packages","--packages",action="store_true",dest="getpackages",required=False)
parser.add_argument("--get-leaderboard","--leaderboard",action="store_true",dest="leaderboard")
parser.add_argument("--auto",action="store_true",dest="auto",required=False)
parser.add_argument("--leaderboard-pos","--pos",action="store_true",dest="pos",required=False)
parser.add_argument("--learn", action="store_true",dest="learn",required=False)
parser.add_argument("--do-full-package", action="store_true", dest="do_full_package", required=False)
parser.add_argument("--hide", action="store_true", dest="hide", required=False)
parser.add_argument("--account", type=str, dest="account", required=False, help="Saved account name or index to use")
args = parser.parse_args()


import os
import json

def load_credentials():
    if os.path.exists("credentials.json"):
        with open("credentials.json", "r") as f:
            return json.load(f)
    return {}

def save_credentials(username, password):
    creds = load_credentials()
    creds[username] = password
    with open("credentials.json", "w") as f:
        json.dump(creds, f)

creds = load_credentials()
if args.account:
    if creds and args.account.isdigit() and int(args.account) < len(creds):
        username = list(creds.keys())[int(args.account)]
        password = creds[username]
    elif creds and args.account in creds:
        username = args.account
        password = creds[username]
    else:
        username = args.account
        password = getpass.getpass()
        save_credentials(username, password)
else:
    if creds:
        logger.info("[#] Saved users:")
        for i, u in enumerate(creds.keys()):
            logger.info(f"{i}: {u}")
        choice = input("Choose user index or press enter for new: ")
        if choice.isdigit() and int(choice) < len(creds):
            username = list(creds.keys())[int(choice)]
            password = creds[username]
        else:
            username = input("Username: ")
            password = getpass.getpass()
            save_credentials(username, password)
    else:
        username = input("Username: ")
        password = getpass.getpass()
        save_credentials(username, password)

woca = wocabee(udaje=(username, password), headless=args.hide)
woca.init()

 
if args.getclasses:
    logger.info(f"{woca.info} Available classes:")
    for i, x in enumerate(woca.get_classes()):
        logger.info(f"{i} {x}")
    if not args.classid and not args.getpackages:
        woca.quit()
        exit(0)

 
if args.classid:
    woca.pick_class(args.classid, woca.get_classes())
elif not args.getclasses and not args.getpackages:
    
    logger.error(f"{woca.err} You need to specify class id (--class)")
    woca.quit()
    exit(1)

 
if args.getpackages:
    logger.info(f"{woca.info} Packages for current class:")
    packages = woca.get_packages(woca.GETPACKAGE)
    if not packages:
        logger.warning(f"{woca.warn} No packages found in this class.")
    for i, pkg in enumerate(packages):
        status = "READY" if pkg["playable"] else "DONE/LOCKED"
        logger.info(f"{i}: {pkg['name']:<40} [{status}]")
    if not any([args.practice, args.do_package, args.learnall, args.leaderboard, args.auto, args.pos, args.learn]):
        woca.quit()
        exit(0)

 
if args.practice:
    if not args.target_points:
        args.target_points = input("points:")
    
    if woca.pick_package(args.package, woca.get_packages(woca.PRACTICE)):
        bodiky(args.target_points)
        exit(0)
    else:
        logger.error(f"{woca.err} Failed to start practice.")
        woca.quit()
        exit(1)
 
if args.do_package:
    if not args.package:
        logger.error(f"{woca.err} You need to specify package (--package).")
        woca.quit()
        exit(1)
    
    if woca.pick_package(args.package, woca.get_packages(woca.DOPACKAGE)):
        while True:
            try:
                woca.do_package()
            except Exception as e:
                logger.error("[-] Exception in do_package")
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
            woca.quit()
            exit(0)
    else:
        logger.error(f"{woca.err} Failed to start package execution.")
    woca.quit()
    exit(0)
if args.do_full_package:
    woca.do_full_package()
    woca.quit()
    exit(0)
if args.learnall:
    woca.learnALL()
    woca.quit()
    exit(0)
if args.leaderboard:
    leaderboard()

if args.auto:
    vsetky_baliky()
    woca.quit()
    exit(0)

if args.pos:
    miesto(int(args.pos))
    woca.quit()
if args.learn:
    if not args.package:
        logger.error(f"{woca.err} You need to specify package (--package).")
        woca.quit()
        exit(1)
    if woca.pick_package(args.package, woca.get_packages(woca.LEARN)):
        woca.learn()
        woca.quit()
        exit(0)
    else:
        logger.error(f"{woca.err} Failed to start learning.")
        woca.quit()
        exit(1)
