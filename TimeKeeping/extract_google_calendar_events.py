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
from datetime import datetime, timedelta, date

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import os
import pandas as pd
import numpy as np


# Set up key and access file/folder
mason_jar_path = 'C:/Users/Leonova/Dropbox/Time Keeping - Mason Jar/'
credential_file_name = 'credentials_client_secret_google_calendar.json'
# Set up tokens and secrets
CLIENT_SECRET_FILE = os.path.join(mason_jar_path, credential_file_name)
APPLICATION_NAME = 'Mason Jar Calendar'
TOKEN = os.path.join(mason_jar_path, 'token.json')
# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'

# Date Range: Start
start_date = '2018-08-01'
# Date Range: End
#now = datetime.now()      #str(date.today())
#now.strftime("%Y-%m-%d %H:%M")

end_date = '2018-08-25'




def main(start_date, end_date):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    store = file.Storage(TOKEN)
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))


    # Call the Calendar API ('Z' indicates UTC time)
    start_date_z = pd.to_datetime(start_date).isoformat()+'Z'
    end_date_z = pd.to_datetime(end_date).isoformat() + 'Z' 
    print('Getting the events between ' + start_date_z + ' and ' + end_date_z)
    
    # Details about the events().list() class: 
    # https://developers.google.com/calendar/v3/reference/events/list
    events_result = service.events().list(
            calendarId = 'primary', 
            timeMin = start_date_z,
            timeMax = end_date_z,
            maxResults = 1000, 
            singleEvents = True,
            orderBy ='startTime').execute()
    
    # We want to extract the things that are stored in items
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        # Get the start and end date/time of the event
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        # Sometimes description is omitted entirely
        if 'description' in event:
            desc = event['description'].replace('\n', ' ').replace('\r', '')
        else:
            desc = 'no description exists'
            
        event_title = event['summary']#.replace(',', ' ')
        # We want our final out put to have the start, name of event and description              
        print(start, end, event_title, desc)
        
        # Add contents to a file (tab separted)
        exportFile.write(start + '\t' + end + '\t' + event_title + '\t' + desc)
        exportFile.write('\n')

# Change the path where to store the export file
os.chdir(mason_jar_path)

if __name__ == '__main__':

    exportFile = open('GoogleCalendarExport ' + start_date + ' to ' + end_date + '.csv','w')
    # Add headers for the csv file (tab separted)
    exportFile.write('start\tend\ttitle\tdescription\n')
    
    main(start_date, end_date)
    
    exportFile.close()
    
    