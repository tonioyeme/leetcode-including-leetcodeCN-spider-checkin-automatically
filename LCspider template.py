import requests, urllib
from bs4 import BeautifulSoup
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import datetime

today_date_unix = time.mktime(datetime.date.today().timetuple())

"""open googlesheet"""
def open_sheet():
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('********.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key("********").sheet1
    return sheet

"""get data from leetcode website"""
def open_url(url, region):
    head = {'********'}
    req = urllib.request.Request(url, headers=head)
    response = urllib.request.urlopen(req)
    html = response.read()
    html_str = html.decode('utf-8')
    t = json.loads(html_str)

    if region == 'C':
        t = t['data']['recentSubmissions']
        t = [{k:v for k,v in x.items() if (int(x['submitTime']) >= today_date_unix and x['status'] == 'A_10')} for x in t]
    elif region == 'A':
        t = t['data']['recentSubmissionList']
        t = [{k:v for k,v in x.items() if (int(x['timestamp']) >= today_date_unix and x['statusDisplay'] == 'Accepted')} for x in t]

    ans = set()
    for x in t:
        if "title" in x:
            ans.add(x["title"])
        elif "question" in x:
            ans.add(x["question"]["title"])
    return ans


"""get leetcode name list from google sheet"""
ltcdnamelist = open_sheet().col_values(3)


"""generate user-specific leetcode links, and write into google sheet"""
for ltcdname in ltcdnamelist:
    ltcdnamecell = open_sheet().find(ltcdname)
    row_number = ltcdnamecell.row
    col_number = ltcdnamecell.col
    region = open_sheet().cell(row_number, col_number-2).value
    if region == 'A':
        url = "https://leetcode.com/graphql?oprationName=getRecentSubmissionList&variables={%22username%22:%22" + ltcdname + "%22}&query=query%20getRecentSubmissionList($username:%20String!,%20$limit:%20Int){recentSubmissionList(username:%20$username,%20limit:%20$limit){title%20titleSlug%20timestamp%20statusDisplay%20lang%20__typename%20}languageList{id%20name%20verboseName%20__typename}}"
    elif region == 'C':
        url = "https://leetcode-cn.com/graphql?oprationName=recentSubmissions&variables={%22userSlug%22:%22" + ltcdname + "%22}&query=query%20recentSubmissions($userSlug:%20String!){recentSubmissions(userSlug:%20$userSlug){status%20lang%20source{sourceType%20...%20on%20SubmissionSrcLeetbookNode{%20slug%20title%20pageId%20__typename}__typename}question{questionFrontendId%20title%20translatedTitle%20titleSlug%20__typename}submitTime%20__typename}}"
    
    #print(open_url(url))

    sheet = open_sheet()
    sheet.update_cell(row_number, col_number+1, len(open_url(url, region)))
    sheet.update_cell(row_number, col_number+2, str(open_url(url, region)))

















