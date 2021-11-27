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
from selenium.webdriver.chrome.service import Service

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
    try:
        driver.find_element(By.XPATH, "//*[contains(text(), 'View')]").click()
    except:
        pass
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
    grouped_df2 = pd.concat([grouped_df_adj2, grouped_df_norm2[["TOTAL_WAM", "TOTAL_std"]]], axis=1)
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
    


#Main Code:            


# Configurations
URL = "https://prod.ss.unimelb.edu.au/student/Login.aspx"

print(f"\n=======  WAM CALCULATOR ========")
print("                     [By Chenghao Li]")
print("\n(If you get stuck, try press ENTER)")
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
print("\nMake Sure You are Connected to Internet (Use VPN if desired)......\n")
s = Service(ChromeDriverManager(log_level=0).install())
driver = webdriver.Chrome(service = s, options=options)
print("\nTesting Connection......\n")
driver.get(URL)
print(f"Succeed!\n")

#Login Part:
# "== Login ==", break when succeed.
print(f"All Login information will NOT be shared.\n*Your Password will NOT be displayed. Press ENTER when finished.*\n")
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
    time.sleep(0.5)
    driver.find_element(By.ID, 'ctl00_Content_cmdLogin').click()  # Login
    time.sleep(1.5)
    print("\nTrying to Login....")
    #Check if login successfully
    try:
        strs = driver.find_element(By.ID, "ctl00_h1PageTitle").text
        # Login Successfully!
        if strs == "Personal Details":
            # Direct to result page
            try:
                driver.find_element(By.XPATH, "//*[text()='Results and Graduation']").click()
                time.sleep(1)
            except:
                print("Cannot Direct To Result Page!")
                assert(1==0)
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
        print(f"\n___ Login Failed, Please Retry! ___ \n")
        time.sleep(1)
    


        
#Analysis Part
df = GetDataframe()
# Try handle the error
try:
    if (type(df) is int):
        print("\nAn error Occured, Please Rerun the program. \n\n")
    else:
        AnalysisMark(df)
except:
    AnalysisMark(df)


#Finish Off

driver.close()
#driver.quit()
print("============================\n")
print("Thank you for using this APP!\n")
print("Made With \u2764\uFE0F  by " + f"https://lich2000117.github.io/")