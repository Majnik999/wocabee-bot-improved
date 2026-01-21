import os
import json
import time
import logging
import random
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common import actions
import time, json, os, datetime,threading
from selenium.webdriver.common.by import By
from selenium import webdriver
import traceback
from concurrent.futures import ThreadPoolExecutor
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

class wocabee:
    def __init__(self,udaje: tuple, headless=False):
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.url = "https://wocabee.app/app"
        self.dict_path = "./dict.json"
        if not os.path.exists(self.dict_path):
            with open(self.dict_path,"w") as f:
                f.write("{}")
        self.word_dictionary = {}
        self.ok = "[+]"
        self.warn = "[!]"
        self.err = "[-]"
        self.info = "[#]"
        self.debug = "[D]"
        self.package = None
        self.logger = logging.getLogger("wocabee")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = ColorFormatter("[%(levelname)s] %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        self.speed_login = 0.5
        self.speed_package = 0.2
        self.speed_learn = 0.33
        
        self.PRACTICE = 0
        self.DOPACKAGE = 1
        self.LEARN = 2
        self.LEARNALL = 3
        self.GETPACKAGE = 4
        self.udaje = udaje
        self.username = udaje[0]
        self.cookies_path = f"cookies_{self.username}.json"
        
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1280,800")
        
        
        try:
            
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            self.logger.error(f"{self.err} Failed to initialize Chrome: {e}")
            self.logger.info(f"{self.info} Attempting to initialize Edge...")
            try:
                from selenium.webdriver.edge.service import Service as EdgeService
                from webdriver_manager.microsoft import EdgeChromiumDriverManager
                from selenium.webdriver.edge.options import Options as EdgeOptions
                edge_options = EdgeOptions()
                if headless:
                    edge_options.add_argument("--headless=new")
                    edge_options.add_argument("--disable-gpu")
                service = EdgeService(EdgeChromiumDriverManager().install())
                self.driver = webdriver.Edge(service=service, options=edge_options)
            except Exception as e2:
                self.logger.error(f"{self.err} Failed to initialize Edge: {e2}")
                raise Exception("No suitable browser found (Chrome or Edge).")
    
        self.driver.get(self.url)
    def init(self):
        self.word_dictionary = self._dictionary_Load()
        self.class_names = []
        username,password = self.udaje
        
        
        if os.path.exists(self.cookies_path):
            self.logger.info(f"{self.info} Loading cookies for {username}...")
            try:
                with open(self.cookies_path, "r") as f:
                    cookies = json.load(f)
                    for cookie in cookies:
                        self.driver.add_cookie(cookie)
                self.driver.refresh()
                self.fast_sleep(2, "login")
            except Exception as e:
                self.logger.error(f"{self.err} Failed to load cookies: {e}")

        if not self.is_loggedIn():
            self.logger.info(f"{self.ok} Logging in... {username}")
            
            attempts = 0
            logged_in = False
            while not logged_in and attempts < 5:
                try:
                    self.login(username,password)
                except:
                    pass
            
                if self.is_loggedIn():
                    logged_in = True
                    
                    self._save_cookies()
                else:
                    attempts+=1
        else:
            self.logger.info(f"{self.ok} Successfully logged in via cookies!")

        if not self.is_loggedIn():
            self.logger.error("[-] Login failed")
            self.driver.quit()
        self.name = self.get_elements_text(By.TAG_NAME,"b")[0]
        for id,Class in enumerate(self.get_classes()):
            self.class_names.append(Class[id].find_element(By.TAG_NAME,"span").text)
        self.logger.info(f"[#] finished init {self.class_names}")
        self.fast_sleep(2, "login")

    def _save_cookies(self):
        self.logger.info(f"{self.info} Saving cookies for {self.username}...")
        try:
            cookies = self.driver.get_cookies()
            with open(self.cookies_path, "w") as f:
                json.dump(cookies, f)
        except Exception as e:
            self.logger.error(f"{self.err} Failed to save cookies: {e}")

    def quit(self):
        try:
            self.executor.shutdown(wait=False)
            self.driver.quit()
        except:
            pass
    def elem_type(self,by,elem,x):
        
        elem = self.get_element(by,elem)
        
        elem.clear()
        elem.send_keys(x)
    
    def login(self,username,password):
        self.elem_type(By.ID,"login",username)
        self.elem_type(By.ID,"password",password)
        self.fast_sleep(0.5, "login")
        btn = self.get_element(By.ID,"submitBtn")
        btn.click()
    def is_loggedIn(self):
        try:
            return self.wait_for_element(2,By.ID,"logoutBtn")
        except:
            return False    
    
    def exists_element(self, root, by, element, timeout=0):
        try:
            if timeout > 0:
                WebDriverWait(self.driver, timeout).until(lambda x: root.find_element(by, element).is_displayed())
            return root.find_element(by, element).is_displayed()
        except:
            return False
    def get_element(self,by, element):
        if self.exists_element(self.driver,by,element):
            return self.driver.find_element(by,element)
        else:
            return None
    def get_elements(self,by,element):
        if self.exists_element(self.driver,by,element):
            return self.driver.find_elements(by,element)
        else:
            return None
    def get_element_text(self,by, element):
        if self.exists_element(self.driver,by,element):
            return self.get_element(by,element).text
        else:
            return ""
    def get_elements_text(self,by,element):
        if self.exists_element(self.driver,by,element):
            return [x.text for x in self.get_elements(by,element)]
        else:
            return [0]
    def wait_for_element(self,timeout,by,element):
        WebDriverWait(self.driver,timeout).until(lambda x: self.driver.find_element(by,element).is_displayed())
        return self.get_element(by,element)
    def wait_for_element_in_element(self,timeout,elem,by,element):
        WebDriverWait(self.driver,timeout).until(lambda x: elem.find_element(by,element).is_displayed())
        return self.get_element(by,element)
    def wait_for_elements_in_element(self,timeout,elem,by,element):
        WebDriverWait(self.driver,timeout).until(lambda x: elem.find_element(by,element).is_displayed())
        return self.get_elements(by,element)

    def fast_sleep(self, seconds, domain="package"):
        factor = 1.0
        if domain == "login":
            factor = self.speed_login
        elif domain == "learn":
            factor = self.speed_learn
        else:
            factor = self.speed_package
        time.sleep(max(0, seconds * factor))

    def click_twice(self, element, domain="package"):
        try:
            element.click()
            self.fast_sleep(0.1, domain)
            element.click()
            return True
        except Exception:
            return False

    def safe_click(self, by, element, timeout=3):
        try:
            if timeout and timeout > 0:
                self.wait_for_element(timeout, by, element)
            el = self.get_element(by, element)
            if el:
                el.click()
                return True
            return False
        except Exception:
            return False

    def clean_exception(self, e):
        t = str(e)
        lines = t.splitlines()
        keep = []
        for ln in lines:
            s = ln.strip()
            if s.startswith("0x"):
                continue
            if "Dumping unresolved backtrace" in s:
                continue
            keep.append(ln)
        return "\n".join(keep)

    def click_skip(self):
        skip_ids = [
            "transcribeSkipBtn",
            "skipBtn",
            "skipButton",
            "skip",
            "skipExerciseBtn",
            "pexesoSkipBtn",
            "pexesoSkipButton"
        ]
        for sid in skip_ids:
            if self.exists_element(self.driver, By.ID, sid, timeout=0.2):
                if self.safe_click(By.ID, sid, timeout=2):
                    return True
        try:
            nodes = self.driver.find_elements(By.XPATH, "//*[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'skip')]")
            for n in nodes:
                try:
                    if n.is_displayed():
                        n.click()
                        return True
                except Exception:
                    continue
        except Exception:
            pass
        return False

    def open_link(self, el):
        try:
            href = el.get_attribute("href")
            if href:
                self.driver.get(href)
                return True
            el.click()
            return True
        except Exception:
            try:
                el.click()
                return True
            except Exception:
                return False

    def start_practice(self):
        try:
            self.fast_sleep(0.5, "package")
            self.enable_two_x_points()
        except Exception:
            pass
        ids = [
            "practiceStartBtn",
            "startPracticeBtn",
            "startPractice",
            "startGameBtn",
            "startBtn",
            "packageStartBtn"
        ]
        for i in ids:
            if self.exists_element(self.driver, By.ID, i, timeout=0.5):
                if self.safe_click(By.ID, i, timeout=3):
                    self.fast_sleep(1, "package")
                    try:
                        self.ensure_two_x_points_on_test_page()
                    except Exception:
                        pass
                    return True
        try:
            btns = self.driver.find_elements(By.XPATH, "//a[contains(@class,'btn') and (contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'start') or contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'practice'))]")
            if btns:
                btns[0].click()
                self.fast_sleep(1, "package")
                try:
                    self.ensure_two_x_points_on_test_page()
                except Exception:
                    pass
                return True
        except Exception:
            pass
        return False

    def ensure_two_x_points_on_test_page(self):
        try:
            if self.exists_element(self.driver, By.ID, "toggleWrapper", timeout=0.5) or self.exists_element(self.driver, By.ID, "levelToggle", timeout=0.5):
                txt = "" 
                try:
                    wp = self.driver.find_element(By.ID, "WP")
                    txt = wp.text
                except Exception:
                    try:
                        lvl2 = self.driver.find_element(By.ID, "level2")
                        txt = lvl2.text
                    except Exception:
                        txt = ""
                if "2 WocaPoints" in txt:
                    return True
                try:
                    lt = self.driver.find_element(By.ID, "levelToggle")
                    if lt and lt.is_displayed():
                        if lt.is_enabled() and not lt.is_selected():
                            lt.click()
                            self.fast_sleep(0.3, "package")
                        elif not lt.is_enabled():
                            try:
                                slider = self.driver.find_element(By.CSS_SELECTOR, "#toggleWrapper label.switch .slider")
                                slider.click()
                                self.fast_sleep(0.3, "package")
                            except Exception:
                                pass
                except Exception:
                    pass
                try:
                    label_sw = self.driver.find_element(By.CSS_SELECTOR, "#toggleWrapper label.switch")
                    if label_sw:
                        label_sw.click()
                        self.fast_sleep(0.3, "package")
                except Exception:
                    pass
                try:
                    wp2 = self.driver.find_element(By.ID, "WP")
                    if "2 WocaPoints" in wp2.text:
                        return True
                except Exception:
                    pass
        except Exception:
            pass
        return False

    def enable_two_x_points(self):
        try:
            on_icons = self.driver.find_elements(By.CSS_SELECTOR, "i.fa-toggle-on")
            for ic in on_icons:
                try:
                    if ic.is_displayed():
                        return True
                except Exception:
                    continue

            ids = [
                "twoXPointsSwitch","twoXToggle","doublePointsSwitch","doublePoints",
                "x2Toggle","x2Switch","practice2xSwitch","practice2xToggle"
            ]
            for i in ids:
                if self.exists_element(self.driver, By.ID, i, timeout=0.2):
                    el = self.get_element(By.ID, i)
                    try:
                        if el.tag_name.lower() == "input":
                            if not el.is_selected():
                                el.click()
                                self.fast_sleep(0.3, "package")
                                return True
                        else:
                            el.click()
                            self.fast_sleep(0.3, "package")
                            return True
                    except Exception:
                        pass

            off_icons = self.driver.find_elements(By.CSS_SELECTOR, "i.fa-toggle-off")
            for icon in off_icons:
                try:
                    if icon.is_displayed():
                        icon.click()
                        self.fast_sleep(0.3, "package")
                        return True
                except Exception:
                    continue

            inputs = self.driver.find_elements(By.XPATH, "//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'2x')]//input[@type='checkbox' or @type='radio']")
            for inp in inputs:
                try:
                    if not inp.is_selected():
                        try:
                            inp.click()
                            self.fast_sleep(0.3, "package")
                            return True
                        except Exception:
                            iid = inp.get_attribute("id")
                            if iid:
                                labels = self.driver.find_elements(By.XPATH, f"//label[@for='{iid}']")
                                if labels:
                                    labels[0].click()
                                    self.fast_sleep(0.3, "package")
                                    return True
                except Exception:
                    continue

            switches = self.driver.find_elements(By.XPATH, "//*[@role='switch' or contains(@class,'switch') or contains(@class,'toggle') or contains(@class,'custom-switch')]")
            for sw in switches:
                try:
                    sw.click()
                    self.fast_sleep(0.3, "package")
                    return True
                except Exception:
                    continue
        except Exception:
            pass
        return False

    def _int_from_text(self, text):
        s = ''.join(ch for ch in str(text) if ch.isdigit())
        return int(s) if s else 0

    def get_wocapoints_value(self):
        try:
            # primary: strict element id
            if self.exists_element(self.driver, By.ID, "WocaPoints", timeout=0.5):
                v = self._int_from_text(self.get_element_text(By.ID, "WocaPoints"))
                return v
            # secondary: visible label "You have earned <n> WocaPoints today"
            try:
                n = self.driver.find_element(By.XPATH, "//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'you have earned') and contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'wocapoints')]")
                if n and n.is_displayed():
                    v2 = self._int_from_text(n.text)
                    return v2
            except Exception:
                pass
            # tertiary: any visible node with class containing WocaPoints
            try:
                nodes = self.driver.find_elements(By.XPATH, "//*[@id='WocaPoints' or contains(@class,'WocaPoints') or contains(@class,'wocapoints')]")
                for n in nodes:
                    try:
                        if n.is_displayed():
                            v3 = self._int_from_text(n.text)
                            return v3
                    except Exception:
                        continue
            except Exception:
                pass
            return 0
        except Exception:
            return 0

    def wait_for_points_at_least(self, value, timeout=7):
        start = time.time()
        last = 0
        while time.time() - start < timeout:
            p = self.get_wocapoints_value()
            if p >= value:
                self.fast_sleep(0.5, "package")
                p2 = self.get_wocapoints_value()
                if p2 >= value:
                    return p2
            last = p
            self.fast_sleep(0.5, "package")
        return last

    def save_and_exit(self):
        try:
            for _ in range(8):
                if self.exists_element(self.driver, By.ID, "continueBtn", timeout=0.5):
                    self.safe_click(By.ID, "continueBtn", timeout=2)
                    self.fast_sleep(0.5, "package")
                if self.exists_element(self.driver, By.ID, "leaveBtn", timeout=0.5):
                    self.safe_click(By.ID, "leaveBtn", timeout=3)
                    self.fast_sleep(5, "package")
                    return True
                if self.exists_element(self.driver, By.ID, "backBtn", timeout=1):
                    txt = self.get_element_text(By.ID, "backBtn")
                    if txt in ["Uložiť a odísť", "Save and exit", "Save and leave"]:
                        self.safe_click(By.ID, "backBtn", timeout=3)
                        self.fast_sleep(5, "package")
                        if self.exists_element(self.driver, By.ID, "leaveBtn", timeout=1):
                            self.safe_click(By.ID, "leaveBtn", timeout=3)
                            self.fast_sleep(5, "package")
                        return True
                    if txt in ["Späť", "Back"]:
                        self.safe_click(By.ID, "backBtn", timeout=2)
                        self.fast_sleep(0.5, "package")
                    if not txt:
                        self.safe_click(By.ID, "backBtn", timeout=2)
                        self.fast_sleep(0.5, "package")
                else:
                    break
        except Exception:
            return False
        return False

    def get_progress_percent(self):
        try:
            el = self.get_element(By.CSS_SELECTOR, ".progress-bar")
            if el:
                style = el.get_attribute("style") or ""
                import re
                m = re.search(r"width:\s*(\d+)%", style)
                if m:
                    return int(m.group(1))
                txt = el.text.strip()
                if "%" in txt:
                    return int(''.join(ch for ch in txt if ch.isdigit()))
            for cid in ["exerciseProgressBar", "progressBar"]:
                el2 = self.get_element(By.ID, cid)
                if el2:
                    txt = el2.text.strip()
                    if "%" in txt:
                        return int(''.join(ch for ch in txt if ch.isdigit()))
            nodes = self.driver.find_elements(By.XPATH, "//*[contains(text(), '%')]")
            for n in nodes:
                t = n.text.strip()
                if "%" in t:
                    return int(''.join(ch for ch in t if ch.isdigit()))
        except Exception:
            return None
        return None

    def log_status(self, exercise_type=""):
        percent = self.get_progress_percent()
        question = ""
        ids = [
            "q_word",
            "tfw_word",
            "ch_word",
            "completeWordQuestion",
            "a_sentence",
            "q_sentence",
            "oneOutOfManyQuestionWord",
            "choosePictureWord",
            "introWord"
        ]
        for i in ids:
            q = self.get_element_text(By.ID, i)
            if q:
                question = q.strip()
                break
        if not question:
            try:
                nodes = self.driver.find_elements(By.XPATH, "//*[contains(@class,'question')]")
                if nodes:
                    question = nodes[0].text.strip()
            except Exception:
                pass
        if percent is not None:
            self.logger.info(f"[#] {percent}% {exercise_type} {question}")
        else:
            self.logger.info(f"[#] {exercise_type} {question}")
    
    def get_classes(self) -> list:
        classesList = []
        classes = self.wait_for_element(5,By.ID,"listOfClasses")
        classesList = [{i:button} for i,button in enumerate(classes.find_elements(By.CLASS_NAME,"btn-wocagrey"))]
        return classesList
    def pick_class(self, class_id, classes):
        self.logger.info(f"{self.info} PICKING {class_id}")
        try:
            
            try:
                idx = int(class_id)
                classes[idx][idx].click()
                self.wocaclass = idx
            except ValueError:
                
                found = False
                for i, class_dict in enumerate(classes):
                    
                    button = class_dict[i]
                    class_name = button.find_element(By.TAG_NAME, "span").text
                    if class_name == class_id:
                        button.click()
                        self.wocaclass = i
                        found = True
                        break
                if not found:
                    self.logger.error(f"{self.err} Class '{class_id}' not found in {self.class_names}")
        except Exception as e:
            self.logger.error(f"{self.err} Error picking class {class_id}: {self.clean_exception(e)}")
        self.fast_sleep(2, "package")

    
    def get_leaderboard(self):
        table_body = self.get_element(By.ID,"tbody")
        students = table_body.find_elements(By.CLASS_NAME,"wb-tr")
        leaderboard = []
        for student in students:
            place = student.find_element(By.CLASS_NAME,"place").text
            name = student.find_element(By.CLASS_NAME,"name").text
            online = "status-online" in student.find_element(By.CLASS_NAME,"status-icon").get_attribute("class")
            points = student.find_elements(By.TAG_NAME,"td")[3].text
            packages = student.find_elements(By.TAG_NAME,"td")[4] .text
            leaderboard.append({"place":place,"name":name,"points":points,"online":online,"packages":packages})
        return leaderboard
    
    def get_packages(self, prac):
        """Get list of available packages based on practice type"""
        prac = int(prac)
        packages = []
        if self.exists_element(self.driver,By.ID,"showMorePackagesBtn"):
            try:
                self.get_element(By.ID,"showMorePackagesBtn").click()
            except:
                self.logger.warning(f"{self.warn} failed to click more packages")
        elements = self.get_elements(By.CLASS_NAME, "pTableRow")
        if not elements:
            return packages

        if prac == self.GETPACKAGE:
            def process_package(elem):
                try:
                    name = elem.find_element(By.CLASS_NAME, "package-name").text
                    playable = self.exists_element(elem, By.CLASS_NAME, "fa-play-circle")
                    return {"name": name, "playable": playable}
                except:
                    return None
                    
            futures = [self.executor.submit(process_package, elem) for elem in elements]
            packages = [f.result() for f in futures if f.result()]

        elif prac == self.PRACTICE:
            for elem in elements:
                try:
                    name = elem.find_element(By.CLASS_NAME, "package-name").text
                except Exception:
                    name = ""
                button = None
                try:
                    button = elem.find_element(By.CSS_SELECTOR, "a[href*='mode=practice']")
                except Exception:
                    pass
                if not button:
                    try:
                        button = elem.find_element(By.XPATH, ".//a[.//i[contains(@class,'fa-gamepad')]]")
                    except Exception:
                        pass
                if not button and self.exists_element(elem, By.CLASS_NAME, "fa-gamepad"):
                    try:
                        button = elem.find_element(By.XPATH, ".//a[.//span[starts-with(@id,'btnRun')]]")
                    except Exception:
                        button = None
                if button:
                    packages.append({len(packages): button, "name": name})

        elif prac == self.DOPACKAGE:
            for elem in elements:
                if self.exists_element(elem, By.CLASS_NAME, "fa-play-circle"):
                    try:
                        name = elem.find_element(By.CLASS_NAME, "package-name").text
                        button = elem.find_element(By.CLASS_NAME, "package").find_element(By.TAG_NAME, "a")
                        packages.append({len(packages): button, "name": name})
                    except:
                        continue

        elif prac in (self.LEARN, self.LEARNALL):
            for elem in elements:
                if self.exists_element(elem, By.TAG_NAME, "a"):
                    try:
                        name = elem.find_element(By.CLASS_NAME, "package-name").text
                        button = elem.find_element(By.TAG_NAME, "a")
                        packages.append({len(packages): button, "name": name})
                    except:
                        continue

        return packages

    
    def normalize_string(self, s):
        import unicodedata, re
        s = str(s)
        s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('utf-8')
        s = s.lower()
        s = re.sub(r"\s+", " ", s)
        return s.strip()

    def pick_package(self, package_id, packages):
        self.logger.info(f"{self.info} PICKING PACKAGE {package_id}")
        try:
            # Index selection
            try:
                idx = int(package_id)
                if 0 <= idx < len(packages):
                    btn = packages[idx].get(idx)
                    if btn and self.open_link(btn):
                        self.package = idx
                        self.fast_sleep(2, "package")
                        return True
                    else:
                        self.logger.error(f"{self.err} Index {idx} not clickable")
                        return False
            except (ValueError, KeyError, IndexError):
                pass

            # Name selection with normalization and simplified match
            import re
            search_name = self.normalize_string(package_id)
            simple_search = self.normalize_string(re.sub(r"\(.*?\)", "", package_id))
            for i, pkg_dict in enumerate(packages):
                pkg_name_val = pkg_dict.get("name")
                if not pkg_name_val:
                    try:
                        btn = pkg_dict.get(i)
                        row = btn.find_element(By.XPATH, "ancestor::tr")
                        pkg_name_val = row.find_element(By.CLASS_NAME, "package-name").text
                    except Exception:
                        pkg_name_val = None
                if not pkg_name_val:
                    continue
                pkg_name = self.normalize_string(pkg_name_val)
                pkg_simple = self.normalize_string(re.sub(r"\(.*?\)", "", pkg_name_val))
                if (
                    pkg_name == search_name or search_name in pkg_name or
                    pkg_simple == simple_search or simple_search in pkg_simple or pkg_simple in simple_search
                ):
                    self.logger.info(f"{self.ok} Found matching package: {pkg_name_val}")
                    btn = pkg_dict.get(i)
                    if btn and self.open_link(btn):
                        pass
                    else:
                        try:
                            row = btn.find_element(By.XPATH, "ancestor::tr")
                            anchor = row.find_element(By.TAG_NAME, "a")
                            if not self.open_link(anchor):
                                return False
                        except Exception:
                            return False
                    self.package = i
                    self.fast_sleep(2, "package")
                    return True

            # Not found
            available = [p.get("name", "Unknown") for p in packages]
            self.logger.error(f"{self.err} Package '{package_id}' not found or not playable.")
            self.logger.info(f"{self.info} Available packages: {available}")
            return False
        
        except Exception as e:
            self.logger.error(f"{self.err} Error picking package {package_id}: {self.clean_exception(e)}")
            return False

    def get_points(self,target_wocapoints = None):
        save = True
        if not self.exists_element(self.driver, By.ID, "WocaPoints", timeout=1):
            self.start_practice()
            if self.exists_element(self.driver, By.ID, "transcribeSkipBtn", timeout=0.5):
                self.safe_click(By.ID, "transcribeSkipBtn", timeout=2)
        try:
            self.ensure_two_x_points_on_test_page()
        except Exception:
            pass
        wocapoints = self.get_wocapoints_value()
        if not target_wocapoints:
            target_wocapoints = input("target wocapoints: ")
        if str(target_wocapoints).startswith("+"):
            target_wocapoints = wocapoints + int(str(target_wocapoints).replace("+", ""))
        else:
            target_wocapoints = int(target_wocapoints)
        difference = target_wocapoints - wocapoints
        self.logger.info(f"{self.info} Doing {difference} wocapoints ({wocapoints} -> {target_wocapoints})")
        stale = 0
        last_points = wocapoints
        while True:
            current = self.get_wocapoints_value()
            if current >= target_wocapoints:
                break
            try:
                self.ensure_two_x_points_on_test_page()
            except Exception:
                pass
            self.do_exercise()
            updated = self.wait_for_points_at_least(current + 1, timeout=6)
            if updated <= current:
                stale += 1
                if stale > 10:
                    if self.exists_element(self.driver, By.ID, "continueBtn", timeout=0.5):
                        self.safe_click(By.ID, "continueBtn", timeout=2)
                    stale = 0
            else:
                last_points = updated
                stale = 0
        if save:
            if not self.save_and_exit():
                if self.exists_element(self.driver, By.ID, "backBtn", timeout=1):
                    self.safe_click(By.ID, "backBtn", timeout=2)
            self.fast_sleep(5, "package")
    def learn(self, echo=False):
        self.logger.info(f"{self.ok} Starting learning process...")
        
        
        if self.exists_element(self.driver, By.ID, "introRun"):
            self.logger.info(f"{self.info} Clicking 'Start Learning' button...")
            self.safe_click(By.ID, "introRun", timeout=5)
            self.fast_sleep(2, "learn")

        
        if self.exists_element(self.driver, By.ID, "intro") or self.exists_element(self.driver, By.ID, "introNext"):
            self.logger.info(f"{self.ok} Learning words in Intro...")
            
            
            while True:
                try:
                    
                    word_elem = None
                    trans_elem = None
                    
                    
                    for w_id in ["word", "introWord"]:
                        if self.exists_element(self.driver, By.ID, w_id):
                            word_elem = self.get_element(By.ID, w_id)
                            break
                    for t_id in ["translation", "introTranslation"]:
                        if self.exists_element(self.driver, By.ID, t_id):
                            trans_elem = self.get_element(By.ID, t_id)
                            break
                            
                    if word_elem and trans_elem:
                        word = word_elem.text.strip()
                        translation = trans_elem.text.strip()
                        if word and translation:
                            self.dictionary_put(word, translation)
                            
                    
                    if self.exists_element(self.driver, By.ID, "pictureThumbnail"):
                        picture = self.get_element(By.ID, "pictureThumbnail")
                        path = picture.get_attribute("src")
                        if path and translation:
                            self.dictionary_put(os.path.basename(path)[:-4], translation, Picture=True)

                    
                    next_btn = None
                    for n_id in ["introNext", "rightArrow"]:
                        if self.exists_element(self.driver, By.ID, n_id):
                            next_btn = self.get_element(By.ID, n_id)
                            break
                    
                    if next_btn:
                        self.safe_click(By.ID, next_btn.get_attribute("id") or "introNext", timeout=5)
                        self.fast_sleep(0.8, "learn")
                    else:
                        
                        break
                except Exception as e:
                    self.logger.error(f"{self.err} Error during intro: {self.clean_exception(e)}")
                    break
        
        
        elif self.exists_element(self.driver, By.CLASS_NAME, "pTableRow"):
            self.logger.info(f"{self.ok} Scraping word list from table...")
            rows = self.get_elements(By.CLASS_NAME, "pTableRow")
            for row in rows:
                try:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 2:
                        word = cols[0].text.strip()
                        translation = cols[1].text.strip()
                        if word and translation:
                            self.dictionary_put(word, translation)
                except:
                    continue
        
        
        self.fast_sleep(1, "learn")
        if self.exists_element(self.driver, By.ID, "backBtn"):
            btn_text = self.get_element_text(By.ID, "backBtn")
            self.logger.info(f"{self.info} Clicking back button ({btn_text})...")
            self.safe_click(By.ID, "backBtn", timeout=5)
        
        self.logger.info(f"{self.ok} Learning finished.")
    def learnALL(self):
        self.logger.info(f"{self.info} Starting Learn-All for all packages...")
        
        packagelist = self.get_packages(self.LEARNALL)
        if not packagelist:
            self.logger.warning(f"{self.warn} No packages found to learn.")
            return

        total = len(packagelist)
        for i in range(total):
            
            current_packages = self.get_packages(self.LEARNALL)
            if i >= len(current_packages):
                break
            
            pkg = current_packages[i]
            
            button = pkg.get(i)
            if not button:
                
                for k, v in pkg.items():
                    if isinstance(k, int):
                        button = v
                        break
            
            if button:
                try:
                    pkg_name = pkg.get("name", f"Package {i}")
                    self.logger.info(f"{self.info} [{i+1}/{total}] Learning: {pkg_name}")
                    self.package = pkg_name
                    button.click()
                    self.fast_sleep(2, "learn")
                    self.learn()
                    
                    if not self.exists_element(self.driver, By.CLASS_NAME, "pTableRow", timeout=5):
                        self.driver.back()
                        self.fast_sleep(2, "learn")
                except Exception as e:
                    self.logger.error(f"{self.err} Error learning package {i}: {e}")
                    self.driver.get("https://wocabee.app/app/?lang=SK")
                    self.fast_sleep(3, "learn")
                    
        
        self.logger.info(f"{self.ok} Learn-All process completed.")

    def find_missing_letters(self,missing,word):
        missing = str(missing)
        word = str(word)
        if not missing or not word:
            
            return ""
        end = ""
        index = 0
        for _ in range(missing.count("_")+1):
            x = missing.find("_",index)
            if x != -1:
                end+=word[x]
                index = x+1

        return end

    def do_exercise(self):
        
        exercise_map = {
            "addMissingWord": self._complete_veta,
            "choosePicture": self._choose_picture,
            "pexeso": self._pexeso,
            "describePicture": self._describe,
            "translateWord": self._handle_translate,
            "tfw_word": self._handle_tfw,
            "chooseWord": self._ch_word,
            "completeWord": self._complete_word,
            "oneOutOfMany": self._outofmany,
            "findPair": self._pariky,
            "sortableWords": self._arrange_words,
            "incorrect-next-button": self._handle_error
        }

        if self.click_skip():
            return

        for element_id, handler in exercise_map.items():
            if self.exists_element(self.driver, By.ID, element_id, timeout=0.1):
                try:
                    
                    if self.exists_element(self.driver, By.ID, element_id, timeout=0.1):
                        self.log_status(element_id)
                        handler()
                        return # Exit after handling one exercise
                except Exception as e:
                    self.logger.error(f"{self.err} Error in {handler.__name__}: {self.clean_exception(e)}")
                    
        
        if self.click_skip():
            return
        elif self.exists_element(self.driver, By.CLASS_NAME, "picture", timeout=0.1):
            self.log_status("picture")
            self._idk()
        elif self.exists_element(self.driver, By.ID, "transcribeSkipBtn", timeout=0.1):
            self.get_element(By.ID, "transcribeSkipBtn").click()
        elif self.exists_element(self.driver, By.ID, "introNext", timeout=0.1):
            
            self.get_element(By.ID, "introNext").click()


    def _handle_translate(self):
        word = self.wait_for_element(5, By.ID, "q_word").text
        self.log_status("translateWord")
        translations = self.dictionary_get(word)
        translated = translations[0] if translations else "idk"
        self.elem_type(By.ID, "translateWordAnswer", translated)
        self.get_element(By.ID, "translateWordSubmitBtn").click()

    def _handle_tfw(self):
        word = self.get_element_text(By.ID, "tfw_word")
        self.log_status("tfw_word")
        translations = self.dictionary_get(word)
        translated = translations[0] if translations else "idk"
        self.elem_type(By.ID, "translateFallingWordAnswer", translated)
        self.get_element(By.ID, "translateFallingWordSubmitBtn").click()

    def _handle_error(self):
        word = self.get_element_text(By.CLASS_NAME, "correctWordQuestion")
        translation = self.get_element_text(By.CLASS_NAME, "correctWordAnswer")
        self.dictionary_put(word, translation)
        self.get_element(By.ID, "incorrect-next-button").click()

    def _pexeso(self):
        self.logger.info(f"{self.ok} Handling Pexeso...")
        try:
            self.log_status("pexeso")
            start = time.time()
            while time.time() - start < 12:
                if self.click_skip():
                    return
                pa_cards = self.get_elements(By.CSS_SELECTOR, "#pa_words .pexesoCardWrapper") or []
                pq_cards = self.get_elements(By.CSS_SELECTOR, "#pq_words .pexesoCardWrapper") or []
                all_cards = self.get_elements(By.CSS_SELECTOR, ".pexesoCardWrapper") or []
                if len(all_cards) >= 2:
                    card1 = random.choice(all_cards)
                    card2 = random.choice(all_cards)
                    self.click_twice(card1)
                    self.click_twice(card2)
                elif pa_cards and pq_cards:
                    card1 = random.choice(pa_cards)
                    card2 = random.choice(pq_cards)
                    self.click_twice(card1)
                    self.click_twice(card2)
                else:
                    if self.click_skip():
                        return
                self.fast_sleep(0.25, "package")
                if self.exists_element(self.driver, By.ID, "incorrect-next-button", timeout=0.3):
                    if self.safe_click(By.ID, "incorrect-next-button", timeout=2):
                        return
                if self.exists_element(self.driver, By.ID, "continueBtn", timeout=0.3):
                    if self.safe_click(By.ID, "continueBtn", timeout=2):
                        return
            self.click_skip()
        except Exception as e:
            self.logger.error(f"{self.err} Pexeso failed: {self.clean_exception(e)}")
    def _choose_picture(self):
        start_time = time.time()
        while time.time() - start_time < 30:
            self.fast_sleep(0.5, "package")
            try:
                word_translation = self.get_element_text(By.ID, "choosePictureWord")
                self.log_status("choosePicture")
                picture_elem = self.get_element(By.CSS_SELECTOR, ".slick-current img")
                if not picture_elem:
                    imgs = self.get_elements(By.CSS_SELECTOR, ".slick-slide img") or []
                    if imgs:
                        self.click_twice(imgs[0])
                        self.fast_sleep(0.2, "package")
                        if self.exists_element(self.driver, By.ID, "incorrect-next-button", timeout=0.3):
                            self.safe_click(By.ID, "incorrect-next-button", timeout=2)
                            return
                        if self.exists_element(self.driver, By.ID, "continueBtn", timeout=0.3):
                            self.safe_click(By.ID, "continueBtn", timeout=2)
                            return
                    continue
                
                word_attr = picture_elem.get_attribute("word")
                
                
                translations = self.dictionary_get(word_attr, Picture=True)
                
                if word_attr == word_translation or word_translation in translations:
                    self.logger.info(f"{self.ok} Clicking picture: {word_attr}")
                    picture_elem.click()
                    self.fast_sleep(0.5, "package")
                    
                    if self.exists_element(self.driver, By.ID, "choosePicture", timeout=0.5):
                        picture_elem.click()
                    return # Successfully handled
                else:
                    imgs = self.get_elements(By.CSS_SELECTOR, ".slick-slide img") or []
                    if imgs:
                        self.click_twice(imgs[0])
                        self.fast_sleep(0.2, "package")
                        if self.exists_element(self.driver, By.ID, "incorrect-next-button", timeout=0.3):
                            self.safe_click(By.ID, "incorrect-next-button", timeout=2)
                            return
                        if self.exists_element(self.driver, By.ID, "continueBtn", timeout=0.3):
                            self.safe_click(By.ID, "continueBtn", timeout=2)
                            return
                    else:
                        btn = self.get_element(By.CLASS_NAME, "slick-next")
                        if btn:
                            btn.click()
            except:
                continue

        
    def _describe(self):
        
        image = self.get_element(By.ID,"describePictureImg")
        path = image.get_attribute("src")
        
        filename = path.split("pictures/")[1][:-4]
        description = self.dictionary_get(filename,Picture=True)
        self.logger.debug(f"{self.debug} {description} {filename} {path}")
        self.elem_type(By.ID,"describePictureAnswer",description)
        self.get_element(By.ID,"describePictureSubmitBtn").click()
        
        
    def _idk(self):
        self.logger.error(f"{self.err} toto neviem ešte")
    def _main(self,translated):
        self.elem_type(By.ID,"translateWordAnswer",translated)
        self.get_element(By.ID,"translateWordSubmitBtn").click()
    def _tfw(self,translated):
        self.elem_type(By.ID,"translateFallingWordAnswer",translated)
        self.get_element(By.ID,"translateFallingWordSubmitBtn").click()
    def _ch_word(self):
        word = self.get_element_text(By.ID, "ch_word")
        self.log_status("chooseWord")
        answers = self.get_elements(By.CLASS_NAME, "chooseWordAnswer")
        translations = self.dictionary_get(word)
        for answer in answers:
            if answer.text.strip() in translations:
                answer.click()
                break
    def _complete_word(self):
        word = self.get_element_text(By.ID,"completeWordQuestion")
        self.log_status("completeWord")
        miss = self.get_element_text(By.ID,"completeWordAnswer")
        preklady = self.dictionary_get(word)
        preklad = ""
        if preklady:
            for x in preklady:
                if len(miss) == len(x):
                    preklad = x
                    break
        if not preklad and preklady:
            preklad = preklady[0]
        
        self.get_element(By.ID,"completeWordAnswer").send_keys("".join(self.find_missing_letters(miss,preklad)))
        try:
            self.wait_for_element(5,By.ID,"completeWordSubmitBtn").click()
        except Exception:
            self.logger.error("[-] Exception in _complete_word submit")
    def _pariky(self):
        questions = self.get_elements(By.CLASS_NAME,"fp_q") # btn-success
        questiontexts = [x.text for x in questions]

        answers = self.get_elements(By.CLASS_NAME,"fp_a") # btn-primary
        answertexts = [x.text for x in answers]
        questionanswers = [self.dictionary_get(x) for x in questiontexts]
        
        found_any = False
        for i, x in enumerate(questionanswers):
            for y in x:
                if y in answertexts:
                    for z in self.dictionary_get(y):
                        if z in questiontexts:
                            questions[questiontexts.index(z)].click()
                    answers[answertexts.index(y)].click()
                    found_any = True
                    break
        
        
        if not found_any and questions and answers:
            self.logger.warning(f"{self.warn} No known pairs! Clicking randomly to learn...")
            questions[0].click()
            answers[0].click()
    def _outofmany(self):
        word_elem = self.wait_for_element(10, By.ID, "oneOutOfManyQuestionWord")
        self.log_status("oneOutOfMany")
        translations_btns = self.get_elements(By.CLASS_NAME, "oneOutOfManyWord")
        known_translations = self.dictionary_get(word_elem.text)
        for btn in translations_btns:
            if btn.text.strip() in known_translations:
                btn.click()
                break
    def _complete_veta(self):
        a_sentence = self.get_element_text(By.ID, "a_sentence")
        q_sentence = self.get_element_text(By.ID, "q_sentence")
        self.log_status("addMissingWord")
        try:
            index = a_sentence.index("_")
            last = len(a_sentence) - a_sentence[::-1].index("_")
            translations = self.dictionary_get(q_sentence)
            for x in translations:
                if len(x) == len(a_sentence):
                    self.elem_type(By.ID, "missingWordAnswer", x[index:last])
                    self.get_element(By.ID, "addMissingWordSubmitBtn").click()
                    break
        except Exception as e:
            self.logger.error(f"{self.err} Veta failed: {e}")
        if self.exists_element(self.driver,By.ID,"addMissingWordSubmitBtn"):
            self.get_element(By.ID,"addMissingWordSubmitBtn").click()
    def _arrange_words(self):
        word = self.get_element_text(By.ID,"def-lang-sentence")
        
        translated = self.dictionary_get(word)[0]
        words = translated.split(" ")
        ponctuation = self.get_element_text(By.ID,"static-punctuation")
        end = list()
        for word in words:
            if word.endswith(ponctuation):
                end.append(word.strip(ponctuation))
            else:
                end.append(word)
        words = end
        for i,x in enumerate(words):
            sortable = self.get_elements(By.CLASS_NAME,"word-to-arrange")
            sortable_text = [x.text for x in sortable]
            if x != sortable_text[i]:
                self.logger.debug(f"{self.debug} Moving: {x} -> {sortable_text[i]}")
                ActionChains(self.driver).drag_and_drop(sortable[sortable_text.index(x)],sortable[i]).perform()
        self.get_element(By.ID,"arrangeWordsSubmitBtn").click()
    def do_package(self):
        self.logger.info(f"{self.ok} Doing Package...")
        if self.exists_element(self.driver, By.ID, "introRun"):
            self.logger.info(f"{self.ok} New package Started...")
            self.safe_click(By.ID,"introRun", timeout=5)
            self.wait_for_element(10,By.ID, "introNext")
            while self.exists_element(self.driver, By.ID, "introNext"):
                    word = self.get_element(By.ID,"introWord")
                    translation = self.get_element(By.ID,"introTranslation")
                    if word and translation:
                        self.dictionary_put(word.text,translation.text)
                    picture = self.get_element(By.ID,"pictureThumbnail")
                    if picture:
                        
                        path = picture.get_attribute("src")
                        self.logger.debug(f"{self.debug} PUT {os.path.basename(path)[:-4]} as translation")
                        self.dictionary_put(os.path.basename(path)[:-4],translation.text,Picture=True)
                    try:
                        self.wait_for_element(10,By.ID, "introNext")
                        self.safe_click(By.ID,"introNext", timeout=5)
                    except Exception as e:
                        self.logger.error(self.clean_exception(e))
                        break
        else:
            self.logger.warning(f"{self.warn} Package has been already started before, words may not be in dictionary!")
        while self.get_element_text(By.ID, "backBtn") in ["Späť", "Back"]:
            self.last = ""
            self.do_exercise()
            
            
            next_buttons = ["completeWordSubmitBtn", "incorrect-next-button", "continueBtn"]
            for btn_id in next_buttons:
                if self.exists_element(self.driver, By.ID, btn_id, timeout=0.1):
                    self.safe_click(By.ID, btn_id, timeout=3)
                    break
        else:
            
            self.logger.info(f"{self.ok} Package completed or button changed: {self.get_element_text(By.ID,'backBtn')}")
            while self.exists_element(self.driver, By.ID, "continueBtn", timeout=1):
                self.safe_click(By.ID, "continueBtn", timeout=2)
            try:
                self.safe_click(By.ID, "backBtn", timeout=5)
            except:
                pass

    def do_full_package(self):
        while True:
            playable = self.get_packages(self.DOPACKAGE)
            if not playable:
                break
            if self.pick_package(0, playable):
                try:
                    self.do_package()
                except Exception as e:
                    self.logger.error(self.clean_exception(e))
                if self.exists_element(self.driver, By.ID, "continueBtn", timeout=1):
                    self.safe_click(By.ID, "continueBtn", timeout=2)
                if self.exists_element(self.driver, By.ID, "backBtn", timeout=1):
                    btn_text = self.get_element_text(By.ID, "backBtn")
                    if btn_text in ["Uložiť a odísť", "Save and exit", "Save and leave"]:
                        self.safe_click(By.ID, "backBtn", timeout=3)
                self.leave_class()
                self.fast_sleep(1, "package")
            else:
                break

    def leave_class(self):
        self.get_element(By.CLASS_NAME,"home-breadcrumb").click()
        self.fast_sleep(0.5, "package")
    def dictionary_get(self, word, *args, **kwargs):
        word = str(word).strip()
        if not self.word_dictionary:
            self.word_dictionary = self._dictionary_Load()
        
        current_class = self.class_names[int(self.wocaclass)]
        dictionary = self.word_dictionary.get(current_class, {})
        
        if "Picture" in kwargs:
            dictionary = self.word_dictionary.get("Picture", {})
            
        end = []
        
        search_words = [w.strip() for w in word.split(",")] if "," in word else [word]
        
        for s_word in search_words:
            
            if s_word in dictionary:
                for translation in dictionary[s_word]:
                    if translation not in end:
                        end.append(translation)
            
            for key, values in dictionary.items():
                if s_word in values:
                    if key not in end:
                        end.append(key)
        
        
        if not end:
            for c_name, c_dict in self.word_dictionary.items():
                if c_name == current_class or c_name == "Picture": continue
                if s_word in c_dict:
                    for translation in c_dict[s_word]:
                        if translation not in end: end.append(translation)
        
        return end

    def dictionary_put(self, word, translation, *args, **kwargs):
        if not word or not translation:
            return
            
        self.wocaclass = int(self.wocaclass)
        word = str(word).strip()
        translation = str(translation).strip()
        
        target_key = "Picture" if "Picture" in kwargs else self.class_names[self.wocaclass]
        
        if target_key not in self.word_dictionary:
            self.word_dictionary[target_key] = {}
            
        dictionary = self.word_dictionary[target_key]
        
        if word not in dictionary:
            dictionary[word] = []
        
        if translation not in dictionary[word]:
            dictionary[word].append(translation)
            self.logger.info(f"{self.ok} Learned: {word} -> {translation}")
            self._dictionary_Save()

        
        """
        if "," in word:
            words = []
            for x in word.split(","):
                words.append(x.strip())
            words.append(word)
            value = words
            key = translation
        """
        if "," in translation:
            translations = []
            for x in translation.split(","):
                translations.append(x.strip())
            translations.append(translation)
            value = translations
            key = word
        else:
            value = [f"{translation}"]
            key = word

        if not key in dictionary:
            dictionary.update({key:value})
        else:
            for x in value:
                if not x in dictionary[key]:
                    dictionary[key].append(x)
       

        
        self.logger.debug(f"{self.debug} (PUT) {word} as {translation}")
        self._dictionary_Save()

    def _dictionary_Load(self):
        with open(self.dict_path,"r") as f:
            ext_dict = json.load(f)
        self.word_dictionary = ext_dict
        return ext_dict
    def _dictionary_Save(self):
        with open(self.dict_path,"w") as f:
            json.dump(self.word_dictionary,f,indent=2)
