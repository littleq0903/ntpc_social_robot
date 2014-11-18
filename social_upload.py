
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import time
import sys
import requests
import re

from social_credentials import LOGIN_USERNAME, LOGIN_PASSWORD
from social_testcases import TEST_APPLIER_ID, TEST_UPLOAD_FILE

"""
Helpers
"""


def request_with_cookie(url, cookies={}):
    resp = requests.get(url, cookies=cookies, verify=False)
    return resp


def cookies_to_dict(cookies_list):
    return {i['name']: i['value'] for i in cookies_list}


def build_query_url(userid=None, item_type_key=None):
    """
    userid := personal identificates
    item_type_key := lowIncome | mediumIncome | mediumIncomeOld | unability | poorKid
    """

    QUERY_USER_URL = "https://social.ntpc.gov.tw/jsp/1/SWJ1111Querydata.jsp?\
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

    browser.get('http://social.ntpc.gov.tw')

    username_input = browser.find_element_by_id('username')
    password_input = browser.find_element_by_id('password')

    username_input.send_keys(LOGIN_USERNAME)
    password_input.send_keys(LOGIN_PASSWORD + Keys.RETURN)

    time.sleep(1)  # TODO: listen to 'done' event'

    # cookies = browser.get_cookies()
    # print type(cookies)
    # print cookies

    # response_data = request_with_cookie(
    #     build_query_url(TEST_APPLIER_ID, 'lowIncome'),
    #     cookies=cookies_to_dict(cookies))
    # print response_data


def part2_findfileno(browser):
    """
    Part 2.
    Get to the form and find file no. by user idenficates
    """

    # directly go to query page
    browser.get("https://social.ntpc.gov.tw/workspace.jsp?prgNo=1112")

    # TODO: document.frames[1].document.getElementById('txt10_IDNO')
    content_frame = browser.find_element_by_id('content_frame')
    browser.switch_to_frame(content_frame)

    applier_id_field = browser.find_element_by_id('txt10_IDNO')
    query_btn = browser.find_element_by_name('Query1')

    time.sleep(1)  # TODO: listen to 'done' event

    applier_id_field.send_keys(TEST_APPLIER_ID)
    query_btn.click()


def part2_queryfileno(browser):
    """
    Part 2.
    Query the file no directly
    """

    SCRIPT_DATA_SIZE = """
        document.title = grd88.rows(1).innerHTML;
    """
    browser.get(build_query_url(TEST_APPLIER_ID, 'lowIncome'))

    time.sleep(1)

    browser.execute_script(SCRIPT_DATA_SIZE)
    html_contains_fileno = browser.title

    fileno = re.search(r'\>(\d{11})\&', html_contains_fileno).group(1)

    return fileno

"""
Main function
"""
def main():
    browser = webdriver.Ie()  # ie only
    part1_login(browser)
    part2_queryfileno(browser)

if __name__ == '__main__':
    main()
