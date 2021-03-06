from random import randint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import sqlite3
import threading
import configparser 
import datetime
import timeit
import os       #used for working path
import time     #used for sleep
import sys      #used for command line arg
import inspect



def print_to_log(message,print_to_console = True):
     try:
        with open("log.txt", 'a') as f:
            if(print_to_console):
                print(message)    
            print(message, file=f)
            return True
     except Exception as e:
        print("CANT WRITE IN LOG FILE")
        return False

def save_log(file_name, line_number, function_name, log_string):
    try:
        with open("log.txt", 'a') as f:
            print("#"*50, file=f)
            print(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")+":", file=f)
            print("File name: "+ str(file_name), file=f)
            print("Line number: "+ str(line_number), file=f)
            print("Function: "+ str(function_name), file=f)
            print(str(log_string), file=f)
            print("*"*30, file=f)
            return True
    except Exception as e:
        print("CANT WRITE IN LOG FILE")
        with open("LOG_FILE_ERROR.txt", 'a') as f:
            print("#"*50, file=f)
            print(datetime.now().strftime("%d/%m/%Y %H:%M:%S")+":", file=f)
            print("File name: "+ str(file_name), file=f)
            print("Line number: "+ str(line_number), file=f)
            print("Function: "+ str(function_name), file=f)
            print(str(log_string), file=f)
            print("*"*30, file=f)
            return False

class instagram_automation:
     def __init__(self): #path is hardcoded for windows
          try:
               #first set up config
               #create example config if none exist
               self.create_example_ini()

               #read config
               self.set_config_from_ini()

               #Chrome Driver Setup---------------------------------------------
               self._chrome_options = Options()

               #chrome driver hardcoded to current path
               self.chromedriver = "chromedriver.exe"

               #set the environment
               os.environ["webdriver.chrome.driver"] = self.chromedriver

               #add the profile to options
               if(not self._USE_LOGIN):
                self._chrome_options.add_argument('--profile-directory=Default')
                self._chrome_options.add_argument("user-data-dir={path}".format(path = self._GOOGLE_PROFILE_PATH))

               #create the bot driver
               try:
                self.driver = webdriver.Chrome(self.chromedriver, options = self._chrome_options)
               except:
                print_to_log("An error occured in attempt to use the WebDriver.",self._print_feedback_results)
                print_to_log("--Make sure you have set <YOUR_USER_NAME> in GOOGLE_PROFILE_PATH in CONFIG.ini.",self._print_feedback_results)
                print_to_log("--Make sure NO OTHER CHROME INSTANCES ARE RUNNNING before using the bot..",self._print_feedback_results)
                print_to_log("or TRY making sure you have the correct chromedriver.exe in the program folder.",self._print_feedback_results)
                input("Exiting Program.. Press Enter to Exit..")
                exit()

               self._t = threading.Thread(target=self.run)
               self._started = False

               self._likes = 0
               self._skips = 0
               self._skips_list = []
               self._enabled = True
               self._paused = False
               self._state = "OFF"
               self._urls_remaining_count = 0
               self._urls_in_queue = 0
               self._time_remaining = 0
               self._last_url = ''
               self._category_current = ''
               self._date = datetime.date.today()
               self._likes_today = 0
               self._paused_time = 0
               self._issue = None
               self._show_menu = False

          except Exception as e:
               print(e)
               _, file_name, line_number, function_name, _, _ = inspect.stack()[0]
               save_log(file_name, line_number, function_name, e)

          
     #config getters and setters ------------
     def get_GOOGLE_PROFILE_PATH():
        return _GOOGLE_PROFILE_PATH
     def set_GOOGLE_PROFILE_PATH(GOOGLE_PROFILE_PATH):
        self._GOOGLE_PROFILE_PATH = GOOGLE_PROFILE_PATH
     def get_LIKE_LIMIT_PER_CATGEORY():
        return self._LIKE_LIMIT_PER_CATGEORY
     def set_LIKE_LIMIT_PER_CATGEORY(LIKE_LIMIT_PER_CATGEORY):
        self._LIKE_LIMIT_PER_CATGEORY = LIKE_LIMIT_PER_CATGEORY
     def get_LIKE_DELAY_RANGE():
        return self._LIKE_DELAY_RANGE
     def set_LIKE_DELAY_RANGE(LIKE_DELAY_RANGE):
        self._LIKE_DELAY_RANGE = LIKE_DELAY_RANGE
     def get_CATEGORIES():
        return self._CATEGORIES
     def set_CATEGORIES(CATEGORIES):
        self._CATEGORIES = CATEGORIES

     #feedback getters-----------------------
     def get_state(self):
        return (self._state)

     def get_run_time(self,_format ='%H:%M:%S' ):
        stop = self._paused_time + int(-1*(self._start - timeit.default_timer()))
        formated_time = time.strftime(_format, time.gmtime(stop))
        return formated_time

     def get_sleep_time_remaining(self):
        return self._time_remaining

     def get_issue(self):
        return self._issue

     def get_last_url(self):
        return self._last_url

     def get_current_category(self):
        return self._category_current

     def get_likes_today(self):
        return self._likes

     def get_total_likes(self):
        return self._likes_today

     def get_skips(self):
        return self._skips

     def get_urls_in_queue(self):
        return self._urls_in_queue

     def get_urls_available(self):
        return self._urls_remaining_count

     #this function is abit depreciated and profile is better to work with 
     def login(self,username, password):
          try:    
             #get username textbox
             try:
                 elem = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME , 'username')))
                 elem.clear()
             except TimeoutException:
                 return 
             
             #send username to textbox
             print_to_log("Entering Username...",self._print_feedback_results)
             elem.send_keys(username)

             #get password textbox
             elem = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME , 'password')))
             elem.clear()
             
             #send password to textbox
             print_to_log("Entering Password...",self._print_feedback_results)
             elem.send_keys(password)
             
             #delay so login button can appear
             time.sleep(2)
             
             #attempt to login
             print_to_log("attempting login credentials",self._print_feedback_results)
             elem.send_keys(Keys.ENTER)
             time.sleep(2)
             try:
                 WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.XPATH,"//*[text()='Sorry, your password was incorrect. Please double-check your password.']")))
                 self._issue = "FAILED LOGIN"
                 print_to_log("Sorry, your password was incorrect. Please double-check your password.",self._print_feedback_results)
             except TimeoutException:
                 print_to_log("Login Successful",self._print_feedback_results)
          except Exception as e:
               print(e)
               _, file_name, line_number, function_name, _, _ = inspect.stack()[0]
               save_log(file_name, line_number, function_name, e)      
            
     #creates a template CONFIG.ini | user then tailors it to their needs
     def create_example_ini(self):
          try:          
               if not os.path.exists('config.ini'):
                 print_to_log("Creating config file: Results.ini",self._print_feedback_results)
                 config = configparser.ConfigParser()
                 config['LOGIN'] = {}
                 config['LOGIN']['USE_LOGIN'] = '0'
                 config['LOGIN']['USERNAME'] = 'NONE'
                 config['LOGIN']['PASSWORD'] = 'NONE'
                 config['LOGIN']['GOOGLE_PROFILE_PATH'] = "C:\\Users\\YOUR_USER_NAME\\AppData\\Local\\Google\\Chrome\\User Data" 
                 config['BOT_CONFIG'] = {}
                 config['BOT_CONFIG']['PRINT_FEED_BACK'] = '1'
                 config['BOT_CONFIG']['LIKE_LIMIT_PER_CATGEORY'] = '5'
                 config['BOT_CONFIG']['LIKE_DELAY_RANGE'] = '15 60'
                 config['BOT_CONFIG']['SCROLL_COUNT'] = '5'
                 config['BOT_CONFIG']['CATEGORIES'] = "#Fractals #FractalArt #prettyArt"
                 
                 with open('CONFIG.ini', 'w') as configfile:
                     config.write(configfile)
                 print_to_log("Created CONFIG.ini",self._print_feedback_results)
                 print_to_log("!! -- Replace <YOUR_USER_NAME> in GOOGLE_PROFILE_PATH in CONFIG.ini then rerun program",self._print_feedback_results)
                 input("Press Enter to continue...",self._print_feedback_results)
                 exit()
          except Exception as e:
               print(e)
               _, file_name, line_number, function_name, _, _ = inspect.stack()[0]
               save_log(file_name, line_number, function_name, e)

     #reads CONFIG.ini and sets proper values
     def set_config_from_ini(self):
          if os.path.exists('config.ini'):  
               #create configuration file if not exist
               #pull from the config file
               config = configparser.ConfigParser()
               config.read('CONFIG.ini')     
               self._GOOGLE_PROFILE_PATH     = config['LOGIN']['GOOGLE_PROFILE_PATH']
               self._LIKE_LIMIT_PER_CATGEORY = int(config['BOT_CONFIG']['LIKE_LIMIT_PER_CATGEORY'])
               self._LIKE_DELAY_RANGE        = list(map(int,config['BOT_CONFIG']['LIKE_DELAY_RANGE'].split()))
               self._SCROLL_COUNT            = int(config['BOT_CONFIG']['SCROLL_COUNT'])
               self._CATEGORIES              = config['BOT_CONFIG']['CATEGORIES'].split()   
               self._USER_NAME               = config['LOGIN']['USERNAME'] 
               self._PASSWORD                = config['LOGIN']['PASSWORD']
               self._USE_LOGIN               = bool(int(config['LOGIN']['USE_LOGIN']))       
               self._print_feedback_results  = bool(int(config['BOT_CONFIG']['PRINT_FEED_BACK']))
          else:
            print_to_log("error.. missing CONFIG.ini",self._print_feedback_results)

     #creates Results.txt with results of run <<----this needs to be adjusted for every run in case of error
     def create_results_file(self):
        print_to_log("Creating results file: Results.txt",self._print_feedback_results)
        t = self._paused_time + int(-1*(self._start - timeit.default_timer()))
        formated_time = time.strftime('%H:%M:%S', time.gmtime(t)) 
        date = datetime.datetime.now()
        config = configparser.ConfigParser()
        config['Results_{}'.format(date)] = {}
        config['Results_{}'.format(date)]['LIKES'] = str(self._likes)
        config['Results_{}'.format(date)]['SKIPS'] = str(self._skips_list)
        config['Results_{}'.format(date)]['CATEGORIES'] = str(self._CATEGORIES)
        config['Results_{}'.format(date)]['LIKES_TODAY'] = str(self._likes_today)
        config['Results_{}'.format(date)]['RUNTIME'] = str(formated_time)

        if(self._issue is not None):
            config['Results_{}'.format(date)]['ISSUE'] = self._issue
                                                               
        with open('Results.txt', 'a') as configfile:
            config.write(configfile)

        print_to_log("Created results file.",self._print_feedback_results)

     #custom sleep function to handle in possible range
     def sleep(self,_from,_to):
        sleep_time = randint(_from,_to)
        print_to_log('sleeping for {} seconds'.format(sleep_time),self._print_feedback_results) 
        time.sleep(sleep_time)

     #opens to instagram.com 
     def open_instagram(self):

        print_to_log('opening instagram',self._print_feedback_results)
        self.driver.get('https://www.instagram.com/')

     #clicks on search, enters search value, then 
     #presses down to select first from drop down then hits enter for search
     def search(self,search_text):
        #find search textbar
        try:
            elem = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Search"]')))
        except NoSuchElementException:
            print_to_log("Web page either failed to load correctly or You not have Instgagram Credentials saved to your Chrome profile",self._print_feedback_results)
            print_to_log("--Make sure you have set <YOUR_USER_NAME> in GOOGLE_PROFILE_PATH in CONFIG.ini.",self._print_feedback_results)
            print_to_log("Exiting Program",self._print_feedback_results)
            input("Press Enter to Exit Program...")
            exit()
        
        #send search_text to textbox
        elem.send_keys(search_text)
        print_to_log('searching for {}'.format(search_text),self._print_feedback_results)
        #sleep so drop down has a moment to populate
        time.sleep(2) #DO NOT DELETE

        #get first result
        #In dropdown list go DOWN one then press ENTER
        elem.send_keys(Keys.DOWN)
        elem.send_keys(Keys.ENTER)
        time.sleep(3) #let things load

     #scroll down to botton of document body
     def scroll(self):
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

     #querys database to see if url exist or not
     def _is_used_url(self,url):
        t = (url,) #safer then python string functions according to SquliteDoc
        self.c.execute("SELECT url FROM tblUrlsVisted WHERE url = '{}'".format(url))
        if(self.c.fetchone() is not None):
            return True
        return False

     def _check_for_block(self):
        try:
            WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.XPATH,"//*[text()='You’re Temporarily Blocked']")))
            self._issue = 'You’re Temporarily Blocked'
            return True
        except TimeoutException:
            try:
                self.driver.find_element_by_xpath("//*[text()='Action Blocked']")
                self._issue = "Action Blocked"
                return True
            except NoSuchElementException:
                return False

     #gets a list of urls from search results page
     def get_posts_urls(self):
        print_to_log('getting url list..',self._print_feedback_results)
        time.sleep(1)
        
        elems = []
        url_list = []
        temp_list = []

        if(self._SCROLL_COUNT == 0): #fix so scroll must happen once
            self._SCROLL_COUNT = 1
        #scroll down to get more results
        for x in range(0, self._SCROLL_COUNT):       
            state = self._manage_pause()
            self._print_feedback()
            if(not self._enabled):
                return
            elems = self.driver.find_elements_by_xpath("//a[@href]")
            for elem in elems:
                if(not self._enabled):
                    break
                url = elem.get_attribute("href")
                if('.com/p' in url):  
                    temp_list.append(url)             
            print_to_log("Scrolling..",self._print_feedback_results)
            self.scroll()
            time.sleep(2)

        #remove duplicates
        temp_list = list(dict.fromkeys(temp_list))

        for url in temp_list:          
            #check if url is already exist in DB
            if(self._is_used_url(url)):
                self._skips = self._skips + 1
            else:
                url_list.append(url)
                print_to_log(url,self._print_feedback_results)
                    
        self._skips_list.append(self._skips)
        
        #count add to total grabbed
        self._urls_remaining_count = len(url_list)

        if(self._LIKE_LIMIT_PER_CATGEORY <= self._urls_remaining_count):
            self._urls_in_queue = self._LIKE_LIMIT_PER_CATGEORY
        else:
            self._urls_in_queue = self._urls_remaining_count
        return url_list

     #likes all post urls in a url list and uses range of manage like speed
     def like_posts(self,post_list_urls):
        try:  
             count = 0
             if(not self._enabled):
                     return
             for post in post_list_urls:
                 if(self._issue is None):
                     self._last_url = post
                     state = self._manage_pause()
                     self._print_feedback()
                     if(not self._enabled):
                         break
                     if (count == self._LIKE_LIMIT_PER_CATGEORY):
                         print_to_log("like limit reached")
                         break
                     
                     #navigate to url in url list
                     self.driver.get(post)
                     
                     #get the like icon
                     elem = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR , 'svg')))
                     time.sleep(1) # might not need..added for rendering tests for double like
                     sql = ''' INSERT INTO tblUrlsVisted(url,date) VALUES(?,?) '''
                     
                     #check if shows "Like or Unlike" if like exist on page then go and like
                     if (elem.get_attribute("aria-label") == "Like"):
                         elem.click()
                         count = count + 1
                         print_to_log('{i} liked post {p}'.format(p = post, i = self._likes + 1),self._print_feedback_results)         
                         self.c.execute(sql,[post,self._date])
                         self.conn.commit()
                         #self.ltd = self.ltd + 1      #likes to date
                         self._likes = self._likes + 1  #likes this session

                         #check for block
                         self._check_for_block()
                     elif(elem.get_attribute("aria-label") == "Unlike"): 
                         #we have already liked this in the past sorted added to the DB
                         self.c.execute(sql,[post,self._date])
                         self.conn.commit()
                         self._skips = self._skips + 1
                         print_to_log('Skipping {}'.format(post),self._print_feedback_results)
                     else:
                         print_to_log("Something isnt right.. not loaded or not were im supposed to be. Moving on..",self._print_feedback_results)
                         continue

                     self._urls_remaining_count = self._urls_remaining_count - 1
                     self._urls_in_queue = self._urls_in_queue - 1
                     
                     #sleep for moment to keep bot human like
                     if(self._urls_in_queue > 0):
                          self._sleep_with_iterupt(self._LIKE_DELAY_RANGE[0],self._LIKE_DELAY_RANGE[1])
                     if(not self._enabled):
                         return
        except Exception as e:
          print(e)
          _, file_name, line_number, function_name, _, _ = inspect.stack()[0]
          save_log(file_name, line_number, function_name, e)            
     #main bot driver
     def run(self):
        print("Running")
        while(True):
            try: 
                 if(self._enabled):
                     try:
                         self.conn = sqlite3.connect('db_instagram_data.db')
                         self.c = self.conn.cursor()
                     except sqlite3.Error:
                         print_to_log ("Error open db.\n",self._print_feedback_results)
                         print_to_log("Exiting Program",self._print_feedback_results)
                         input("Press Enter to Exit Program...")
                         exit()
                         
                     try:
                         #set up two tables Questions and jobs applied to
                         self.c.execute('''CREATE TABLE tblUrlsVisted (url text)''')
                         print_to_log("Created tblUrlsVisted Table",self._print_feedback_results)

                         # Save (commit) the changes
                         self.conn.commit()
                         print_to_log("Tables Created",self._print_feedback_results)
                     except:
                         pass #Tables Already Exist
                         
                     self.set_config_from_ini()
                     self._paused_time = 0
                     self._start = timeit.default_timer()
                     self._skips = 0
                     self.enabled(True)
                     self.pause(False)

                     self.open_instagram()
                     
                     if(self._USE_LOGIN):
                         self.login(self._USER_NAME,self._PASSWORD)
                     elif('YOUR_USER_NAME' in self._GOOGLE_PROFILE_PATH):
                         print_to_log("!! -- Replace <YOUR_USER_NAME> in GOOGLE_PROFILE_PATH in CONFIG.ini then rerun program",self._print_feedback_results)
                         print_to_log("Exiting Program",self._print_feedback_results)
                         input("Press Enter to Exit Program...")
                         exit()
                         
                     for c in self._CATEGORIES:
                         if(not self._enabled):
                             break
                         self._manage_pause()
                         if(self._issue is None):
                             self._category_current = c
                             state = self._manage_pause()
                             self._print_feedback()
                             if(not self.enabled):
                                 break
                             print_to_log("Searching..",self._print_feedback_results)
                             self.search(c)
                             urls = self.get_posts_urls()
                             self.like_posts(urls)
                             
                             if(not self._enabled):
                                 break
                              
                     self.create_results_file()
                     self.enabled(False)
                     self._started = False
                     self._state = "DONE"
                     self._print_feedback()
                     
                     print_to_log("Finished Running",self._print_feedback_results)
                     if(not self._show_menu):
                          break
                 else:
                     time.sleep(1)
            except Exception as e:
               print(e)
               _, file_name, line_number, function_name, _, _ = inspect.stack()[0]
               save_log(file_name, line_number, function_name, e)         
     #this PAUSED and OFF when set
     def _manage_pause(self):
        while(self._paused):
            self._print_feedback()
            time.sleep(1)
            if(not self._enabled):
                return self._state
        return self._state

     #this counts all likes in the DB the current day
     def count_todays_likes(self):
        sql = "SELECT COUNT(url) from tblUrlsVisted WHERE date = '{}'".format(self._date)
        self.c.execute(sql)
        self._likes_today = self.c.fetchone()[0]

     def stop(self):
        if(self._enabled):
            self.enabled(False)
            #self._t.join()
            while(self._state != "DONE" and self._state != "OFF"):
                print_to_log("STOPPED",self._print_feedback_results)
                time.sleep(2)
                print(self._state)
                self._print_feedback(False)



     def start(self):
         print("starting")
         if(self._state == "OFF" or self._state == "DONE" ):
            self.enabled(True)
            if(not self._started):
                #self._t.start()
                 self._started = True
                 self.run()
                 
                
     def resume(self):
        if(self._state == "PAUSED"):
            self.pause(False)
            self._start = timeit.default_timer()
            print_to_log("RESUMED",self._print_feedback_results)
            time.sleep(2)

     #sets pause flag   
     def pause(self, v = True):
        self._paused = v
        if(self._paused): 
            self._state = "PAUSED"
        else:
            if(self.enabled):
                self._state = "ON"
                
     #sets enabled flag
     def enabled(self,v):
        self._enabled = v
        if(not self._enabled):            
            self._state = "OFF"
        else:
            self._state = "ON"

     # define our clear function 
     def _clear(self): 
        # for windows 
        if os.name == 'nt': 
            _ = os.system('cls')   
        # for mac and linux(here, os.name is 'posix') 
        else: 
            _ = os.system('clear')
            
     #this is sleep function state inbetween sleep intervals
     def _sleep_with_iterupt(self,_from,_to):
        sleep_time = randint(_from,_to)
        self._time_remaining = sleep_time
        for t in range(0, sleep_time):
            if(not self._enabled):
                return
            time.sleep(1)
            self._time_remaining =  self._time_remaining - 1
            state = self._manage_pause()
            self._print_feedback()

     #this handles the input to the bot when running assigned to thread in run        
     def cmd_in(self):
        try:  
             self.t = threading.Thread(target=self.run)
             started = False
             self._show_menu = True
             self._print_feedback(False)
             while(True):
                 state = self._state         
                 r = input()
                 r = r.lower()
                 if(r == "stop" or r == "4"):
                     self.enabled(False)     
                     if(self._state == "DONE"):
                         print_to_log("STOPPED",self._print_feedback_results)
                         time.sleep(2)
                         self._print_feedback(False)
                         self.t.join()
                 elif(r == "pause" or r == "2"):
                     if(self._state == "ON"):
                         self.pause(True)
                         self._paused_time =  self._paused_time + int(-1*(self._start - timeit.default_timer()))
                         print_to_log("PAUSED",self._print_feedback_results)
                         time.sleep(2)
                 elif(r == "resume" or r == "3"):
                     if(self._state == "PAUSED"):
                         self.pause(False)
                         self._start = timeit.default_timer()
                         print_to_log("RESUMED",self._print_feedback_results)
                         time.sleep(2)
                 elif(r == "start"or r == "1"):
                     if(self._state == "OFF" or self._state == "DONE" ):
                         self.enabled(True)
                         if(not started):
                             self.t.start()
                             started = True
        except Exception as e:
             print(e)
             _, file_name, line_number, function_name, _, _ = inspect.stack()[0]
             save_log(file_name, line_number, function_name, e)

                
     #this prints feedback for bot
     def _print_feedback(self, is_running = True):
          try:  
             datetimeFormat = '%Y-%m-%d %H:%M:%S.%f'
             stop = 0
             if(is_running):
                 self.count_todays_likes()
                 if(not self._state == "PAUSED"):
                     stop = self._paused_time + int(-1*(self._start - timeit.default_timer()))
                 else:
                     stop = self._paused_time


             if(self._print_feedback_results):        
                  out_layout = str("\033[1;33;40m-----------------------Instagram Automation Tool------------------------\n"
                      " \033[0;33;40m@ \033[1;35;40mUrls Available:\033[0;33;40m{urls_remaining_count:->3}             \033[92m STATUS:{state}\n" 
                      " \033[0;33;40m@ \033[1;35;40mUrls In Queue:\033[0;33;40m{queue:->4}             \033[94m Sleep-Time Remaining:\033[1;37;40m{tm}\n" 
                      " \033[0;33;40m@ \033[1;35;40mUrls Skips:\033[0;33;40m{skips:->7}             \033[94m Runtime:\033[1;37;40m{rn}\n"
                      " \033[0;33;40m@ \033[1;35;40mUrl Limit:\033[0;33;40m{limit:->8}             \033[94m ISSUE:\033[1;37;40m{issue}\n"
                      "\n\033[0;33;40m"
                      " * \033[1;36;40mLast Url:\033[0;33;40m{last_url}\n"
                      " * \033[1;36;40mCatgeorgies:\033[0;33;40m{catgories_list}\n"                       
                      " * \033[1;36;40mCurent Category: \033[1;34;40m{current_category}\n"
                      "\n"                                                                                            
                      " \033[0;33;40m-\033[1;37;40m Likes:\033[1;34;40m{likes}\n"
                      " \033[0;33;40m#\033[1;37;40m Total Likes Today :\033[1;34;40m{today_likes}\n"
                      "\033[1;33;40m************************************************************************\n"
                      "------------------------------------------------------------------------\n")
                  menu = str(" \033[1;34;40mCOMMANDS LIST:\n"                               
                      "   \033[1;33;40m1)START\n"
                      "   2)PAUSE\n"             
                      "   3)RESUME\n"
                      "   4)STOP\n\n"            
                      "\n"             
                      "\033[1;37;40mEnter Command or # at anytime...\n")

                  if(self._show_menu):
                      out_layout = out_layout + menu
                      
                  self._clear()
                  formated_time = time.strftime('%H:%M:%S', time.gmtime(stop))
                  print(out_layout.format(urls_remaining_count = self._urls_remaining_count,
                                          state = self._state,
                                          tm = self._time_remaining,
                                          last_url = self._last_url,
                                          queue = self._urls_in_queue,
                                          catgories_list = self._CATEGORIES,
                                          current_category = self._category_current,
                                          likes = self._likes,
                                          skips = self._skips,
                                          today_likes = self._likes_today,
                                          limit = self._LIKE_LIMIT_PER_CATGEORY,
                                          rn = formated_time,
                                          issue = self._issue))

          except Exception as e:
               print(e)
               _, file_name, line_number, function_name, _, _ = inspect.stack()[0]
               save_log(file_name, line_number, function_name, e)

#this is main..duh
if __name__ == "__main__":    
    i = instagram_automation()
    i.cmd_in()

        







    





