#Project to extract youtube comments from seached text and filter doubts of students
import requests
import logging
from googleapiclient.discovery import build
from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
#import pandas as pd
from bs4 import BeautifulSoup
import re
import json

Api_Key = "AIzaSyCbObbUVs3fNCXVJPlKxT-Sh1vBTuhSMP0"
youtube = build('youtube', 'v3', developerKey=Api_Key)
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

    page = requests.get(x).text

    beauty=BeautifulSoup(page,"html.parser")
    url_find=beauty.find_all("script")
    stdic=url_find[33].text

    dict_object = json.loads(re.search('var ytInitialData = (.+)[,;]{1}',str(stdic)).group(1))
    d=dict_object['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
    list_url=[]
    for i in range(len(d)-1):
        if list(d[i].keys())[0]=='videoRenderer':
            list_url.append(d[i]['videoRenderer']['videoId'])
    comment_list=ytcomments(list_url)
    return render_template("results.html",comments=comment_list[0:len(comment_list)])
def ytcomments(l):
    com_list=[]
    sq={"kaise","kyun","why","how","confused","confusion","where","which","doubt"}
    for url in l:
        #try and except was necessary as I was getting errors while running the code as in some cases comments were disabled
        try:
            data = youtube.commentThreads().list(part='snippet', videoId=url, maxResults='100',
                                                 textFormat="plainText").execute()
        except:
            continue
        for i in data["items"]:
            comment = i["snippet"]['topLevelComment']["snippet"]["textDisplay"]
            likes = i["snippet"]['topLevelComment']["snippet"]['likeCount']
            cq = set(comment.split())
            if comment != "" and len(sq.intersection(cq)) != 0 and len(cq)<100:
                com_list.append({"comment": comment,"likes":likes, "url": "https://www.youtube.com/watch?v="+url})
        while ("nextPageToken" in data):
            data = youtube.commentThreads().list(part='snippet', videoId=url, pageToken=data["nextPageToken"],
                                                 maxResults='100', textFormat="plainText").execute()
            for i in data["items"]:
                comment = i["snippet"]['topLevelComment']["snippet"]["textDisplay"]
                likes = i["snippet"]['topLevelComment']["snippet"]['likeCount']
                cq = set(comment.split())
                if comment!="" and len(sq.intersection(cq))!=0 and len(cq)<100:
                    com_list.append({"comment":comment,"likes":likes,"url":"https://www.youtube.com/watch?v="+url})

    com_list=sorted(com_list,key=lambda d:d["likes"], reverse=True)
    return com_list


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Default to 8000 if not set
    app.run(host='0.0.0.0', port=port,debug=True)
   
