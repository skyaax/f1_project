import requests
import pandas as pd
import json
import sqlite3

def load(data, table_name,index=False, if_exists="replace"):
    connection = sqlite3.connect("f1_data.db")
    data.to_sql(table_name, connection, if_exists=if_exists, index=index)
    connection.close()

def extract_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")
        return None


connection = sqlite3.connect("f1_data.db")
cursor = connection.cursor()

#Meetings Data loading
url_for_meetings_data = "https://api.openf1.org/v1/meetings"

meetings_data_response = extract_data(url_for_meetings_data)
meetings_data_df = pd.DataFrame(meetings_data_response)

print(meetings_data_df.head(10))
#print(meetings_data_df.info())
#print(meetings_data_df.describe())

load(meetings_data_df, "meetings")

#Drivers Data loading
url_for_drivers_data = "https://api.openf1.org/v1/drivers"
drivers_data_response = extract_data(url_for_drivers_data)
drivers_data_df = pd.DataFrame(drivers_data_response)

print(drivers_data_df.head(10))
#print(drivers_data_df.info())
#print(drivers_data_df.describe())

load(drivers_data_df, "drivers")

#session data loading
url_for_session_data = "https://api.openf1.org/v1/sessions?session_type=Race"
session_data_response = extract_data(url_for_session_data)
session_data_df = pd.DataFrame(session_data_response)

print(session_data_df.head(10))
#print(session_data_df.info())
#print(session_data_df.describe())

load(session_data_df, "sessions")

#session result data loading
url_for_session_results_data = "https://api.openf1.org/v1/session_result?position<=3"

session_keys = cursor.execute("select session_key from sessions").fetchall()
session_result_data_response = requests.get(url_for_session_results_data,params={"session_key": [key[0] for key in session_keys]}).json()

session_result_data_df = pd.DataFrame(session_result_data_response)
print("Session Result Data:")
print(session_result_data_df.head(10))

load(session_result_data_df, "session_result")

count_max_wins = cursor.execute("select count(*) from session_result join dri where position=1")