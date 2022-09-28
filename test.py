#Project to extract youtube comments from seached text and filter doubts of students
import time
import requests
from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
from googleapiclient.discovery import build
import pandas as pd
from bs4 import BeautifulSoup
import re
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import  WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")
@app.route('/comments',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def ytlist_of_urls():
    search=request.form["content"]
    search=search.replace(" ","+")
    x="https://www.youtube.com/results?search_query="+search

    #headers = {
        #'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
    #}#this is optional for cases where the site does not allow scrapping

    page = requests.get(x).text

    beauty=BeautifulSoup(page,"html.parser")
    #print(beauty)
    url_find=beauty.find_all("script")
    stdic=url_find[33].text
    dict_object = json.loads(re.search('var ytInitialData = (.+)[,;]{1}',str(stdic)).group(1))
    d=dict_object['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
    list_url=[]
    for i in range(len(d)-1):
        if list(d[i].keys())[0]=='videoRenderer':
            list_url.append("https://www.youtube.com/watch?v="+d[i]['videoRenderer']['videoId'])
    comment_list=ytcomments(list_url)
    return render_template("results.html",comments=comment_list[0:len(comment_list)])


    # Put api key with your own.
Api_Key = "AIzaSyCbObbUVs3fNCXVJPlKxT-Sh1vBTuhSMP0"

youtube = build('youtube', 'v3', developerKey=Api_Key)
    # Put Any YouTube video ID.
ID = "glDU96h8A48"
List = [['Name', 'Comment', 'Likes', 'time']]


def scrape_all_with_replies():
    data = youtube.commentThreads().list(part='snippet', videoId=ID, maxResults='100',
                                         textFormat="plainText").execute()
    for i in data["items"]:
        name = i["snippet"]['topLevelComment']["snippet"]["authorDisplayName"]
        comment = i["snippet"]['topLevelComment']["snippet"]["textDisplay"]
        likes = i["snippet"]['topLevelComment']["snippet"]['likeCount']
        published_at = i["snippet"]['topLevelComment']["snippet"]['publishedAt']
        List.append([name, comment, likes, published_at])
    while ("nextPageToken" in data):
        data = youtube.commentThreads().list(part='snippet', videoId=ID, pageToken=data["nextPageToken"],
                                             maxResults='100', textFormat="plainText").execute()
        for i in data["items"]:
            name = i["snippet"]['topLevelComment']["snippet"]["authorDisplayName"]
            comment = i["snippet"]['topLevelComment']["snippet"]["textDisplay"]
            likes = i["snippet"]['topLevelComment']["snippet"]['likeCount']
            published_at = i["snippet"]['topLevelComment']["snippet"]['publishedAt']
            List.append([name, comment, likes, published_at])
    df = pd.DataFrame({'Name': [i[0] for i in List], 'Comment': [i[1] for i in List], 'Likes': [i[2] for i in List],
                       'Time': [i[3] for i in List]})
    df.to_csv('YT-Scrape-Result.csv', index=False, header=False)
    return "Successful! Check the CSV file that you have just created."

    #diction={"comments":data,"url":lurl}
    #df1=pd.DataFrame(diction)
    #df1.to_csv(r"C:\Users\dell\Documents\search.csv")
#l1=ytlist_of_urls()
#l2=["youtube.com/watch?v=4c0CLUER6nw"]
#ytcomments(l2)
scrape_all_with_replies()
"""if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8001, debug=True)
"""