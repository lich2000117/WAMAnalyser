#-*-coding:utf-8-*-

#import matplotlib.pyplot as plt
import plotext as pltt
import time
import getpass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import pandas as pd
from tabulate import tabulate

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By   #By.ID
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC

#Turn off Log
import logging
logging.getLogger('WDM').setLevel(logging.NOTSET)

use_local_info = False  # Don't store password information into local, PASSWORD will not be encrypted.


###functions:

#Mode Choosing Input
def ask_user_mode():
    while (True):
        inp = str(input("\n== Mode Select ==: \n  1.Calculate TOTAL WAM: Please Enter: 1\n  2.Calculate COVID-19 WAM: Please Enter: 2\n"))
        if(inp == "1"):
            print("\nTotal WAM Calculator......Initiated\n")
            return '1'
        elif (inp == "2"):
            print("\nCOVID-19 WAM Calculator......Initiated\n")
            return '2'
        else:
            print("Please Enter '1' or '2' ONLY!\n")



## Save User login information to local, to enable reuse.
def save_user_new_pass(userInfo):
    with open('UserPass.json','w') as file_obj:
        json.dump(userInfo, file_obj)
    return

def get_saved_pass():
    """If local has Login Information，Retrive it"""
    try:
        with open('UserPass.json') as file_obj:
            userInfo = json.load(file_obj)
    except:
        return None
    else:
        return userInfo


# Scrap for mark, return a dataframe
def GetDataframe():
    # Click on Latest Degree Button "View" to show score table
    result_rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'cssSmGridView')]")
    names = []
    links = []
    i=0
    print("\n==Please Select One Course to view the result: ")
    for row in result_rows:
        i+=1
        link = row.find_element(By.TAG_NAME, "a")
        links.append(link)
        name = row.find_elements(By.TAG_NAME, "td")[2].text
        names.append(name) # store subject name
        print(i,': ', name)
    while True:
        inp = str(input("==Enter a number and return\n"))
        try:
            index = int(inp)-1
            links[index].click()
            time.sleep(1)
            print("Course Selected!")
            break
        except:
            print("Please Select a Number Above!")
            continue

    # Scraping Part for extracting marks from table.
    try:
        df=pd.read_html(driver.page_source)[0]
        df.loc[df['Grade Description'].str.contains('\^'), 'Covid'] = True
        df.loc[~df['Grade Description'].str.contains('\^'), 'Covid'] = False
        if (type(df) is int):
            print("\nAn error Occured, Please Rerun the program. \n\n")
        else:
            AnalysisMark(df)
            end_greet()
    except:
        print("\n==Seems like there's no results available for this course, please try another course.")
        pass

    input("\nPress Enter to Select Another Course")
    driver.back()
    print("asd")
    GetDataframe()
    return True

def end_greet():
    print("============================\n")
    print("Thank you for using this APP!\n")
    print("Made With \u2764\uFE0F  by " + f"https://lich2000117.github.io/")

def AnalysisMark(df):
    """Analysis Marks"""
    df_covid_adj = df.loc[df["Covid"]!=True]

    ## Get Newest FOUR Marks:
    print(f"\n===================LATEST RESULTS====================\n")
    try:
        print(df.iloc[:4][["Year", "Study Period", "Subject", "Mark", "Grade Code", "Covid"]].to_string(index=False))
    except:
        print(df["Year", "Study Period", "Subject", "Mark", "Grade Code", "Covid"].to_string(index=False))

    ## Summary:
    print(f"\n===================COURSE Summary====================\n")
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


    print(f"\n===================Semester Summary====================\n")
    # adjusted wam
    grouped_df_adj2 = df_covid_adj.groupby(['Year', 'Study Period'], as_index=False).agg(COVID_WAM=('Mark', 'mean'))

    # non-adj wam
    grouped_df_norm2 = df.groupby(['Year', 'Study Period'], as_index=False).agg(TOTAL_WAM=('Mark', 'mean'), TOTAL_std=('Mark', 'std'))
 
    # total dataframe
    grouped_df2 = pd.concat([grouped_df_norm2, grouped_df_adj2[["COVID_WAM"]]], axis=1)
    print(grouped_df2.to_string(index=False))

    print(f"\n\n===================Total Summary====================\n")
    d = [ 
        ["WAM", round(df.loc[df["Covid"]==False]["Mark"].mean(), 2), round(df["Mark"].mean(), 2)],
        ["Median", round(df.loc[df["Covid"]==False]["Mark"].median(), 2), round(df["Mark"].median(), 2)],
        ["std", round(df.loc[df["Covid"]==False]["Mark"].std(), 2), round(df["Mark"].std(), 2)],
        ]
    print(tabulate(d, headers=["", "Covid-Adj Marks", "ALL Marks"]))

    ## Graph
    print(f"\n\n===================Graph Summary====================\n")
    grouped_df2["Period"] = grouped_df2["Year"].astype(str) +" "+ grouped_df2["Study Period"]
    pltt.bar(grouped_df2["Period"].tolist(), grouped_df2["TOTAL_WAM"].tolist())
    pltt.plot([round(df["Mark"].mean(), 2)]*(len(grouped_df2)+1), label = "TotalWAM")
    pltt.plot([round(df.loc[df["Covid"]==False]["Mark"].mean(), 2)]*(len(grouped_df2)+1), label = "CovidWAM")
    pltt.title("My WAM Trend")

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
    print(f"==All Login information will NOT be shared.\n*Your Password will NOT be displayed. Press ENTER when finished.*\n")
    while(True):
        # use local information
        if (use_local_info):
            userInfo = get_saved_pass()
        #if first time login, ask for input, do not save to configurations yet.
        if (not use_local_info) or (not userInfo):
            """ASK for Uni Username and Password"""
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
        print("\n==Trying to Login....", end='')
        # wait untill login successfully
        try:
            WebDriverWait(driver, 10).until(
                # check if the authentication dropdown menu is shown up
                EC.presence_of_element_located((By.XPATH, '//*[@id="okta-sign-in"]/div[1]/div/div/div[3]/div/a'))
            )
            return True
        except Exception as e:
            print("Login Failed, Check your UserName and Password and Try Again.")
            continue

def twostep_part():
    """ 2-step Auth Page"""
    #Click Drop Down then click item, OR we can use javascript to click driver.execute_script("arguments[0].click();", authmethods)
    #driver.find_element(By.XPATH, '//*[@id="okta-sign-in"]/div[1]/div/div/div[3]/div/a').click()
    # ask for how to do verification
    def okta_part():
        """Okta Push to Phone Authentication"""
        print("Using Okta Push to Phone")
        # Select Okta out of the dropdown menu
        phone_auth = driver.find_element(By.XPATH, '//*[@id="okta-dropdown-options"]/ul/li[2]/a')
        driver.execute_script("arguments[0].click();", phone_auth)
        # Push Button to send notification
        driver.find_element(By.XPATH, '//*[@id="okta-sign-in"]/div[2]/div/div/form[1]/div[2]/input').click()
        print("\n==Please Accept the Login Request on your phone\n")
        time.sleep(10)
        return True
        
    def google_part():
        """Google Authentication part untill success"""
        print("Using Google Authenticator.")
        # Select Google Auth
        google_auth = driver.find_element(By.XPATH, '//*[@id="okta-dropdown-options"]/ul/li[3]/a')
        driver.execute_script("arguments[0].click();", google_auth)
        codes = str(input("\n== Please Enter the Google Authenticator Number On your Phone ==: \n "))
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
            print("==Authenticated!")
            return True
        except:
            pass
        inp = str(input("\n== Authentication Method Select ==: \n  1.Okta Push To My Phone: Please Enter: 1\n  2.Google Authenticator: Please Enter: 2\n"))
        if(inp == "1"):
            okta_part()
        elif(inp == "2"):
            google_part()
        
        try:
            WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.XPATH, "//*[text()='Results and Graduation']"))
            )
            print("==Authenticated!")
            return True
        except Exception as e:
            print("Authentication Failed, Please Try Again or Select Different Method")
            continue
#Main Code:            

# Configurations
URL = "https://prod.ss.unimelb.edu.au/student/Login.aspx"

print(f"\n=======  WAM CALCULATOR ========")
print("                     [By Chenghao Li]")
print("\n(If you get stuck, try press ENTER)")
#Driver Initialize
# Headless runs explorer at background without windows
options = Options()
#options.add_argument('headless')
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
print("\n==Make Sure You are Connected to Internet (Use VPN if desired)......\n")
s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service = s, options=options)
print("==Testing Connection......", end='')
driver.get(URL)
print(f"Succeed!\n")

#Login Part:
# "== Login ==", break when succeed.
login_part()
print("Success! \n==Need 2-step authentication!")
twostep_part()
# Direct to result page
try:
    driver.find_element(By.XPATH, "//*[text()='Results and Graduation']").click()
    time.sleep(1)
except:
    print("Cannot Direct To Result Page! Please Rerun the Program")
    assert(1==0)

#Analysis Part
df = GetDataframe()
# Try handle the error


#Finish Off

driver.close()
#driver.quit()
