# -*- coding: utf-8 -*-
import requests

from settings import SOCIAL_SITE_URL
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

    query_user_url = SOCIAL_SITE_URL + "/jsp/1/SWJ1111Querydata.jsp?\
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

    result_url = query_user_url.format(**data)

    return result_url

