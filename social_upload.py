
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

import time
import requests
import re

import sys

try:
    from social_credentials import LOGIN_USERNAME, LOGIN_PASSWORD
    from social_testcases import TEST_APPLIER_ID, TEST_UPLOAD_FILE
except ImportError:
    raise ImportError(
        "Please add social_testcases, social_credentials module at first")

SOCIAL_SITE_URL = "https://social.ntpc.gov.tw"
WAIT_TIMEOUT = 5

"""
Helpers
"""


def request_with_cookie(url, cookies={}):
    """
    send HTTP requests with cookie set and get result
    """
    resp = requests.get(url, cookies=cookies, verify=False)
    return resp


def cookies_to_dict(cookies_list):
    """
    transform [{name: str, value: str, secure: bool}]
    to format {name: value...} dictionary
    """
    return {i['name']: i['value'] for i in cookies_list}


def build_query_url(userid=None, item_type_key=None):
    """
    userid := personal identificates
    item_type_key := lowIncome | mediumIncome | mediumIncomeOld |
                     unability | poorKid
    """

    QUERY_USER_URL = SOCIAL_SITE_URL + "/jsp/1/SWJ1111Querydata.jsp?\
where_str=&\
P_OBJID=&\
P_TBHEAD=&\
cmd=Query2&\
mycmd=2&\
status=undefined&\
userid={userid}&\
wfItem={item_type}&\
tableFlag=W11&\
app_date=&\
creatdt2=&\
paperno=&\
idno={userid}&\
loginID=A126348202&\
loginName=劉宇竤&\
loginDept=各區公所&\
prgno=1112&\
deptNo=1099&\
switchnum=undefined"

    item_type = {
        'lowIncome': "1001005",
        'mediumIncome': "1001007",
        'mediumIncomeOld': "1001010",
        'unability': "1001015",
        'poorKid': "1001020"
    }

    data = {
        'userid': userid,
        'item_type': item_type[item_type_key]
    }

    result_url = QUERY_USER_URL.format(**data)

    print "URL Built: %s" % result_url
    return result_url


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

def part2_findfileno(browser):
    """
    (Currently deprecated)
    Part 2.
    click query button manually, selenium might hang in this approach
    """
    raise NotImplementedError("method deprecated.")

    # directly go to query page
    browser.get(SOCIAL_SITE_URL + "/workspace.jsp?prgNo=1112")

    # document.frames[1].document.getElementById('txt10_IDNO')
    # switch to document.frames[1]
    content_frame = browser.find_element_by_id('content_frame')
    browser.switch_to_frame(content_frame)

    # look for query button
    applier_id_field = browser.find_element_by_id('txt10_IDNO')
    query_btn = browser.find_element_by_name('Query1')

    applier_id_field.send_keys(TEST_APPLIER_ID)
    query_btn.click()


def part2_queryfileno(browser):
    """
    Part 2.
    Query the file number directly
    """

    SCRIPT_DATA_SIZE = """
        document.title = grd88.rows(1).innerHTML;
    """
    # go to query page with parameters directly
    browser.get(build_query_url(TEST_APPLIER_ID, 'lowIncome'))

    # TODO: wait until query finished
    time.sleep(1)

    # use JavaScript to find out the first case and return by set title
    browser.execute_script(SCRIPT_DATA_SIZE)

    # use re to search which matches file number pattern
    html_contains_fileno = browser.title
    fileno = re.search(r'\>(\d{11})\&', html_contains_fileno).group(1)

    return fileno


def part3_file_upload(browser, file_number, upload_file_path):
    """
    Part 3.
    upload file via robot
    """

    def build_upload_interface_url(fileno):
        url_template = SOCIAL_SITE_URL + \
            "/jsp/SF/SWJSF92_2.jsp?prgNo=W1111&fileSno={fileno}&ctlbtn=0&returnButton=Y"
        return url_template.format(fileno=fileno)

    browser.get(build_upload_interface_url(file_number))

    # Traverse all checkboxes and find first not selected one for uploading.
    for fileIndex in range(5):
        checkboxName = 'checkboxKey%s' % fileIndex
        srcName = 'fileSrc%s' % fileIndex

        elem_checkbox = browser.get_element_by_name(checkboxName)
        elem_src = browser.get_element_by_name(srcName)

        if elem_checkbox.is_selected():
            continue
        else:
            # not selected, available for uploading
            elem_checkbox.click()
            elem_src.send_keys(upload_file_path)

    # submit the form
    elem_form = browser.get_element_by_id('FileForm')
    elem_form.submit()

    # TODO: check whether file has been uploaded


"""
Main function
"""


def main():
    browser = webdriver.Ie()  # ie only
    part1_login(browser)
    file_number = part2_queryfileno(browser)
    part3_file_upload(browser, file_number)


if __name__ == '__main__':
    main()
