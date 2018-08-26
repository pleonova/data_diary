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
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import pandas as pd
import numpy as np

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'


# Set up key and access file/folder
mason_jar_path = 'C:/Users/Leonova/Dropbox/Time Keeping - Mason Jar/'
credential_file_name = 'credentials_client_secret_google_calendar.json'


CLIENT_SECRET_FILE = mason_jar_path + credential_file_name
APPLICATION_NAME = 'Mason Jar Calendar'



def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    store = file.Storage(mason_jar_path + 'token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    
    # Details about the events().list() class
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))

        if 'description' in event:
            desc = event['description']
        else:
            desc = 'no description exists'
                    
        print(start, event['summary'], desc)
        
    #### try to add description, but it only appears sometimes   

        if 'description' in event:
            return(event['description'])
        else:
            return('no description exists')
    
        try:
           a = events[0]['description'] 
        except:
            end = 'error'
   
df = pd.DataFrame(np.array(events[0])) #.reshape(3,3), columns = list("abc"))
     
#        
#    for description in descriptions:
#        des = description['description']
#        print(des)
#

######
if __name__ == '__main__':
    main()