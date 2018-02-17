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
for x in soup.findAll('a')[5:]:
    path = x.get('href')
    print path
    filename = path.replace('/','_').replace('?','_').replace('&','_').replace('=','_')
    options = {
    'page-size': 'Letter',
    'margin-top': '0.5in',
    'margin-right': '0.5in',
    'margin-bottom': '0.5in',
    'margin-left': '0.5in',
    'encoding': "UTF-8",
    'username': user,
    'password': passwd,
    'zoom': '.9'
    }
    pdfkit.from_url("%s/%s"%(urlroot,path), "%s.pdf"%filename  ,  options=options)
