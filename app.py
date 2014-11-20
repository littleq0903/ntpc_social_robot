# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert

import re
import sys

from helpers import cookies_to_dict, build_query_url, build_upload_interface_url, extract_id_from_filename
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

    script_get_content = """
        document.title = document.body.innerHTML;
    """

    # go to query page with parameters directly
    browser.get(build_query_url(applier_id, upload_type))

    # use re to search which matches file number pattern
    browser.execute_script(script_get_content)
    html_contains_fileno = browser.title
    fileno = re.search(r'\>(\d{11})\&', html_contains_fileno).group(1)

    return fileno


def part3_file_upload(browser, file_number, upload_file_path):
    """
    Part 3.
    upload file via robot
    """

    browser.get(build_upload_interface_url(file_number))

    """
    WebDriverWait(browser, WAIT_TIMEOUT)\
            .until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, "input[type=file]")))
    """

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

    # should be an alert here
    print "Alert:", alert_text

    # success detection
    if re.search(u"新增共 \\d 個檔案", alert_text):
        print 'succeed'
        browser.close()
        sys.exit(0)
    else:
        print 'failed'


def upload(file_path, upload_type=UPLOAD_TYPE):
    """Upload file.

    -t=<str>, --type=<str> upload type, options: lowIncome, mediumIncome, mediumIncomeOld, disability, poorKid
    """
    applier_id = extract_id_from_filename(file_path)

    browser = webdriver.Chrome('./chromedriver')

    part1_login(browser)
    file_number = part2_queryfileno(browser, applier_id, upload_type)
    part3_file_upload(browser, file_number, file_path.decode('utf-8'))


if __name__ == '__main__':
    import clime.now
