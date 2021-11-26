#-*-coding:utf-8-*-

import numpy as np
import matplotlib.pyplot as plt

import time
import getpass
from selenium import webdriver
#from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains  #鼠标操作包
import os
import json
import pandas as pd
from tabulate import tabulate


from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select  #select类，下拉菜单使用
from selenium.webdriver.common.by import By   #By.ID
from selenium.webdriver.chrome.service import Service


#get current directory
cwd = os.getcwd()

use_local_info = False  # Don't store password information into local, PASSWORD will not be encrypted.


###functions:

#模式选择Input
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
    ## Output Format:
    MarkInfo = {
            'covid_list': [],
            'norm_list': [],    
            'covid_count': 0,
            'norm_count': 0,
        }

    # Click on Latest Degree Button "View" to show score table
    try:
        driver.find_element(By.ID, "ctl00_Content_grdResultPlans_ctl02_ctl00").click()
    except:
        print("Failed to click on degree button!\n")
        return -1
    time.sleep(1)

    # Scraping Part for extracting marks from table.
    df=pd.read_html(driver.page_source)[0]
    df.loc[df['Grade Description'].str.contains('\^'), 'Covid'] = True
    df.loc[~df['Grade Description'].str.contains('\^'), 'Covid'] = False
    #print(df)
    return df


def AnalysisMark(df):
    """Analysis Marks"""
    df_covid_adj = df.loc[df["Covid"]!=True]

    ## Get Newest FOUR Marks:
    print(f"\n===========LATEST RESULTS============\n")
    print(df.iloc[:4]["Year", "Study Period", "Subject", "Short Title", "Mark", "Grade Code"])

    ## Summary:
    print(f"\n===========Semester Summary============\n")
    # adjusted wam
    grouped_df_adj = df_covid_adj.groupby(['Year', 'Study Period'], as_index=True).agg(COVID_WAM=('Mark', 'mean'))
    #print(grouped_df_adj)
    # non-adj wam
    grouped_df_norm = df.groupby(['Year', 'Study Period'], as_index=True).agg(TOTAL_WAM=('Mark', 'mean'), TOTAL_std=('Mark', 'std'))
    # total dataframe
    grouped_df = pd.concat([grouped_df_adj, grouped_df_norm[["TOTAL_WAM", "TOTAL_std"]]], axis=1)
    print(grouped_df)
    print(f"\n\n===========Total Summary============\n")
    d = [ 
        ["WAM", round(df.loc[df["Covid"]==False]["Mark"].mean(), 2), round(df["Mark"].mean(), 2)],
        ["Median", round(df.loc[df["Covid"]==False]["Mark"].median(), 2), round(df["Mark"].median(), 2)],
        ["std", round(df.loc[df["Covid"]==False]["Mark"].std(), 2), round(df["Mark"].std(), 2)],
        ]
    print(tabulate(d, headers=["", "Covid-Adj Marks", "ALL Marks"]))

    ## Graph
    plt.figure(figsize=(12, 5), dpi=200)
    plt.tight_layout()
    plt.ylim([30, 100])
    
    grouped_df["TOTAL_WAM"].plot(kind='bar',x=['Year', 'Study Period'],y='TOTAL_WAM',rot=10)
    #Plot WAM line
    plt.axhline(y=round(df["Mark"].mean(), 2), color='r', linestyle='-', label="TotalWAM")
    plt.axhline(y=round(df.loc[df["Covid"]==False]["Mark"].mean(), 2), color='b', linestyle='-', label="COVIDWAM")

    
    plt.title("My WAM Trend")
    plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    
    input(f"Press ANY KEY to show my WAM trend: ")
    plt.show()
    return
    


#Main Code:            


# Configurations
URL = "https://prod.ss.unimelb.edu.au/student/login.aspx?ReturnUrl=%2fstudent%2fSM%2fResultsDtls10.aspx%3fr%3d%2523UM.STUDENT.APPLICANT%26f%3d%24S1.EST.RSLTDTLS.WEB&r=%23UM.STUDENT.APPLICANT&f=$S1.EST.RSLTDTLS.WEB"

print(f"\n=======  WAM CALCULATOR ========")
print("                     By Chenghao Li")
print("\nPlease Press ENTER after your entry later.")
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
s = Service(ChromeDriverManager(log_level=0).install())
driver = webdriver.Chrome(service = s, options=options)

print("Testing Connection......\n", end = '')
driver.get(URL)
print(f"Succeed!\n")

#Login Part:
# "== Login ==", break when succeed.
print(f"All Login information will NOT be shared.\n")
while(True):
    if (use_local_info):
        userInfo = get_saved_pass()
    #if first time login, ask for input, do not save to configurations yet.
    if (not use_local_info) or (not userInfo):
        """ASK for ID Password"""
        userName = str(input("Uni UserName: "))
        passWord = str(getpass.getpass("Uni Password: "))
        userInfo = {
            'userName': userName,
            'passWord': passWord,    
        }

    #Login Coding
    driver.find_element(By.ID, 'ctl00_Content_txtUserName_txtText').clear()    #UserName
    driver.find_element(By.ID, 'ctl00_Content_txtUserName_txtText').send_keys(userInfo['userName'])
    driver.find_element(By.ID, 'ctl00_Content_txtPassword_txtText').clear()
    driver.find_element(By.ID, 'ctl00_Content_txtPassword_txtText').send_keys(userInfo['passWord'])  #password
    time.sleep(1)
    driver.find_element(By.ID, 'ctl00_Content_cmdLogin').click()  # Login
    time.sleep(1)
    print("\nTrying to Login....")

    #Check if login successfully
    try:
        strs = driver.find_element(By.ID, "ctl00_h1PageTitle").text
        if strs == "Results > Choose a Study Plan":
            #Save To Local?
            #use_local_info = str(input("Do you want to save your login information on your computer? (T/F)"))
            if use_local_info == True:
                save_user_new_pass(userInfo)  # Save information to local
            print("\nUser " + f"{userInfo['userName']}" + " Login Successfully!")
            break
        # Fail to login, Retry
        else:
            print(f"\n Time out, Please Retry! ___\n")
            time.sleep(1)
    except:
        print(f"\n___ Unmatched UserName and Passwords, Please Retry! ___ \n")
        time.sleep(1)
    


        
#Analysis Part
df = GetDataframe()
# Try handle the error
try:
    if (df == -1):
        print("\nAn error Occured, Please Rerun the program. \n\n")
except:
    AnalysisMark(df)


#Finish Off

driver.close()
#driver.quit()
print("============================\n")
print("Thank you for using this APP!\n")
print("Made With \u2764\uFE0F  by " + f"https://lich2000117.github.io/")


