# -*- coding: utf-8 -*-
import requests

from io import StringIO
from settings import SOCIAL_SITE_URL
"""
Helpers
"""
def convert_query_result_to_dict(html_code, encoding='big5'):
    """
    Convert the query result into a Python dictionary in order to read all data in table

    This returns a dictionary which contains query result data.
    """
    import lxml
    from lxml import etree
    from lxml import cssselect

    # make selectors here
    tr_select = cssselect.CSSSelector("tr")
    td_select = cssselect.CSSSelector("td")

    # get html_tree
    html_parser = etree.HTMLParser()
    try:
        html_string = StringIO(html_code.decode(encoding))
    except UnicodeEncodeError:
        html_string = StringIO(html_code)
    html_tree = etree.parse(html_string, html_parser)

    # get all rows
    trs = tr_select(html_tree)

    # deal with keys, first row
    th = trs[0]
    keys = [td.text for td in td_select(th)]

    # deal with values, the other rows
    result = []

    trs = trs[1:]
    for tr in trs:
        tds = td_select(tr)
        new_data = {}
        for idx in range(len(tds)):
            new_data[keys[idx]] = tds[idx].text

        result.append(new_data)

    return result


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


def build_upload_interface_url(fileno):
    url_template = SOCIAL_SITE_URL + \
        "/jsp/SF/SWJSF92_2.jsp?prgNo=W1111&fileSno={fileno}&ctlbtn=0&returnButton=Y"
    return url_template.format(fileno=fileno)


def build_query_url(userid=None, item_type_key=None):
    """
    userid := personal identificates
    item_type_key := lowIncome | mediumIncome | mediumIncomeOld |
                     disability | poorKid
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
tableFlag={table_flag}&\
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

    item_type_ids = {
        'lowIncome': "1001005",
        'mediumIncome': "1001007",
        'mediumIncomeOld': "1001010",
        'disability': "1001015",
        'poorKid': "1001020"
    }
    item_type_id = item_type_ids[item_type_key]

    table_flags = {
        '1001005': 'W11',
        '1001010': 'W21',
        '1001015': 'W31',
        '1001020': 'W41',
        '1001007': 'WA1'
    }

    data = {
        'userid': userid,
        'item_type': item_type_id,
        'table_flag': table_flags[item_type_id]
    }

    result_url = query_user_url.format(**data)

    return result_url

def extract_id_from_filename(file_path):
    import os
    import re

    filename = os.path.basename(file_path)

    return re.search(r"[A-Z]\d{9}", filename).group(0)


if __name__ == '__main__':
    import pprint
    class MyPP(pprint.PrettyPrinter):
        def format(self, object, context, maxlevels, level):
            ret = pprint.PrettyPrinter.format(self, object, context, maxlevels, level)
            if isinstance(object, unicode):
                ret = ('"'+ object.encode('utf-8') + '"', ret[1], ret[2])
            return ret
    mypp = MyPP()
    mypp.pprint(convert_query_result_to_dict(open('./test_resource/query_sample.html').read()))
                                        
