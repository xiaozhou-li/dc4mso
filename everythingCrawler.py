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


personal_token = "" #New KDCode 20241105
token = os.getenv('GITHUB_TOKEN', personal_token)
headers = {'Authorization': f'token {token}'}

desired_width=640
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)
pd.set_option('display.max_columns',25)

def getAllRepos(theOrgName):
    theOrgQuery = f'https://api.github.com/orgs/{theOrgName}/repos'
    p_search = requests.get(theOrgQuery, headers=headers)
    org_info = p_search.json()
    return [x['full_name'] for x in org_info]

def getIssuesStartListbyProject(projectfullname):
    todayis = "20241105"
    theIssueQuery = f"https://api.github.com/repos/{projectfullname}/issues"
    #theProjectQuery = f"https://api.github.com/repos/{projectfullname}"
    #p_search = requests.get(theProjectQuery, headers=headers)
    #project_info = p_search.json()
    #project_id = project_info['id']
    params = {'per_page': 100, 'state': 'all'} #, 'state':'closed'
    page = 1
    #projectissuedataitems = []
    thefeatures = ['project_name', 'issue_number', 'author_id', 'created_at', 'closed_at',
                       'author_association', 'comments', 'labels', 'state', 'title', 'body']
    updateIssuetablename = '_'.join(projectfullname.split('/'))+'_issues_'+todayis+'.csv'
    with open(updateIssuetablename, 'a', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(thefeatures)
    while 1 == 1:
        params['page'] = page
        print(page)
        print(projectfullname + ' ' + 'page ' + str(page))
        theResult = requests.get(theIssueQuery, headers=headers, params=params)
        theItemListPerPage = theResult.json()
        if len(theItemListPerPage) == 0:
            break
        else:
            print(len(theItemListPerPage))
            for item in theItemListPerPage:
                issueitem = {}
                #issueitem['project_id'] = project_id
                #issueitem['commit_sha'] = item['sha']
                issueitem['project_name'] = projectfullname
                issueitem['issue_number'] = item['number']
                try:
                    issueitem['author_id'] = item['user']['login']
                except:
                    issueitem['author_id'] = np.NaN
                issueitem['created_at'] = item['created_at']
                try:
                    issueitem['closed_at'] = item['closed_at']
                except:
                    issueitem['closed_at'] = np.NaN
                issueitem['author_association'] = item['author_association']
                issueitem['comments'] = item['comments']
                issueitem['labels'] = len(item['labels'])
                issueitem['state'] = item['state']
                issueitem['title'] = item['title']
                issueitem['body'] = item['body']
                with open(updateIssuetablename, 'a', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile, delimiter=',')
                    writer.writerow([issueitem[x] for x in thefeatures])
                #projectissuedataitems.append(commititem)
            page = page + 1

#getIssuesStartListbyProject('spinnaker/spinnaker', '../KeyDevelopers/spinnaker_spinnaker_issues_20231107.csv')
#getIssuesTimelinesListbyProject('spinnaker/spinnaker', '../KeyDevelopers/spinnaker_spinnaker_issues_20231107.csv')


#repolist = getAllRepos('spinnaker')
#for repo in repolist:
#    getIssuesStartListbyProject(repo)

#df = pd.read_csv('spinnaker_clouddriver_issues_20240605.csv')
#print(df.shape)

def getCommitTablebyProject(projectfullname):
    theCommitQuery = f"https://api.github.com/repos/{projectfullname}/commits"
    theProjectQuery = f"https://api.github.com/repos/{projectfullname}"
    p_search = requests.get(theProjectQuery, headers=headers)
    project_info = p_search.json()
    project_id = project_info['id']
    params = {'per_page': 100}
    page = 1
    #projectissuedataitems = []
    todayis = "20241105"
    updateissuetablename = '_'.join(projectfullname.split('/'))+'_commits_'+todayis+'.csv'

    commit_features = ['project_name', 'commit_sha', 'author_email', 'author_date']
    with open(updateissuetablename, 'a', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(commit_features)
    while 1 == 1:
        params['page'] = page
        print(page)
        print(projectfullname + ' ' + 'page ' + str(page))
        theResult = requests.get(theCommitQuery, headers=headers, params=params)
        theItemListPerPage = theResult.json()
        if len(theItemListPerPage) == 0:
            break
        else:
            print(len(theItemListPerPage))
            for item in theItemListPerPage:
                commititem = {}
                commititem['project_name'] = projectfullname
                commititem['commit_sha'] = item['sha']
                try:
                    commititem['author_email'] = item['commit']['author']['email']
                except:
                    commititem['author_email'] = np.NaN
                commititem['author_date'] = item['commit']['author']['date']
                #try:
                #    commititem['message'] = item['commit']['message']
                #except:
                #    commititem['message'] = np.NaN

                with open(updateissuetablename, 'a', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile, delimiter=',')
                    writer.writerow([commititem[x] for x in commit_features])
                #projectissuedataitems.append(commititem)
            page = page + 1

#repolist = getAllRepos('spinnaker')
#for repo in repolist:
#    getCommitTablebyProject(repo)

def furtherCrawlCommits(commitsdf, newupdateissuetablename):
    commitsshalist = commitsdf.loc[:, ['commit_sha', 'project_name']].values.tolist()
    commit_features = ['project', 'commit_sha', 'author_email', 'author_date', 'file_sha', 'filename', 'status', 'additions', 'deletions', 'previous_filename']

    with open(newupdateissuetablename, 'a', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(commit_features)

    for sha in commitsshalist:
        print(sha)
        projectfullname = sha[1]
        theCommitQuery = f"https://api.github.com/repos/{sha[1]}/commits/{sha[0]}"
        #theProjectQuery = f"https://api.github.com/repos/{projectfullname}"
        commit_search = requests.get(theCommitQuery, headers=headers)
        commit_info = commit_search.json()
        #project_id = project_info['id']
        #params = {'per_page': 100}
        #page = 1
        print(commit_info)
        commititem = {}
        commititem['project'] = sha[1]
        commititem['commit_sha'] = sha[0]
        try:
            commititem['author_email'] = commit_info['commit']['author']['email']
        except:
            commititem['author_email'] = np.NaN
        try:
            commititem['author_date'] = commit_info['commit']['author']['date']
        except:
            commititem['author_date'] = np.NaN
        thefiles = commit_info['files']
        for file in thefiles:
            commititemFile = commititem.copy()
            commititemFile['file_sha'] = file['sha']
            commititemFile['filename'] = file['filename']
            commititemFile['status'] = file['status']
            commititemFile['additions'] = file['additions']
            commititemFile['deletions'] = file['deletions']
            #commititemFile['contents_url'] = file['contents_url']
            #try:
            #    commititemFile['patch'] = file['patch']
            #except:
            #    commititemFile['patch'] = np.NaN
            try:
                commititemFile['previous_filename'] = file['previous_filename']
            except:
                commititemFile['previous_filename'] = np.NaN
            with open(newupdateissuetablename, 'a', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow([commititemFile[x] for x in commit_features])

def furtherCrawlCommitsContinuefromBreak(commitsdf, newupdateissuetablename, startpoint):
    commitsshalist = commitsdf.loc[:, ['commit_sha', 'project_name']].values.tolist()
    commit_features = ['project', 'commit_sha', 'author_email', 'author_date', 'file_sha', 'filename', 'status', 'additions', 'deletions', 'previous_filename']

    with open(newupdateissuetablename, 'a', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(commit_features)

    for sha in commitsshalist[startpoint:]:
        print(sha)
        projectfullname = sha[1]
        theCommitQuery = f"https://api.github.com/repos/{sha[1]}/commits/{sha[0]}"
        #theProjectQuery = f"https://api.github.com/repos/{projectfullname}"
        commit_search = requests.get(theCommitQuery, headers=headers)
        commit_info = commit_search.json()
        #project_id = project_info['id']
        #params = {'per_page': 100}
        #page = 1
        print(commit_info)
        commititem = {}
        commititem['project'] = sha[1]
        commititem['commit_sha'] = sha[0]
        try:
            commititem['author_email'] = commit_info['commit']['author']['email']
        except:
            commititem['author_email'] = np.NaN
        try:
            commititem['author_date'] = commit_info['commit']['author']['date']
        except:
            commititem['author_date'] = np.NaN
        thefiles = commit_info['files']
        for file in thefiles:
            commititemFile = commititem.copy()
            commititemFile['file_sha'] = file['sha']
            commititemFile['filename'] = file['filename']
            commititemFile['status'] = file['status']
            commititemFile['additions'] = file['additions']
            commititemFile['deletions'] = file['deletions']
            #commititemFile['contents_url'] = file['contents_url']
            #try:
            #    commititemFile['patch'] = file['patch']
            #except:
            #    commititemFile['patch'] = np.NaN
            try:
                commititemFile['previous_filename'] = file['previous_filename']
            except:
                commititemFile['previous_filename'] = np.NaN
            with open(newupdateissuetablename, 'a', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow([commititemFile[x] for x in commit_features])

#all_issues_files = glob.glob("../KeyDevelopers/*_issues_20240605.csv")
#df_all_issues = pd.concat((pd.read_csv(f) for f in all_issues_files), ignore_index=True)
#df_all_issues.to_csv('../KeyDevelopers/spinnaker_all_issues_20240605.csv', index=False)

#all_issues_files = glob.glob("../KeyDevelopers/*_commits_20240605.csv")
#df_all_issues = pd.concat((pd.read_csv(f) for f in all_issues_files), ignore_index=True)
#df_all_issues.to_csv('../KeyDevelopers/spinnaker_all_commits_20240605.csv', index=False)

#df_commits = pd.read_csv("spinnaker_all_commits_20240605.csv")
#furtherCrawlCommits(df_commits, "spinnaker_all_commits_20240605_detailed.csv")
#furtherCrawlCommitsContinuefromBreak(df_commits, "spinnaker_all_commits_20240605_detailed.csv", 48193)


def getIssuesTimelinesListbyProject(theissuedf, savefilename):
    issueshalist = theissuedf.loc[:, ['issue_number', 'project_name']].values.tolist()
    issuefeatures = ['project_name','issue_number','created_at','updated_at','commit_sha','event',
                     'author_email','author_login','actor_type','comment_body','commit_msg','review_requester',
                     'requested_reviewer','commit_date','review_submitted_at','cross-referenced_issue_number',
                     'referenced_commit_id','label_name','label_color']

    with open(savefilename, 'a', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(issuefeatures)
    for issue in issueshalist:
        print(issue)
        projectfullname = issue[1]
        issuenumber = issue[0]
        theissuetimelineurl = f"https://api.github.com/repos/{projectfullname}/issues/{issuenumber}/timeline"
        params = {'per_page': 100}
        page = 1
        while 1 == 1:
            params['page'] = page
            theResult = requests.get(theissuetimelineurl, headers=headers, params=params)
            theissuetimelinePerPage = theResult.json()
            if len(theissuetimelinePerPage) == 0:
                break
            else:
                #print(len(theissuetimelinePerPage))
                for item in theissuetimelinePerPage:
                    timelineitem = {}
                    timelineitem['project_name'] = issue[1]
                    timelineitem['issue_number'] = issue[0]
                    try:
                        timelineitem['created_at'] = item['created_at']
                    except:
                        timelineitem['created_at'] = np.NaN
                    try:
                        timelineitem['updated_at'] = item['updated_at']
                    except:
                        timelineitem['updated_at'] = np.NaN
                    try:
                        timelineitem['commit_sha'] = item['sha']
                    except:
                        timelineitem['commit_sha'] = np.NaN
                    try:
                        timelineitem['event'] = item['event']
                    except:
                        timelineitem['event'] = np.NaN
                    try:
                        timelineitem['author_email'] = item['author']['email']
                    except:
                        timelineitem['author_email'] = np.NaN
                    try:
                        timelineitem['author_login'] = item['actor']['login']
                    except:
                        timelineitem['author_login'] = np.NaN
                    try:
                        timelineitem['actor_type'] = item['actor']['type']
                    except:
                        timelineitem['actor_type'] = np.NaN
                    try:
                        timelineitem['comment_body'] = item['body']
                    except:
                        timelineitem['comment_body'] = np.NaN
                    try:
                        timelineitem['commit_msg'] = item['message']
                    except:
                        timelineitem['commit_msg'] = np.NaN
                    try:
                        timelineitem['review_requester'] = item['review_requester']['login']
                    except:
                        timelineitem['review_requester'] = np.NaN
                    try:
                        timelineitem['requested_reviewer'] = item['requested_reviewer']['login']
                    except:
                        timelineitem['requested_reviewer'] = np.NaN
                    try:
                        timelineitem['commit_date'] = item['author']['date']
                    except:
                        timelineitem['commit_date'] = np.NaN
                    try:
                        timelineitem['review_submitted_at'] = item['submitted_at']
                    except:
                        timelineitem['review_submitted_at'] = np.NaN
                    try:
                        timelineitem['cross-referenced_issue_number'] = item['source']['issue']['number']
                    except:
                        timelineitem['cross-referenced_issue_number'] = np.NaN
                    try:
                        timelineitem['referenced_commit_id'] = item['commit_id']
                    except:
                        timelineitem['referenced_commit_id'] = np.NaN
                    try:
                        timelineitem['label_name'] = item['label']['name']
                    except:
                        timelineitem['label_name'] = np.NaN
                    try:
                        timelineitem['label_color'] = item['label']['color']
                    except:
                        timelineitem['label_color'] = np.NaN
                    with open(savefilename, 'a', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile, delimiter=',')
                        writer.writerow([timelineitem[x] for x in issuefeatures])
                page = page + 1

def getIssuesTimelinesListbyProjectContinue(theissuedf, savefilename, startpoint):
    issueshalist = theissuedf.loc[:, ['issue_number', 'project_name']].values.tolist()
    issuefeatures = ['project_name','issue_number','created_at','updated_at','commit_sha','event',
                     'author_email','author_login','actor_type','comment_body','commit_msg','review_requester',
                     'requested_reviewer','commit_date','review_submitted_at','cross-referenced_issue_number',
                     'referenced_commit_id','label_name','label_color']
    #with open(savefilename, 'a', encoding='utf-8') as csvfile:
    #    writer = csv.writer(csvfile, delimiter=',')
    #    writer.writerow(issuefeatures)
    for issue in issueshalist[startpoint:]:
        print(issue)
        projectfullname = issue[1]
        issuenumber = issue[0]
        theissuetimelineurl = f"https://api.github.com/repos/{projectfullname}/issues/{issuenumber}/timeline"
        params = {'per_page': 100}
        page = 1
        while 1 == 1:
            params['page'] = page
            theResult = requests.get(theissuetimelineurl, headers=headers, params=params)
            theissuetimelinePerPage = theResult.json()
            if len(theissuetimelinePerPage) == 0:
                break
            #elif theissuetimelinePerPage['status'] == '403':
            #    break
            else:
                try:
                    if theissuetimelinePerPage['status'] == '403':
                        break
                except:
                    pass
                for item in theissuetimelinePerPage:
                    timelineitem = {}
                    timelineitem['project_name'] = issue[1]
                    timelineitem['issue_number'] = issue[0]
                    try:
                        timelineitem['created_at'] = item['created_at']
                    except:
                        timelineitem['created_at'] = np.NaN
                    try:
                        timelineitem['updated_at'] = item['updated_at']
                    except:
                        timelineitem['updated_at'] = np.NaN
                    try:
                        timelineitem['commit_sha'] = item['sha']
                    except:
                        timelineitem['commit_sha'] = np.NaN
                    try:
                        timelineitem['event'] = item['event']
                    except:
                        timelineitem['event'] = np.NaN
                    try:
                        timelineitem['author_email'] = item['author']['email']
                    except:
                        timelineitem['author_email'] = np.NaN
                    try:
                        timelineitem['author_login'] = item['actor']['login']
                    except:
                        timelineitem['author_login'] = np.NaN
                    try:
                        timelineitem['actor_type'] = item['actor']['type']
                    except:
                        timelineitem['actor_type'] = np.NaN
                    try:
                        timelineitem['comment_body'] = item['body']
                    except:
                        timelineitem['comment_body'] = np.NaN
                    try:
                        timelineitem['commit_msg'] = item['message']
                    except:
                        timelineitem['commit_msg'] = np.NaN
                    try:
                        timelineitem['review_requester'] = item['review_requester']['login']
                    except:
                        timelineitem['review_requester'] = np.NaN
                    try:
                        timelineitem['requested_reviewer'] = item['requested_reviewer']['login']
                    except:
                        timelineitem['requested_reviewer'] = np.NaN
                    try:
                        timelineitem['commit_date'] = item['author']['date']
                    except:
                        timelineitem['commit_date'] = np.NaN
                    try:
                        timelineitem['review_submitted_at'] = item['submitted_at']
                    except:
                        timelineitem['review_submitted_at'] = np.NaN
                    try:
                        timelineitem['cross-referenced_issue_number'] = item['source']['issue']['number']
                    except:
                        timelineitem['cross-referenced_issue_number'] = np.NaN
                    try:
                        timelineitem['referenced_commit_id'] = item['commit_id']
                    except:
                        timelineitem['referenced_commit_id'] = np.NaN
                    try:
                        timelineitem['label_name'] = item['label']['name']
                    except:
                        timelineitem['label_name'] = np.NaN
                    try:
                        timelineitem['label_color'] = item['label']['color']
                    except:
                        timelineitem['label_color'] = np.NaN
                    with open(savefilename, 'a', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile, delimiter=',')
                        writer.writerow([timelineitem[x] for x in issuefeatures])
                page = page + 1




#df_done = pd.read_csv("spinnaker_all_issues_20240605_timeline_part1_new.csv")
#df_issues['theid'] = df_issues['project_name']+df_issues['issue_number'].apply(str)
#df_done['theid'] = df_done['project_name']+df_done['issue_number'].apply(str)

#donelist = df_done['theid'].values.tolist()
#df_issues_undone = df_issues.loc[~df_issues['theid'].isin(donelist),:]
#print(df_issues_undone.shape)
#df_issues=df_issues.loc[:, ['project_name','issue_number']]
#df_issues=df_issues.drop_duplicates()
#print(df_issues.shape)
#df_issues.to_csv("spinnaker_all_issues_20240605_oldleft_.csv", index=False)
#df_done = df_done.loc[:, ['project_name','issue_number']]
#df_done=df_done.drop_duplicates()
#print(df_done.shape)
#print(df_issues.shape)
#df_issues_undone.to_csv("spinnaker_all_issues_20240605_undone.csv", index=False)

#df_issues=df_issues.loc[:, ['project_name','issue_number']]
#df_issues.to_csv("spinnaker_all_issues_20240605_thecount_new.csv", index=False)

#df_issues= pd.read_csv('spinnaker_all_issues_20240605_new.csv')
#print(df_issues.shape)
#df_tl1 = pd.read_csv('spinnaker_all_issues_20240605_timeline_part1_new.csv')
#df_tl2 = pd.read_csv('spinnaker_all_issues_20240605_timeline_part2_new.csv')
#df_tl1=df_tl1.loc[:, ['project_name','issue_number']]
#df_tl1=df_tl1.drop_duplicates()
#df_tl2=df_tl2.loc[:, ['project_name','issue_number']]
#df_tl2=df_tl2.drop_duplicates()
#df_done = pd.concat([df_tl1,df_tl2])
#print(df_done.shape)
#df_done=df_done.drop_duplicates()
#print(df_done.shape)
#df_done['theid'] = df_done['project_name']+df_done['issue_number'].apply(str)
#df_issues['theid'] = df_issues['project_name']+df_issues['issue_number'].apply(str)
#donelist = df_done['theid'].values.tolist()
#df_issues = df_issues.loc[~df_issues['theid'].isin(donelist),:]
#df_issues.to_csv('spinnaker_all_issues_20240605_stillstillundone.csv', index=False)
#print(df_done.shape)
#print(df_tl1.shape)
#print(df_tl2.shape)
#df_done.to_csv('spinnaker_all_issues_timelines_final.csv',index=False)
#df_issues= pd.read_csv('spinnaker_all_issues_20240605_stillstillundone.csv')
#getIssuesTimelinesListbyProjectContinue(df_issues, "spinnaker_all_issues_20240605_timeline_part2_new.csv",0)
#df_issues=df_issues.loc[:, ['project_name','issue_number']]
#df_issues.to_csv("spinnaker_all_issues_20240605_thecount_new_stillundone.csv", index=False)
def mapauthorloginemail(thedf, savefilename):
    emaillist = thedf.loc[:, 'author_email'].values.tolist()
    emaillist = list(set(emaillist))
    emaillist = [x for x in emaillist if "root@" not in str(x)]
    emaillist = [str(x) for x in emaillist]

    #with open(savefilename, 'a', encoding='utf-8') as csvfile:
    #    writer = csv.writer(csvfile, delimiter=',')
    #    writer.writerow(['author_email', 'author_login', 'author_name'])

    for item in emaillist[1337:]:
        commitlist = df.loc[df['author_email'] == str(item), ['project_name', 'commit_sha']].values.tolist()
        projectfullname = commitlist[0][0]
        commitsha = commitlist[0][1]
        singlecommiturl = f"https://api.github.com/repos/{projectfullname}/commits/{commitsha}"
        theResult = requests.get(singlecommiturl, headers=headers)
        theresultjson = theResult.json()
        pprint(theresultjson)
        developerline = {}
        try:
            developerline['author_email'] = item
        except:
            developerline['author_email'] = np.NaN
        try:
            developerline['author_login'] = theresultjson['author']['login']
        except:
            developerline['author_login'] = np.NaN
        try:
            developerline['author_name'] = theresultjson['commit']['author']['name']
        except:
            developerline['author_name'] = np.NaN
        with open(savefilename, 'a', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow([developerline[x] for x in ['author_email', 'author_login', 'author_name']])

df = pd.read_csv('spinnaker_all_issues_timelines_final.csv')

def mapauthorloginemailfromlogin(thedf, savefilename):
    thedf = thedf.loc[~thedf['author_login'].isnull(), :]
    loginlist = thedf.loc[:, 'author_login'].values.tolist()
    loginlist = [str(x) for x in loginlist]
    loginlist = list(set(loginlist))
    print(len(loginlist))

    with open(savefilename, 'a', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['author_email', 'author_login', 'author_name'])

    for item in loginlist:
        userurl = f"https://api.github.com/users/{item}"
        theResult = requests.get(userurl, headers=headers)
        theresultjson = theResult.json()
        #pprint(theresultjson)
        developerline = {}
        try:
            developerline['author_email'] = theresultjson['email']
        except:
            developerline['author_email'] = np.NaN
        try:
            developerline['author_login'] = item
        except:
            developerline['author_login'] = np.NaN
        try:
            developerline['author_name'] = theresultjson['name']
        except:
            developerline['author_name'] = np.NaN
        with open(savefilename, 'a', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow([developerline[x] for x in ['author_email', 'author_login', 'author_name']])

#df_login = pd.read_csv("logincheck.csv")
#df_email = pd.read_csv("emailcheck.csv")
#result = pd.merge(df_login, df_email, on='author_name', how='right')
#result.to_csv("merged.csv", index=False)

#df = pd.read_csv('spinnaker_all_commits_20240605_detailed.csv')
#print(df.head())
#print(df.shape)
#df = df.loc[(~df['author_login_x'].isnull() & ~df['author_login_y'].isnull()),:]
#thelist = df.loc[:, ['author_login_x', 'author_login_y']].values.tolist()
#thelist = [x for x in thelist if x[0]!=x[1]]
#services = ['deck', 'gate', 'orca', 'clouddriver', 'front50', 'rosco', 'igor', 'echo', 'fiat', 'kayenta', 'keel', 'halyard']
#testing =['clouddriver']
#services = ['spinnaker/'+str(x) for x in services]
#df_services = df.loc[df['project_name'].isin(services)]
#print(df_services.head())
#print(df_services.shape)

#getCommitTablebyProject("geoserver/geoserver-cloud")
#df = pd.read_csv('geoserver_geoserver-cloud_commits_20240605.csv')
#furtherCrawlCommits(df,'geoserver_geoserver-cloud_commits_20240605_detailed.csv')


##############################################################################
##############################################################################
#getCommitTablebyProject("dotnet-architecture/eShopOnContainers")
#df = pd.read_csv('dotnet_eShop_commits_20241105.csv')
#furtherCrawlCommits(df,'dotnet_eShop_commits_20241105_detailed.csv')
#df = pd.read_csv('dotnet-architecture_eShopOnContainers_commits_20241105.csv')
#furtherCrawlCommits(df,'dotnet-architecture_eShopOnContainers_commits_20241105_detailed.csv')

#getIssuesStartListbyProject('dotnet/eShop')
#df = pd.read_csv('dotnet_eShop_issues_20241105.csv')
#getIssuesTimelinesListbyProject(df, 'dotnet_eShop_issues_timeline_20241105.csv')
#df_index = df.loc[:, ['project_name', 'issue_number', 'author_id']]
#df_index.to_csv('dotnet-architecture_eShopOnContainers_issues_index_20241105.csv', index=False)
#getIssuesTimelinesListbyProjectContinue(df, 'dotnet-architecture_eShopOnContainers_issues_timeline_20241105.csv', 1383)
##############################################################################
##############################################################################

df = pd.read_csv('')
print(df.head())