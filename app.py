# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import UnexpectedAlertPresentException

import re
import os
import sys
import requests

from helpers import *
from settings import SOCIAL_SITE_URL, WAIT_TIMEOUT, UPLOAD_TYPE, DEBUG, MAX_RETRIES
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

    # wait until login dialog has been loaded
    WebDriverWait(browser, WAIT_TIMEOUT).until(
        expected_conditions.presence_of_element_located((By.NAME, "password"))
        )

    # look for username password input fields and login
    username_input = browser.find_element_by_name('username')
    password_input = browser.find_element_by_name('password')
    username_input.send_keys(LOGIN_USERNAME)
    password_input.clear()
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

    if DEBUG:
        print "FCODE: %s" % selected_file["FCODE"]
        import pprint
        pprint.pprint(selected_file)

    return {
        'FCODE': selected_file["FCODE"].strip() if selected_file["FCODE"] else None,
        'PAPERNO': selected_file[utf8('案號')].strip() or None,
        'CREATDT': selected_file['crtdt'].strip() or None
    }


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
    browser.switch_to_default_content()


    # success detection
    if re.search(u"新增共 \\d 個檔案", alert_text):
        print 'uploaded %s - %s' % (user_id, file_number)
        browser.close()
    else:
        # should be an alert here
        print "Alert:", alert_text
        print 'failed'

def action_gen_filesno(browser, paperno, creatdt):
    browser.get("https://social.ntpc.gov.tw/workspace.jsp?prgNo=1112")
    browser.implicitly_wait(3)
    browser.switch_to.frame("content_frame")

    assert paperno and creatdt

    script_to_gen_filesno = compose_set_fileSno_script(paperno, creatdt)
    if DEBUG: print script_to_gen_filesno.encode('utf-8')

    browser.execute_script(script_to_gen_filesno)
    WebDriverWait(browser, WAIT_TIMEOUT)\
        .until(expected_conditions.alert_is_present())
    browser.switch_to_alert().accept()
    browser.implicitly_wait(1)


"""
Commands
"""


def upload(file_path, upload_type=UPLOAD_TYPE, close_after=False):
    """Upload file.

    -t=<str>, --upload_type=<str>  upload type, options: lowIncome, mediumIncome, mediumIncomeOld, disability, poorKid
    """

    if DEBUG: print "file: %s" % file_path

    applier_id = extract_id_from_filename(file_path)

    if DEBUG: print "detected %s in file name" % applier_id

    browser = webdriver.Ie()
    #browser = webdriver.Chrome('chromedriver')

    try:
        part1_login(browser)

        # due to FCODE won't show up everytime, so we can try 3 times.
        data = part2_queryfileno(browser, applier_id, upload_type)
        file_number = data['FCODE']
        
        if not file_number:
            # cannot find FCODE, start generating it.
            paperno = data['PAPERNO']
            creatdt = data['CREATDT']

            action_gen_filesno(browser, paperno, creatdt)

            data = part2_queryfileno(browser, applier_id, upload_type)
            file_number = data['FCODE']

        part3_file_upload(browser, file_number, file_path, applier_id)
    except:
        if close_after:
            browser.close()
        raise



def batchupload(dir_path, upload_type=UPLOAD_TYPE):
    """Batch upload all files in the specified folder

    -t=<str>, --upload_type=<str>  upload type, options: lowIncome, mediumIncome, mediumIncomeOld, disability, poorKid
    """

    # get all pdf files
    for root, dirs, files in os.walk(dir_path.decode('cp950')):
        def is_processed(name):
            result = name.endswith('.pdf')
            postfix_titles = ['done', 'failed']

            for postfix_title in postfix_titles:
                result = result and not name.endswith('-%s.pdf' % postfix_title)
            return result
        pdf_files = filter(is_processed, files)

        for pdf_file in pdf_files:
            fullpath = os.path.join(root, pdf_file)
            try:
                upload(fullpath, upload_type=upload_type, close_after=True)
            except Exception as e:
                # when looking up FCODE failed, skip to the next case.
                print ('uploading %s failed.' % pdf_file), 
                print 'Reason: %s' % e if DEBUG else ''
                if DEBUG:
                    raise
                update_filename(fullpath, postfix='failed')
                continue
            update_filename(fullpath)

def reset_fail(dir_path):

    for root, dirs, files in os.walk(dir_path.decode("cp950")):
        failed_files = filter(lambda n: n.endswith('-failed.pdf'), files)

        for failed_file in failed_files:
            fullpath = os.path.join(root, failed_file)

            try:
                reset_filename(fullpath)
            except WindowsError:
                print [fullpath]

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
    clime.start(white_list=['upload', 'download', 'batchupload', 'reset_fail'], debug=DEBUG)
