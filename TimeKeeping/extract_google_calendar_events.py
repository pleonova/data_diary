# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 18:02:54 2018

Modification of the Python Google Calendar API
https://developers.google.com/calendar/quickstart/python

@author: Leonova

Objective: Extract past google calander events into a pandas dataframe in order 
to detect behavioral patterns. 

Goals: Extract data from Fitbit, Google Now, RescueTime to have a comprehensive
overview of where my time goes. 

"""

from __future__ import print_function
from datetime import datetime, timedelta

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import pandas as pd
import numpy as np


# Set up key and access file/folder
mason_jar_path = 'C:/Users/Leonova/Dropbox/Time Keeping - Mason Jar/'
credential_file_name = 'credentials_client_secret_google_calendar.json'


CLIENT_SECRET_FILE = mason_jar_path + credential_file_name
APPLICATION_NAME = 'Mason Jar Calendar'
TOKEN = mason_jar_path + 'token.json'
# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'

# How far back do you want to retrieve events
num_days_prior = 2

def main(num_days_prior):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    store = file.Storage(TOKEN)
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))


    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    x_days_before = (datetime.today() - timedelta(days=num_days_prior)).isoformat() + 'Z'
    print('Getting the upcoming 10 events')
    
    # Details about the events().list() class: 
    # https://developers.google.com/calendar/v3/reference/events/list
    events_result = service.events().list(
            calendarId='primary', 
            timeMin=x_days_before,
            maxResults=10, 
            singleEvents=True,
            orderBy='startTime').execute()
    
    # We want to extract the things that are stored in items
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))

    # Sometimes description is omitted entirely
        if 'description' in event:
            desc = event['description']
        else:
            desc = 'no description exists'
      
    # We want our final out put to have the start, name of event and description              
        print(start, event['summary'], desc)


if __name__ == '__main__':
    main()