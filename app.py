# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert

import re
import os
import sys
import requests

from helpers import *
from settings import SOCIAL_SITE_URL, WAIT_TIMEOUT, UPLOAD_TYPE
from social_exceptions import NoFileFoundException

try:
    from social_credentials import LOGIN_USERNAME, LOGIN_PASSWORD
    from social_testcases import TEST_APPLIER_ID, TEST_UPLOAD_FILE
except ImportError:
    raise ImportError(
        "Please add social_testcases, social_credentials module at first")


"""
Page Actions
"""
def part1_login(browser):
    """
    Part 1.
    Initiate the browser and login
    """

    # go to homepage
    browser.get(SOCIAL_SITE_URL)

    # look for username password input fields and login
    username_input = browser.find_element_by_id('username')
    password_input = browser.find_element_by_id('password')
    username_input.send_keys(LOGIN_USERNAME)
    password_input.send_keys(LOGIN_PASSWORD + Keys.RETURN)

    # wait until logged in
    # Locator format (tuple): (By.<type>, <value>)
    WebDriverWait(browser, WAIT_TIMEOUT).until(
        expected_conditions.presence_of_element_located((By.ID, "3000"))
        )


def part2_queryfileno(browser, applier_id, upload_type):
    """
    Part 2.
    Query the file number directly
    """
    utf8 = lambda x: x.decode('utf-8')

    script_get_content = """
        document.title = document.body.innerHTML;
    """

    # go to query page with parameters directly
    browser.get(build_query_url(applier_id, upload_type))

    # use re to search which matches file number pattern
    browser.execute_script(script_get_content)
    html_contains_fileno = browser.title

    #TODO: change pattern to <td>(fileno)</td><td>userid</td>,
    # and file no. is not 11 digits anymore, could be 10 or 9.
    # we assume 12 - 7 for futher usage.
    data = convert_query_result_to_dict(html_contains_fileno)
    data_matched_id = filter(lambda d: d[utf8('身分證號')] == applier_id, data)
    selected_file = data_matched_id[0]


    print utf8('案號'), selected_file[utf8("案號")]
    print selected_file
 
    return selected_file[utf8("案號")].strip()


def part3_file_upload(browser, file_number, upload_file_path, user_id):
    """
    Part 3.
    upload file via robot
    """
    upload_file_path = os.path.abspath(upload_file_path)

    browser.get(build_upload_interface_url(file_number))

    WebDriverWait(browser, WAIT_TIMEOUT)\
            .until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "input[type=file]")))

    # Traverse all checkboxes and find first not selected one for uploading.
    # (update), just use the first one it's okay
    fileIndex = 0
    checkboxName = 'checkboxKey%s' % fileIndex
    srcName = 'fileSrc%s' % fileIndex

    # upload file
    elem_src = browser.find_element_by_name(srcName)
    elem_src.send_keys(upload_file_path)

    import ipdb; ipdb.set_trace()
    # submit the form
    script_upload = """
        runAction('Upload');
    """
    browser.execute_script(script_upload)

    # wait for alert
    WebDriverWait(browser, WAIT_TIMEOUT)\
            .until(expected_conditions.alert_is_present())

    alert_text = Alert(browser).text
    Alert(browser).accept()


    # success detection
    if re.search(u"新增共 \\d 個檔案", alert_text):
        print 'uploaded %s - %s' % (user_id, file_number)
        browser.close()
    else:
        # should be an alert here
        print "Alert:", alert_text
        print 'failed'

"""
Commands
"""


def upload(file_path, upload_type=UPLOAD_TYPE):
    """Upload file.

    -t=<str>, --upload_type=<str>  upload type, options: lowIncome, mediumIncome, mediumIncomeOld, disability, poorKid
    """
    applier_id = extract_id_from_filename(file_path)

    browser = webdriver.Chrome('chromedriver')

    part1_login(browser)
    file_number = part2_queryfileno(browser, applier_id, upload_type)
    part3_file_upload(browser, file_number, file_path.decode('utf-8'), applier_id)

def batchupload(dir_path, upload_type=UPLOAD_TYPE):
    """Batch upload all files in the specified folder

    -t=<str>, --upload_type=<str>  upload type, options: lowIncome, mediumIncome, mediumIncomeOld, disability, poorKid
    """

    # get all pdf files
    for root, dirs, files in os.walk(dir_path):
        pdf_files = filter(lambda name: name.endswith('.pdf'), files)

        for pdf_file in pdf_files:
            fullpath = os.path.join(root, pdf_file)
            upload(fullpath, upload_type=upload_type)



def download(target_id):

    browser = webdriver.Ie()

    part1_login(browser)

    loggedin_cookies = cookies_to_dict(browser.get_cookies())

    get_profile_url = 'https://social.ntpc.gov.tw/jsp/G/SWJG010.jsp?update=1231231123'
    get_profile_formdata = 'actionType=query&primarykey1=&primarykey2=&primarykey3=&P_QUERYTYPE=G010&P_USERDOWNTN=10100010&P_ALLTITLES=11003005&P_LIMITCONTROL=townApply&P_FDYYY=&P_CHECKFLAG0=0&P_CHECKFLAG=&P_WFNO1=&P_WFNO2=&P_TBHEAD=W00&view_P_APPDTS=&P_APPDTS=&view_P_APPDTE=&P_APPDTE=&P_IDNO=F290211348&P_NAME=&P_DOWNTN=&P_AREA=&view_P_WSDTS=&P_WSDTS=&view_P_WSDTE=&P_WSDTE=&P_APPDOWNTN=&P_APPIDNO=&view_P_ALLOTDTSY=&view_P_ALLOTDTSM=&P_ALLOTDTS=&view_P_ALLOTDTEY=&view_P_ALLOTDTEM=&P_ALLOTDTE=&P_CHK539=&view_P_DOCDT=&P_DOCDT=&P_DOCNO='

    resp_caselist = requests.post(get_profile_url, data=get_profile_formdata, cookies=loggedin_cookies, verify=False)
    print resp_caselist.text



if __name__ == '__main__':
    import clime
    clime.start(white_list=['upload', 'download', 'batchupload'])
