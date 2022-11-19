#-*-coding:utf-8-*-

#import matplotlib.pyplot as plt
import plotext as pltt
import time
import getpass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
from tabulate import tabulate

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By   #By.ID
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC

# colour definition
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#Turn off Log
import logging
logging.getLogger('WDM').setLevel(logging.NOTSET)

###functions:

# Scrap for mark, return a dataframe
def SelectCourse():
    # This try block handles the situation where you have multiple courses to choose, or it displays result directly
    try:
        # Click on Latest Degree Button "View" to show score table
        result_rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'cssSmGridView')]")
        names = []
        links = []
        i=0
        print(f"{bcolors.HEADER}\n== Please Select One Course to view the result: {bcolors.ENDC}")
        for row in result_rows:
            i+=1
            TDs = row.find_elements(By.TAG_NAME, "td")
            link = TDs[0].find_element(By.TAG_NAME, "a")
            links.append(link)
            name = TDs[2].text
            names.append(name) # store subject name
            print(i,': ', name)
        while True:
            inp = str(input(f"{bcolors.HEADER}== Enter a number and return\n{bcolors.ENDC}"))
            try:
                index = int(inp)-1
                links[index].click()
                time.sleep(1)
                #print("Course Selected!")
                break
            except:
                print(f"{bcolors.WARNING}Please Select a Number Above!{bcolors.ENDC}")
                continue
    except:
        pass
    # Scraping Part for extracting marks from table.
    try:
        df=pd.read_html(driver.page_source)[0]
        df.loc[df['Grade Description'].str.contains('\^'), 'Covid'] = True
        df.loc[~df['Grade Description'].str.contains('\^'), 'Covid'] = False
        if (type(df) is int):
            print(f"{bcolors.FAIL}\nAn error Occured, Please Rerun the program. \n\n{bcolors.ENDC}")
        else:
            AnalysisMark(df)
            end_greet()
    except Exception as e:
        print(e)
        print(f"{bcolors.WARNING}\n==Seems like there's no results available for this course, please try another course.{bcolors.ENDC}")
        pass

    i = str(input(f"{bcolors.BOLD}\n== Enter Any Key to try another course! == \n== Press 'q' to quit =={bcolors.ENDC}"))
    if i == "q":
        return False
    else:
        driver.back()
        SelectCourse()
    return False

def end_greet():
    print("\n================================================\n")
    print(f"{bcolors.OKGREEN}Thank you for using this APP!\n{bcolors.ENDC}")
    print("Made With \u2764\uFE0F  by " + f"{bcolors.OKCYAN}https://lich2000117.github.io/{bcolors.ENDC}")

def AnalysisMark(df):
    """Analysis Marks"""
    df_covid_adj = df.loc[df["Covid"]!=True]

    print(f"{bcolors.OKCYAN}Generating Report....{bcolors.ENDC}", end='')
    time.sleep(1)
    print(f"{bcolors.OKGREEN}Succeed!{bcolors.ENDC}")
    time.sleep(0.5)
    

    ## Get Newest FOUR Marks:
    print(f"{bcolors.HEADER}\n=================== LATEST RESULTS ====================\n{bcolors.ENDC}")
    try:
        print(df.iloc[:4][["Year", "Study Period", "Subject", "Mark", "Grade Code", "Covid"]].to_string(index=False))
    except:
        print(df["Year", "Study Period", "Subject", "Mark", "Grade Code", "Covid"].to_string(index=False))

    time.sleep(0.5)

    ## Summary:
    print(f"{bcolors.HEADER}\n=================== COURSE Summary ====================\n{bcolors.ENDC}")
    # Groupby Course Types
    df_covid_adj2 = df_covid_adj.copy()
    df2 = df.copy()
    df_covid_adj2['Subject'] = df_covid_adj2['Subject'].str[:4]
    df2['Subject'] = df2['Subject'].str[:4]
    # adjusted wam
    grouped_df_adj1 = df_covid_adj2.groupby(['Subject'], as_index=False).agg(COVID_WAM=('Mark', 'mean'))
    # non-adj wam
    grouped_df_norm1 = df2.groupby(['Subject'], as_index=False).agg(TOTAL_WAM=('Mark', 'mean'), TOTAL_std=('Mark', 'std'))
    # total dataframe
    grouped_df1 = pd.concat([grouped_df_norm1, grouped_df_adj1[["COVID_WAM"]]], axis=1)
    print(grouped_df1.sort_values(by=['TOTAL_WAM'], ascending = False).to_string(index=False))

    time.sleep(1)

    print(f"{bcolors.HEADER}\n=================== Semester Summary ====================\n{bcolors.ENDC}")
    # adjusted wam
    grouped_df_adj2 = df_covid_adj.groupby(['Year', 'Study Period'], as_index=False).agg(COVID_WAM=('Mark', 'mean'))
    # non-adj wam
    grouped_df_norm2 = df.groupby(['Year', 'Study Period'], as_index=False).agg(TOTAL_WAM=('Mark', 'mean'), TOTAL_std=('Mark', 'std'))
    # total dataframe
    grouped_df2 = pd.concat([grouped_df_norm2, grouped_df_adj2[["COVID_WAM"]]], axis=1)
    print(grouped_df2.to_string(index=False))

    time.sleep(0.2)

    print(f"{bcolors.HEADER}\n\n=================== Total Summary ====================\n{bcolors.ENDC}")
    d = [ 
        ["WAM", round(df.loc[df["Covid"]==False]["Mark"].mean(), 2), round(df["Mark"].mean(), 2)],
        ["Median", round(df.loc[df["Covid"]==False]["Mark"].median(), 2), round(df["Mark"].median(), 2)],
        ["std", round(df.loc[df["Covid"]==False]["Mark"].std(), 2), round(df["Mark"].std(), 2)],
        ]
    print(tabulate(d, headers=["", "Covid-Adj Marks", "ALL Marks"]))

    ## Graph
    print(f"{bcolors.OKCYAN}Generating Graph....{bcolors.ENDC}", end='')
    time.sleep(2)
    print(f"{bcolors.OKGREEN}Succeed!{bcolors.ENDC}")
    time.sleep(1)
    
    print(f"{bcolors.HEADER}\n\n=================== Graph Summary ====================\n{bcolors.ENDC}")
    pltt.clear_figure()
    pltt.ylim(min(grouped_df2["TOTAL_WAM"].tolist()), 100) # set y axis low and high limit
    grouped_df2["Period"] = grouped_df2["Year"].astype(str) +" "+ grouped_df2["Study Period"]
   
    # simple horizontal plot
    pltt.simple_multiple_bar(grouped_df2["Period"].tolist(), [grouped_df2["TOTAL_WAM"].tolist()], labels = ["WAM"], title = "WAM Trend")
    
    # bar plot with WAM line
    #pltt.bar(grouped_df2["Period"].tolist(), grouped_df2["TOTAL_WAM"].tolist())
    #pltt.plot([round(df["Mark"].mean(), 2)]*(len(grouped_df2)+1), label = "TotalWAM")
    #pltt.plot([round(df.loc[df["Covid"]==False]["Mark"].mean(), 2)]*(len(grouped_df2)+1), label = "CovidWAM")
    #pltt.title("My WAM Trend")
    #input(f"\nPress ANY KEY to show my WAM trend: ")
    pltt.show()
    
    ## Pop Out GRAPH:
    # plt.figure(figsize=(10, 5), dpi=160)
    # plt.tight_layout()
    # plt.ylim([30, 100])
    # grouped_df2["TOTAL_WAM"].plot(kind='bar',x=['Year', 'Study Period'],y='TOTAL_WAM',rot=10)
    # #Plot WAM line
    # plt.axhline(y=round(df["Mark"].mean(), 2), color='r', linestyle='-', label="TotalWAM")
    # plt.axhline(y=round(df.loc[df["Covid"]==False]["Mark"].mean(), 2), color='b', linestyle='-', label="COVIDWAM")
    # plt.title("My WAM Trend")
    # plt.legend(loc='center left', bbox_to_anchor=(0, 0.3))
    # input(f"\nPress ANY KEY to show my WAM trend: ")
    # print(plt.show())
    return
    
def login_part():
    """Login function that controls login part of the program"""
    print(f"{bcolors.FAIL}==All Login information will NOT be shared.\n{bcolors.ENDC}" + 
    f"*Your Password will NOT be displayed. Press ENTER when finished.*\n")
    while(True):
        # use local information
        #if first time login, ask for input, do not save to configurations yet.
        """ASK for Uni Username(not email) and Password"""
        userName = str(input("Uni UserName: "))
        passWord = str(getpass.getpass("Uni Password: "))
        userInfo = {
            'userName': userName,
            'passWord': passWord,}

        #Login Coding
        driver.find_element(By.ID, 'okta-signin-username').clear()    #UserName
        driver.find_element(By.ID, 'okta-signin-username').send_keys(userInfo['userName'])
        driver.find_element(By.ID, 'okta-signin-password').clear()
        driver.find_element(By.ID, 'okta-signin-password').send_keys(userInfo['passWord'])  #password
        time.sleep(0.5)
        driver.find_element(By.ID, 'okta-signin-submit').click()  # Login
        print(f"{bcolors.OKCYAN}\n==Trying to Login....{bcolors.ENDC}", end='')
        # wait untill login successfully
        try:
            WebDriverWait(driver, 12).until(
                # check if the url is directed to verify page
                EC.url_contains("verify")
            )
            time.sleep(1)
            return True
                    #driver.find_element(By.ID, 'okta-signin-username').clear()
        except Exception as e:
            print(e)
            print(f"{bcolors.WARNING}Login Failed, Check your UserName and Password and Try Again.{bcolors.ENDC}")
            continue

def twostep_part():
    """ 2-step Auth Page"""
    #Click Drop Down then click item, OR we can use javascript to click driver.execute_script("arguments[0].click();", authmethods)
    #driver.find_element(By.XPATH, '//*[@id="okta-sign-in"]/div[1]/div/div/div[3]/div/a').click()
    # ask for how to do verification
    def okta_part():
        """Okta Push to Phone Authentication"""
        # Select Okta out of the dropdown menu or check if it's already therer
        try:
            title = driver.find_element(By.XPATH, '//*[@id="okta-sign-in"]/div[2]/div/div/form[1]/div[1]/h2').text
            if "Okta" not in title:
                phone_auth = driver.find_element(By.XPATH, '//*[@id="okta-dropdown-options"]/ul/li[2]/a')
                driver.execute_script("arguments[0].click();", phone_auth)
        except:
            print(f"{bcolors.FAIL}Cannot Do Okta Auth, Please Try other options!{bcolors.ENDC}")
            return False
        # Push Button to send notification
        time.sleep(1)
        driver.find_element(By.XPATH, '//*[@id="okta-sign-in"]/div[2]/div/div/form[1]/div[2]/input').click()
        print(f"{bcolors.OKBLUE}\n== Please Accept the Login Request on your phone\n{bcolors.ENDC}")
        time.sleep(10)
        return True
        
    def google_part():
        """Google Authentication part untill success"""
        # Select Google Auth
        try:
            title = driver.find_element(By.XPATH, '//*[@id="okta-sign-in"]/div[2]/div/div/form[1]/div[1]/h2').text
            if "Google" not in title:
                google_auth = driver.find_element(By.XPATH, '//*[@id="okta-dropdown-options"]/ul/li[3]/a')
                driver.execute_script("arguments[0].click();", google_auth)
        except:
            print(f"{bcolors.FAIL}Cannot Do Google Auth, Please Try other options!{bcolors.ENDC}")
            return False
        codes = str(input(f"{bcolors.OKBLUE}\n== Please Enter the Google Authenticator Number On your Phone ==: \n {bcolors.ENDC}"))
        driver.find_element(By.XPATH, '//*[@id="okta-sign-in"]/div[2]/div/div/form/div[1]/div[2]/div[1]/div[2]/span/input').clear()
        driver.find_element(By.XPATH, '//*[@id="okta-sign-in"]/div[2]/div/div/form/div[1]/div[2]/div[1]/div[2]/span/input').send_keys(codes)
        time.sleep(0.5)
        driver.find_element(By.XPATH, '//*[@id="okta-sign-in"]/div[2]/div/div/form').submit()
        time.sleep(5)
        return True
    while True:
        try:
            WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, "//*[text()='Results and Graduation']"))
            )
            print(f"{bcolors.OKGREEN}== Authenticated! =={bcolors.ENDC}")
            return True
        except:
            pass
        inp = str(input(f"{bcolors.OKBLUE}\n== Authentication Method Select ==: \n{bcolors.ENDC}" + "  1.Okta Push To My Phone: Please Enter: 1\n  2.Google Authenticator: Please Enter: 2\n"))
        if(inp == "1"):
            if not okta_part(): continue # continue to re-select login methods
        elif(inp == "2"):
            if not google_part(): continue
        
        try:
            WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.XPATH, "//*[text()='Results and Graduation']"))
            )
            print(f"{bcolors.OKGREEN}==Authenticated!{bcolors.ENDC}")
            return True
        except Exception as e:
            print(f"{bcolors.WARNING}Authentication Failed, Please Try Again or Select Different Method\n{bcolors.ENDC}")
            continue
#Main Code:            

# Configurations
URL = "https://prod.ss.unimelb.edu.au/student/Login.aspx"

print(f"{bcolors.HEADER}\n==========  WAM Analyser ==========={bcolors.ENDC}")
print(f"                     [By Chenghao Li]")
print(f"{bcolors.OKBLUE}\n(If you get stuck, try press ENTER){bcolors.ENDC}")
#Driver Initialize
# Headless runs explorer at background without windows
options = Options()
options.add_argument('headless')
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument('log-level=3')
options.add_argument("--window-size=4000,1600") #Big Window
options.add_argument("--mute-audio") #Mute
#Disable Image Loading
No_Image_loading = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", No_Image_loading)

##using firefox driver Open windows
#driver = webdriver.Firefox(options=options, executable_path=driverPath)
#driver = webdriver.Chrome(options=options, executable_path=driverPath)

## Install Driver
print(f"{bcolors.WARNING}\n== Make Sure You are Connected to Internet (Use VPN if desired)......\n{bcolors.ENDC}")
s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service = s, options=options)
print(f"{bcolors.OKCYAN}\n\n== Testing Connection......{bcolors.ENDC}", end='')
driver.get(URL)
print(f"{bcolors.OKGREEN}Succeed!\n{bcolors.ENDC}")

#Login Part:
# "== Login ==", break when succeed.
login_part()
print(f"{bcolors.OKGREEN}Succeed!{bcolors.ENDC}")
twostep_part()
# Direct to result page
try:
    driver.find_element(By.XPATH, "//*[text()='Results and Graduation']").click()
    time.sleep(1)
except:
    print(f"{bcolors.FAIL}Cannot Direct To Result Page! Please run the Program again{bcolors.ENDC}")
    assert(1==0)

#Analysis Part
SelectCourse()
#Finish Off, close driver
driver.quit()
