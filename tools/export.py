#!/bin/env python

import pdfkit
import requests
import getpass
from BeautifulSoup import BeautifulSoup
import sys

user = sys.argv[2]
urlroot = sys.argv[1]
passwd = getpass.getpass()
auth=(user,passwd)

r=requests.get("%s/ringsheets"%urlroot, auth=auth, verify=False)
soup = BeautifulSoup(r.text)
for x in soup.findAll('a')[5:6]:
    path = x.get('href')
    print path
    options = {
    'page-size': 'Letter',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8",
    'username': user,
    'password': passwd,
    'zoom': '0.5'
    }
    pdfkit.from_url("%s/%s"%(urlroot,path), "out.pdf"  ,  options=options)
