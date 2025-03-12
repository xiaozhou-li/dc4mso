import os
from pprint import pprint
import requests
import pandas as pd
import numpy as np
import time
import csv, json
from matplotlib import pyplot as plt
import glob
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme()


personal_token = ""
token = os.getenv('GITHUB_TOKEN', personal_token)
headers = {'Authorization': f'token {token}'}

desired_width=640
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)
pd.set_option('display.max_columns',25)

def reshapeResultIntoCSV(projectname, thetxt, newcsvfile):
    with open(thetxt) as thetxtfile:
        linelist = [x.strip('\n') for x in thetxtfile.readlines()]
    thewholestring = ''.join(linelist)
    #thecontent = thewholestring.replace("'", '"')
    #print(thecontent)
    #json_object = json.loads(thecontent)
    #print(json_object)
    thelistofitems = [x for x in thewholestring.split('datetime.datetime')]
    thelistofitems = thelistofitems[1:]
    with open(newcsvfile, 'a', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['projectname','author_name','datetime','role','value'])
    for item in thelistofitems:
        thedatetime = item.split(', 999999): ')[0].strip('(')
        thedatetimeformatted = '-'.join(thedatetime.split(', ')[:3]) + ' ' + ':'.join(thedatetime.split(', ')[-3:])
        thedatetimeformatteddt = pd.to_datetime(thedatetimeformatted)
        # print(thedatetimeformatteddt)
        thecontent = item.split(', 999999): ')[1].strip().rstrip(',')
        thecontent = thecontent.replace("'", '"')
        json_object = json.loads(thecontent)
        developerlist = json_object['developers']
        keydeveloperlist = []
        for key in ['connectors','jacks','mavens']:
            thedict = json_object[key]
            for thekeydeveloper in thedict.keys():
                keydeveloperlist.append(thekeydeveloper)
                with open(newcsvfile, 'a', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile, delimiter=',')
                    writer.writerow([projectname, thekeydeveloper, thedatetimeformatteddt, key, thedict[thekeydeveloper]])
        #pprint(json_object)

reshapeResultIntoCSV('spinnaker/rosco', 'rosco.txt', 'rosco_developer.csv')