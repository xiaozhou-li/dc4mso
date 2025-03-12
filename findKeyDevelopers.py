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

df = pd.read_csv('spinnaker_all_issues_timelines_final.csv')
df_reviewed = df.loc[df['event']=='reviewed', :]
print(df_reviewed.head())
print(df_reviewed.shape)

def getreviewedUsers(thedf, theservice, updateissuetablename):
    df_selected = thedf.loc[(thedf['project_name']==theservice) & (thedf['event'] == 'reviewed'), :]
    thereviewedissuelist = df_selected.loc[:, 'issue_number'].values.tolist()
    #user_loginlist = []
    for issuenumber in thereviewedissuelist[1001:]:
        issuetimelineurl = f'https://api.github.com/repos/{theservice}/issues/{issuenumber}/timeline'
        p_search = requests.get(issuetimelineurl, headers=headers)
        issueinfo = p_search.json()
        #user_loginlist.append([x for x in issueinfo if x['event'] == 'reviewed'][0]['user']['login'])
        print([x for x in issueinfo if x['event'] == 'reviewed'][0]['user']['login'])
        with open("user_reviewed.txt", "a") as text_file:
            text_file.writelines([x for x in issueinfo if x['event'] == 'reviewed'][0]['user']['login']+'\n')
    #df_selected['author_login'] = user_loginlist
    #df_selected.to_csv(updateissuetablename, index=False)

getreviewedUsers(df, 'spinnaker/clouddriver', 'testing_clouddriver_reviewed.csv')
