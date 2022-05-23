# WAMAnalyser
Get Latest WAM / COVID-19 WAM and bunch of Analysis based on your subject group, semester etc.

Since the University provides students options to include all of their results(including COVID WAM^) in their final year's wam calculation, it is important to know which option is better for you.
Therefore, I wrote this small program that aotumatically calculate your wam with/without covid-19 wam boost.

![plot](./pics/pc1.webp)
![plot](./pics/pc2.webp)

## Functionality:
1. Login into unimelb website with 2-step verification (Okta and Google Authenticator)
1. Retrive latest course results
2. Comparisons between Standard WAM and Covid-Affected WAM.  More Info: (https://students.unimelb.edu.au/your-course/manage-your-course/exams-assessments-and-results/results-and-academic-statements/wam/wam-adjustments-2021)
3. Analysis Plot based on Subjects, Course, Semester

## Quick Guide:

#### Mac/Linux User:
1. Make sure you have Python 3.8+ Installed.
2. Copy "WAMAnalyser.py" to Desktop.
3. Open "Terminal" app.
4. Enter ```cd Desktop```  #set working directory to desktop 
5. Enter in Terminal: ```pip3 install selenium webdriver_manager tabulate plotext lxml```  #Install Packages
6. Run Program, Enter in Terminal: ```python3 WAMAnalyser.py```  #use Python3 to run the program
7. Follow Instructions in Terminal.

#### Windows:
- Download executable file from "release" section.
- Or, follow the similar guide with Mac user defined above.

#### Uninstall:
```pip3 remove selenium webdriver_manager tabulate plotext lxml```

## Known Issues:
- Login might fail if you take Okta Verification too slow.
- For Privacy issues the password will not be displayed but it still works.
- If open the app and nothing happens, press Enter for a few times.


## Your Login information is only used to login into school's website. Your Information will NOT be gathered or shared with any other use.



## Tips For Developer: 
1. Always use XPATH and javascript click instead of simple .click() as some of the button may not be visible.
- XPATH: always use XPATH without dynamic id in it, for example, we don't want id="input17" as it is a dynamic field
- Solution: simply delete this field in the browser's "inspect" tab and copy XPATH again to get one without dynamic ID.
2. Use JavaScript Click rather than .click()
    ```
    element = driver.find(xxxx) 
    driver.execute_script("arguments[0].click();", element)
    ```
3. Build in Windows: use terminal 'auto-py-to-exe' to build, pip can install this package