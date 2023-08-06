# Standard Library
import pandas as pd
import statistics as st
import numpy as np
import imdb
from datetime import datetime
from datetime import timedelta
import multiprocessing
import json
import time
import re
import random
import matplotlib.pyplot as plt
# Email Library
from email.mime.text import MIMEText as text
import smtplib
# Scraper Library
from bs4 import BeautifulSoup as soup  # HTML data structure
from urllib.request import urlopen as uReq  # Web client
from lxml import etree
# Twitter API Library
import tweepy
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from tweepy import Stream
# Kafka Library
from kafka import KafkaProducer
from kafka import KafkaConsumer
# Pymongo Library
from pymongo import MongoClient
from pprint import pprint
# Pre-processing Library
from difflib import SequenceMatcher
import string
import unicodedata
import nltk
import contractions
import inflect
# Sentiment Analysis Library
from textblob import TextBlob
from nltk import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import *
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from google.oauth2 import service_account
# No Warning
pd.options.mode.chained_assignment = None
#! YOU NEED ALSO HTMLIB5 INSTALLED, NOT NEED TO IMPORT IT

#!! YOU NEED TO HAVE COMPLETED NTLK INSTALLATION, INCLUDING "ntlk-download()"


def movie_title():
    #selects yearly calendar
    exit = 0
    while exit != 1:
        while True:
            year_selected = str(input('Select which release calendar you want [2019/2020]: '))
            if year_selected not in ("2019", "2020"):
                print("Sorry, you selected a year out of range.")
                continue
            else:
                break
        while True:
            print("You selected: "+year_selected+". Is that correct?")
            yes_no = input('[y/n]:  ')
            if (yes_no == "y") or (yes_no == "n"):
                break
            else:
                print("Sorry, you did not enter y or n.")
                continue
        while True:
            if yes_no == "n":
                is_looping = False
                break
            else:
                exit = 1
                break
    print("Please wait...")
    # URl to web scrap from.
    page_url = "https://www.firstshowing.net/schedule"+year_selected
    # opens the connection and downloads html page from url
    uClient = uReq(page_url)
    # parses html into a soup data structure to traverse html
    # as if it were a json data type.
    page_soup = soup(uClient.read(), "html.parser")
    uClient.close()
    # finds the container from the page
    #containers = page_soup.findAll("p", {"class": "sched"})
    containers = page_soup.findAll("div", {"class": "schedcontent"})
    #How many movies are releasing from 20 dec to 17 jan? (variable)
    #Create a dataframe which contains all movies release dates
    movie_dates_list = []
    datecontainer = page_soup.findAll("h4")
    y=0
    for container in datecontainer:
        date = container.strong.text
        y += 1
        movie_dates_list.append([date])
    movie_dates = pd.DataFrame(movie_dates_list, columns=["dates"])
    movie_dates = movie_dates.drop(movie_dates.tail(1).index)
    pd.set_option('display.max_rows', movie_dates.shape[0]+1)
    display(movie_dates)

    exit = 0
    while exit != 1:
        while True:
            while True:
                try:
                    movie_index_start = int(input('Enter index of start date:  '))
                    break
                except ValueError:
                    print("Cannot enter null or string value.")
            if movie_index_start > len(movie_dates)-1:
                print("Sorry, you selected an index out of range.")
                continue
            else:
                break
        while True:
            print("You selected: "+movie_dates.iloc[movie_index_start]["dates"]+". Is that correct?")
            yes_no = input('[y/n]:  ')
            if (yes_no == "y") or (yes_no == "n"):
                break
            else:
                print("Sorry, you did not enter y or n.")
                continue
        while True:
            if yes_no == "n":
                is_looping = False
                break
            else:
                start_date_input = movie_dates.iloc[movie_index_start]["dates"]
                exit = 1
                break

    exit = 0
    while exit != 1:
        while True:
            while True:
                try:
                    movie_index_end = int(input('Enter index of end date: '))
                    break
                except ValueError:
                    print("Cannot enter null or string value.")
            if movie_index_end > len(movie_dates)-1:
                print("Sorry, you selected an index out of range.")
                continue
            else:
                if movie_index_end >= movie_index_start:
                    break
                else:
                    print("You must select an end date that is after the start date selected previously.")
                    continue
        while True:
            print("You selected: "+movie_dates.iloc[movie_index_end]["dates"]+". Is that correct?")
            yes_no = input('[y/n]:  ')
            if (yes_no == "y") or (yes_no == "n"):
                break
            else:
                print("Sorry, you did not enter y or n.")
                continue
        while True:
            if yes_no == "n":
                is_looping = False
                break
            else:
                try:
                    end_date_input = movie_dates.iloc[movie_index_end+1]["dates"]
                except IndexError:
                    end_date_input = '<h4 align="center">'
                exit = 1
                break
    print("Please wait...")
    #create list in which to store movie names
    movie_titles_list = []
    #Counts how many movies are releasing between the two specified dates.
    start_date = start_date_input+"<"
    end_date = end_date_input+"<"
    html_str = str(containers)
    text = html_str[html_str.index(start_date)+len(start_date):html_str.index(end_date)]
    textsoup = soup(text, "html.parser")
    containers_new = textsoup.findAll("a", {"class": "showTip"})
    n_movies= len(textsoup.findAll("a", {"class": "showTip"}))
    #Get movie names from start_date to end_date
    for container in containers_new:
        title = container.text
        movie_titles_list.append([title])
    movie_titles = pd.DataFrame(movie_titles_list, columns=["title"])
    #Select one movie
    display(movie_titles)
    exit = 0
    while exit != 1:
        while True:
            while True:
                try:
                    movie_index = int(input('Select the movie of your interest. Enter index of desired movie:  '))
                    break
                except ValueError:
                    print("Cannot enter null or string value.")
            if movie_index > len(movie_titles)-1:
                print("Sorry, you selected an index out of range.")
                continue
            else:
                break
        while True:
            print("You selected: "+movie_titles.iloc[movie_index]["title"]+". Is that correct?")
            yes_no = input('[y/n]:  ')
            if (yes_no == "y") or (yes_no == "n"):
                break
            else:
                print("Sorry, you did not enter y or n.")
                continue
        while True:
            if yes_no == "n":
                is_looping = False
                break
            else:
                selected_movie = movie_titles.iloc[movie_index]["title"]
                exit = 1
                break
    #Now we use imdbpy to get data about the movie
    ia = imdb.IMDb()
    i = imdb.IMDb('http')
    #Create lists for each column of the new dataframe
    movie_info = pd.DataFrame( columns = ["title", "release", "genres", "top_5_cast"])
    print("Please wait...")
    #Get info like: movie title, release date in us, genres, top 5 actors
    title = selected_movie
    movies = ia.search_movie(title)
    movies_id = movies[0].movieID
    movie = i.get_movie(movies_id)
    i.update(movie, 'release dates')
    release_list = [i for i in movie["release dates"] if i.startswith('USA')]
    release = []
    for z in release_list:
        if re.match("USA::\d+\s\w+\s\d\d\d\d$", z):
            release.append(z)
    genres = movie['genres']
    top_5_list = []
    try:
        cast = movie.get('cast')
        topActors = 5
        for actor in cast[:topActors]:
            top_5 = ("{}".format(actor['name']))
            top_5_list.append(top_5)
    except KeyError:
        cast = np.nan
    #Populate the dataframe
    movie_info.at[0,"title"] = title
    movie_info.at[0,"release"] = release[0].lstrip("'[USA::").rstrip("]'")
    movie_info["release"] = pd.to_datetime(movie_info["release"])
    movie_info.at[0,"genres"] = [', '.join(genres)][0]
    movie_info.at[0, "top_5_cast"] = [', '.join(top_5_list)][0]
    #Clean the data
    print("Done!")

    return movie_info

def hashtags(movie):
    #Takes title and actors and makes them lowercase, no whitespace, etc and creates a column for each hashtag
    hashtag_df_cast = movie["top_5_cast"].str.split(", ", expand=True).reindex(columns=np.arange(5)).add_prefix('actor_hashtag_')
    hashtag_df_title = movie["title"].str.split(": ", expand=True).reindex(columns=np.arange(2)).add_prefix('title_hashtag_')
    hashtag_df_title["title_hashtag_2"] = hashtag_df_title["title_hashtag_0"] +"movie"
    hashtag_df_title["title_hashtag_3"] = movie["title"]
    hashtag_df_cast = hashtag_df_cast.apply(np.vectorize(lambda x: x.lower().replace(" ", "").strip("'").replace(".", "") if(np.all(pd.notnull(x))) else x))
    hashtag_df_title = hashtag_df_title.apply(np.vectorize(lambda x: x.lower().replace(" ", "").replace(":", "") if(np.all(pd.notnull(x))) else x))
    hashtag_df_title.at[(hashtag_df_title["title_hashtag_1"].isnull() == True), "title_hashtag_3"] = np.nan
    movie_info_hashtags = pd.concat([movie, hashtag_df_title, hashtag_df_cast], axis=1).replace(to_replace=["None"], value=np.nan)
    hashtags_only_df = pd.concat([hashtag_df_title, hashtag_df_cast], axis=1).replace(to_replace=["None"], value=np.nan)
    query = hashtags_only_df.T.apply(lambda x: x.dropna().tolist())[0].tolist()
    mytopic = str(movie_info_hashtags.iloc[0]["title_hashtag_0"])
    return movie_info_hashtags, query, mytopic

def nifi_template_changer(template, mytopic):
    tree = etree.parse(template)
    for elem in tree.iterfind("//*"):
    #change topic
        if elem.text in ("mycollectionname", "mytopicname"):
            elem.text = mytopic
        tree.write('new_template.xml', pretty_print=True)

def key():
    consumer_key = str(input("Please type your consumer key: "))
    consumer_secret = str(input("Please type your consumer secret key: "))
    access_key = str(input("Please type your access key: "))
    access_secret = str(input("Please type your access secret key: "))
    return consumer_key, consumer_secret, access_key, access_secret

def stream(stop, keys, mytopic, query):
    while True:

        consumer_key = keys[0]
        consumer_secret = keys[1]
        access_key = keys[2]
        access_secret = keys[3]

        class MyListener(StreamListener):

            def __init__(self, producer, producer_topic):
                super().__init__()
                self.producer = producer
                self.producer_topic = producer_topic

            def on_status(self, status):
                is_retweet = hasattr(status, "retweeted_status")
                is_ext = hasattr(status, "extended_tweet")
                if hasattr(status,"extended_tweet"):
                    text = status.extended_tweet["full_text"]
                else:
                    text = status.text
                tweet = {
                  'user_id': status.user.id,
                  'username': status.user.name,
                  'screen_name': status.user.screen_name,
                  'text': text,
                  'which_lang' : status.lang,
                  'is_RT' : is_retweet,
                  'is_EXT' : is_ext,
                }
                self.producer.send(topic=self.producer_topic, value=tweet)

        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(auth)

        producer = KafkaProducer(
            bootstrap_servers=["kafka:9092"],
            value_serializer=lambda v: json.dumps(v).encode("utf-8"))

        listener = MyListener(producer = producer, producer_topic = mytopic)

        stream = Stream(auth=api.auth,tweet_mode='extended',listener=listener)
        stream.filter(track=query, languages=["en"])
        if stop():
                break

def ask_time():
    while True:
        try:
            timeout_input = int(input("For how long do you want to collect tweets? (in minutes - integer): "))
        except ValueError:
            print("Sorry, you have not inputed an integer number.")
            continue
        break
    timeout_mins = timeout_input
    timeout = timeout_mins*60
    return timeout

def get_email():
    while True:
        print("Do you wanna receive an email when the collection completes?")
        yes_no = str(input('[y/n]:  '))
        if (yes_no == "y") or (yes_no == "n"):
            break
        else:
            print("Sorry, you did not enter y or n.")
            continue
    if yes_no == "n":
        exit=1
        email = 0
    else:
        exit=0
    while exit != 1:
        while True:
            email_entered = str(input("Please type in your email: "))
            print("You entered: "+email_entered+". Is that correct?")
            yes_no_mail = input('[y/n]:  ')
            if (yes_no_mail == "y") or (yes_no_mail == "n"):
                break
            else:
                print("Sorry, you did not enter y or n.")
                continue
        while True:
            if yes_no_mail == "n":
                is_looping = False
                print("c")
                break
            else:
                email = email_entered
                exit = 1
                break
    return email

def send_email_finish(email):
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login("mtsbcomplete@gmail.com", "DataMan2019!")
    m = text("The tweet collector have finished,\nNow you can check on Mongodb typing: \nlocalhost:8081 on your local browser.")
    m['Subject'] = '***TWEET COLLECTION FINISHED***'
    m['From'] = "mtsbcomplete@gmail.com"
    m['To'] = email
    server.sendmail(
        "mtsbcomplete@gmail.com",
        email,
        m.as_string())
    server.quit()

def starter(timeout, keys, mytopic, query, email):
    stop_process = False
    streamf = multiprocessing.Process(target = stream, args =(lambda : stop_threads, keys, mytopic, query))
    streamf.daemon = True
    streamf.start()
    time.sleep(timeout)
    stop_process = True
    streamf.terminate()
    if email!=0:
        send_email_finish(email)
    streamf.join()
    print('Process killed')
    print("Is stream alive?")
    print(streamf.is_alive())

def get_database_coll():
    #Variable with client info
    client = MongoClient('mongo', 27017, username='admin', password='DataMan2019!')
    #Choose database
    print('List of all databases in mongodb')
    db_names= pd.DataFrame(client.list_database_names(), columns = ["db_name"])
    display(db_names)
    exit = 0
    while exit != 1:
        while True:
            while True:
                try:
                    db_index = int(input('Select the database of your interest. Enter index of desired db:  '))
                    break
                except ValueError:
                    print("Cannot enter null or string value.")
            if db_index > len(db_names)-1:
                print("Sorry, you selected an index out of range.")
                continue
            else:
                break
        while True:
            print("You selected: "+db_names.iloc[db_index]["db_name"]+". Is that correct?")
            yes_no = input('[y/n]:  ')
            if (yes_no == "y") or (yes_no == "n"):
                break
            else:
                print("Sorry, you did not enter y or n.")
                continue
        while True:
            if yes_no == "n":
                is_looping = False
                break
            else:
                selected_db = db_names.iloc[db_index]["db_name"]
                exit = 1
                break
    #Choose collection
    print('List of all databases in the selected database')
    coll_names= pd.DataFrame(client[selected_db].list_collection_names(), columns = ["collection_name"])
    display(coll_names)
    exit = 0
    while exit != 1:
        while True:
            while True:
                try:
                    coll_index = int(input('Select the collection of your interest. Enter index of desired collection:  '))
                    break
                except ValueError:
                    print("Cannot enter null or string value.")
            if coll_index > len(coll_names)-1:
                print("Sorry, you selected an index out of range.")
                continue
            else:
                break
        while True:
            print("You selected: "+coll_names.iloc[coll_index]["collection_name"]+". Is that correct?")
            yes_no = input('[y/n]:  ')
            if (yes_no == "y") or (yes_no == "n"):
                break
            else:
                print("Sorry, you did not enter y or n.")
                continue
        while True:
            if yes_no == "n":
                is_looping = False
                break
            else:
                selected_coll = coll_names.iloc[coll_index]["collection_name"]
                exit = 1
                break
        db = client[selected_db]
        collection = db[selected_coll]
        data_python = collection.find()
        #Transform collection from json to pandas dataframe
        pd.set_option('display.max_colwidth', -1)
        df =  pd.DataFrame(list(data_python))
        return df


def clean_tweet_auto(dataframe):
    #Delete metada
    def remove_metadata(rows,start):
        for i in range(len(rows)):
            if(rows[i] == '\n'):
                start = i+1
                break
        new_doc_start = rows[start:]
        return new_doc_start
    #Delete contractions
    def replace_contractions(rows):
        new_doc = []
        for row in rows:
            new_row = contractions.fix(row)
            new_doc.append(new_row)
        return new_doc
    #Delete URL and e-mail
    def remove_url_mail(rows):
        new_doc = []
        for row in rows:
            new_row = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', row)
            new_row = re.sub(r'[\w\.-]+@[\w\.-]+', '', new_row)
            new_doc.append(new_row)
        return new_doc
    #Delete empty rows and tabs
    def remove_tabs(tokens):
        table= str.maketrans('','','\t\n\r')
        new = [token.translate(table) for token in tokens]
        return new
    #Delete non unicode characters
    def remove_non_unicode(tokens):
        new_tokens = []
        for token in tokens:
            new_token = unicodedata.normalize('NFKD', token).encode('ascii', 'ignore').decode('utf-8', 'ignore')
            new_tokens.append(new_token)
        return new_tokens
    #Delete punctuation
    def remove_punctuation(tokens):
        table= str.maketrans('','', string.punctuation)
        new = [token.translate(table) for token in tokens]
        new = [str for str in new if str]
        return new
    #Text stemming e lemmatization
    def stem_and_lem(tokens):
        stemmer = PorterStemmer()
        lemmatizer = WordNetLemmatizer()
        stemmed = [stemmer.stem(token) for token in tokens]
        lemmatized = [lemmatizer.lemmatize(token, pos='v') for token in tokens]
        return stemmed,lemmatized
    # pre processing,take only non-retweet
    df = dataframe.loc[~dataframe.is_RT == True]
    #Delete tweets that contains an http (usually ads)
    df['indexes'] = df['text'].str.find('http')
    df = df.loc[~df.indexes > -1]
    array_text = df.text.values
    array_text = remove_metadata(array_text,0)
    array_text = replace_contractions(array_text)
    array_text = remove_url_mail(array_text)
    array_text = remove_tabs(array_text)
    array_text = remove_non_unicode(array_text)
    array_text = remove_punctuation(array_text)
    print('\nAll tweets are clean')
    return array_text


def which_sentiment():
    exit = 0
    while exit != 1:
        while True:
            print("You can use Textblob sentiment analyzer or Google NLU service. Which one do you prefer?")
            sentiment_selected = str(input('[textblob/google]:  '))
            if sentiment_selected not in ("textblob", "google"):
                print("Sorry, you must select one of the two services.")
                continue
            else:
                break
        while True:
            print("You selected: "+sentiment_selected+". Is that correct?")
            yes_no = input('[y/n]:  ')
            if (yes_no == "y") or (yes_no == "n"):
                break
            else:
                print("Sorry, you did not enter y or n.")
                continue
        while True:
            if yes_no == "n":
                is_looping = False
                break
            else:
                sentiment_type = sentiment_selected
                exit = 1
                break
    return sentiment_type

def sentiment_textblob(array):
    print('\nThere are',len(array),'tweets in your database\n')
    df_result=pd.DataFrame()
    exit = 0
    while exit != 1:
        while True:
            while True:
                try:
                    num_tweet = int(input('\nHow many tweet you wanna analyze?\n'))
                    break
                except ValueError:
                    print("Cannot enter null or string value.")
            if num_tweet < 0:
                print("Sorry, you selected a negative number of tweets.")
                continue
            elif num_tweet > len(array):
                print("Sorry, you only have "+len(array)+" in your collection.")
            else:
                 break
        while True:
            print('\nDo you want do a random sampling?')
            yes_no = input('[y/n]: ')
            if yes_no in ("y", "n"):
                if (yes_no == "y"):
                    array=random.choices(array, k=num_tweet)
                    break
                else:
                    print("Ok. No random sampling.")
                    break
            else:
                print("Sorry, you did not enter y or n.")
                continue
        exit = 1
    for i in range(len(array)):
        text = TextBlob(array[i])
        df_result = df_result.append({'score': text.sentiment.polarity, 'magnitude' : text.sentiment.subjectivity}, ignore_index=True)
    return df_result

def google_analyze_tweet(array):
    print('\nThere are',len(array),'tweets in your database\n')
    df_result = pd.DataFrame()
    print('***IMPORTANT***\n')
    print('You need copy and paste your google credentials.json in my-data folder before continuing!\n')
    while True:
        print("Type [y] when you have done it: ")
        yes = input('[y]:  ')
        if (yes == "y"):
            break
        else:
            print("Sorry, you did not enter y.")
            continue
    while True:
        name_cred = str(input("\nPlease insert the name of your Google credential file: \n"))
        dire_cred = '/data/my-data/' + name_cred + '.json'
        #Does the file exists in my:data?
        try:
            with open(dire_cred) as f:
                # google credentials
                creds = service_account.Credentials.from_service_account_file(dire_cred)
                client = language.LanguageServiceClient(credentials=creds)
                exit = 0
                while exit != 1:
                    while True:
                        while True:
                            try:
                                num_tweet = int(input('\nHow many tweet you wanna analyze?\n'))
                                break
                            except ValueError:
                                print("Cannot enter null or string value.")
                        if num_tweet < 0:
                            print("Sorry, you selected a negative number of tweets.")
                            continue
                        elif num_tweet > len(array):
                            print("Sorry, you only have "+len(array)+" in your collection.")
                        else:
                            break
                    while True:
                        print('\nDo you want do a random sampling?')
                        yes_no = input('[y/n]: ')
                        if yes_no in ("y", "n"):
                            if (yes_no == "y"):
                                array=random.choices(array, k=num_tweet)
                                break
                            else:
                                print("Ok. No random sampling.")
                                break
                        else:
                            print("Sorry, you did not enter y or n.")
                            continue
                    exit = 1
                #Analyzing tweets
                for i in range(num_tweet):
                    text = array[i]
                    document = types.Document(
                        content=text,
                        type=enums.Document.Type.PLAIN_TEXT)
                    sentiment = client.analyze_sentiment(document=document).document_sentiment
                    df_result = df_result.append({'score': sentiment.score, 'magnitude' : sentiment.magnitude}, ignore_index=True)
            break
        except IOError:
            print("File not accessible or not existing in that directory.")
            print('You need copy and paste your google credentials.json in my-data folder.\n')
            print("Please check if the file is accessible and if the filename is correct.")
            continue
    return df_result

#Matcher to find the correct movie title
def matcher (df, title):
    return SequenceMatcher(None, title, df["Release"]).ratio()

def box_office(selected_movie_title, selected_movie_date):
    print("Please wait...")
    #Creates empty list
    boxoff_week = pd.DataFrame(columns = ['Release', 'Gross'])
    #Checks if 8 days has passed from the release
    current_day = pd.to_datetime(datetime.now().date())
    if (current_day - selected_movie_date).days < 8:
        print("Sorry. Not enough days has passed to aggregate 7 days data.")
    else:
        #Scrape data from boxofficemojo for the 7 days after the tweets collection
        try:
            delta_day = 2
            selected_boxoff = 0
            while delta_day < 9:
                boxoff_daily = pd.read_html("https://www.boxofficemojo.com/date/"+(selected_movie_date+timedelta(days=delta_day)).strftime('%Y-%m-%d'))[0]
                boxoff_daily = boxoff_daily[["Release", "Daily"]]
                boxoff_daily["titlematch"] = boxoff_daily.apply(matcher, args=[selected_movie_title], axis=1)
                boxoff_daily['Daily'] = boxoff_daily['Daily'].str.replace(',', '')
                boxoff_daily['Daily'] = boxoff_daily['Daily'].str.replace('$', '')
                boxoff_daily['Daily'] = boxoff_daily['Daily'].astype(int)
                selected_boxoff += boxoff_daily.loc[boxoff_daily["titlematch"] == boxoff_daily["titlematch"].max(),"Daily"].values[0]
                delta_day+=1
            boxoff_week.at[0,"Release"] = selected_movie_title
            boxoff_week.at[0,"Gross"] = selected_boxoff
            return boxoff_week
        except ValueError:
            print("No data found on boxofficemojo.com.")


#____________________________________________________________________________________________________________________
#FULL FUNCTIONS

def tweet_collector():
    print("Please start the following services via shell:")
    print("zookeeper, kafka, mongo, nifi")
    while True:
        print("Type [y] when you're ready: ")
        yes = input('[y]:  ')
        if (yes == "y"):
            break
        else:
            print("Sorry, you did not enter y.")
            continue
    movies = movie_title()
    movies_info_hashtags, query, mytopic = hashtags(movies)
    print("The topic for kafka and nifi is: "+str(mytopic))
    print("Do you want to create a nifi template with correct topic names?")
    while True:
        yes_no = input('[y/n]: ')
        if yes_no in ("y", "n"):
            if (yes_no == "y"):
                nifi_template_changer("template.xml", mytopic)
                print("Please upload the template to nifi and start all services.")
                break
            else:
                print("Ok. Remember to check you nifi template's settings and to start all services.")
                break
        else:
            print("Sorry, you did not enter y or n.")
            continue
    while True:
        print("Type [y] when you're ready: ")
        yes = input('[y]:  ')
        if (yes == "y"):
            break
        else:
            print("Sorry, you did not enter y.")
            continue
    timeout = ask_time()
    keys =  key()
    email = get_email()
    print("Are you ready to start tweets' collection?")
    while True:
        print("Type [y] when you're ready: ")
        yes = input('[y]:  ')
        if (yes == "y"):
            break
        else:
            print("Sorry, you did not enter y.")
            continue
    starter(timeout, keys, mytopic, query, email)


def sentiment():
    #Asks the user which sentiment service wants to use
    sentiment_type = which_sentiment()
    #Returns the weighted geometric mean of the score*magnitude for the selected collection
    tweet_df = get_database_coll()
    tweets_array = clean_tweet_auto(tweet_df)
    if sentiment_type == "textblob":
        sentiment_df = sentiment_textblob(tweets_array)
        mean_magnitude = sentiment_df.magnitude.mean()
        mean_sentiment = sentiment_df.score.mean()
        mean_sentiment_perc_pos = len(sentiment_df[sentiment_df.score >= 0])/len(sentiment_df)
        std_magnitude = round(statistics.stdev(sentiment_df.magnitude),4)
        std_score = round(statistics.stdev(sentiment_df.score),4)
    else:
        sentiment_df = google_analyze_tweet(tweets_array)
    mean_magnitude = sentiment_df.magnitude.mean()
    mean_sentiment = sentiment_df.score.mean()
    mean_sentiment_perc_pos = len(sentiment_df[sentiment_df.score >= 0])/len(sentiment_df)
    std_magnitude = round(st.stdev(sentiment_df.magnitude),4)
    std_score = round(st.stdev(sentiment_df.score),4)

    return mean_sentiment, mean_magnitude, mean_sentiment_perc_pos, std_score, std_magnitude

def sentiment_boxoffice_all():
    boxoffice_sentiment_all = pd.DataFrame()
    exit = 0
    while exit!=1:
        selected_movie = movie_title()
        selected_movie_title = selected_movie.iloc[0]["title"]
        selected_movie_date = selected_movie.iloc[0]["release"]
        print("Please wait...")
        try:
            boxoffice_sentiment_data = box_office(selected_movie_title, selected_movie_date)
            boxoffice_sentiment_data = boxoffice_sentiment_data[["Release", "Gross"]]
            boxoffice_sentiment_data["Genres"] = selected_movie.iloc[0]["genres"]
            boxoffice_sentiment_data["sentiment_Avg"], boxoffice_sentiment_data["magnitude_Avg"], boxoffice_sentiment_data["sentiment_pos_percentage"], boxoffice_sentiment_data["sentiment_std_score"], boxoffice_sentiment_data["sentiment_std_magnitude"] = sentiment()
            boxoffice_sentiment_data["sentiment_neg_percentage"] = 1 - boxoffice_sentiment_data["sentiment_pos_percentage"]
            boxoffice_sentiment_all = boxoffice_sentiment_all.append(boxoffice_sentiment_data, ignore_index=True)
        except TypeError:
            print("No data found.")
        print("Do you want to add more movies?")
        while True:
            yes_no = input('[y/n]: ')
            if yes_no in ("y", "n"):
                    break
            else:
                print("Sorry, you did not enter y or n.")
                continue
        while True:
            if (yes_no == "y"):
                print("Ok. Please select another movie to add.")
                break
            else:
                print("Ok.")
                exit = 1
                break
    return boxoffice_sentiment_all


def spearman_corr(df):
    corr_matrix = df.corr(method="spearman")
    return corr_matrix
