# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

import re
import sys

from helpers import cookies_to_dict, build_query_url, build_upload_interface_url
from settings import SOCIAL_SITE_URL, WAIT_TIMEOUT
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


def part2_queryfileno(browser):
    """
    Part 2.
    Query the file number directly
    """
    script_file_num = """
        document.title = grd88.rows.length - 1;
    """

    script_get_first_row = """
        document.title = grd88.rows(1).innerHTML;
    """
    # go to query page with parameters directly
    browser.get(build_query_url(TEST_APPLIER_ID, UPLOAD_TYPE))

    # check the number of applier's files
    browser.execute_script(script_file_num)
    file_number = browser.title
    print 'Detected file number: %s' % file_number

    if file_number < 1:
        raise NoFileFoundException("Target doesn't have any file.")

    # use JavaScript to find out the first case and return by set title
    browser.execute_script(script_get_first_row)

    # use re to search which matches file number pattern
    html_contains_fileno = browser.title
    fileno = re.search(r'\>(\d{11})\&', html_contains_fileno).group(1)

    return fileno


def part3_file_upload(browser, file_number, upload_file_path):
    """
    Part 3.
    upload file via robot
    """

    browser.get(build_upload_interface_url(file_number))

    # Traverse all checkboxes and find first not selected one for uploading.
    for fileIndex in range(5):
        print 'try upload box %s ...' % fileIndex
        checkboxName = 'checkboxKey%s' % fileIndex
        srcName = 'fileSrc%s' % fileIndex

        elem_checkbox = browser.find_element_by_name(checkboxName)
        elem_src = browser.find_element_by_name(srcName)

        if elem_checkbox.is_selected():
            print 'upload box selected, skip to the next one'
            continue
        else:
            # not selected, available for uploading
            elem_checkbox.click()
            elem_src.send_keys(upload_file_path)
            break

    # submit the form
    sys.exit(1) # currently not submit the form
    elem_form = browser.find_element_by_id('FileForm')
    elem_form.submit()

    # TODO: check whether file has been uploaded


def main():
    browser = webdriver.Ie()  # ie only
    part1_login(browser)
    file_number = part2_queryfileno(browser)
    part3_file_upload(browser, file_number, "C:\\RHDSetup.log")


if __name__ == '__main__':
    main()
