import os
import sqlite3
import logging

import fastf1
import pandas as pd


YEARS = [2021,2022,2023,2024]
DB_NAME = "f1_data.db"


def value(x):
    if pd.isna(x):
        return None
    if isinstance(x, pd.Timedelta):
        return str(x)
    return x


def insert(cursor, table, data):
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    sql = f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})"
    cursor.execute(sql, tuple(data.values()))


os.makedirs("fastf1_cache", exist_ok=True)
logging.disable(logging.CRITICAL)
fastf1.set_log_level("ERROR")
fastf1.Cache.enable_cache("fastf1_cache")
connection = sqlite3.connect(DB_NAME)
cursor = connection.cursor()

for year in YEARS:
    schedule = fastf1.get_event_schedule(year)

    for _, event in schedule.iterrows():
        if event["EventFormat"] == "testing":
            continue

        race_id = int(f"{year}{int(event['RoundNumber']):02d}")
        circuit_id = str(event["Location"]).lower().replace(" ", "_")

        print(f"Loading {year} - {event['EventName']}")

        insert(cursor, "circuits", {
            "circuit_id": circuit_id,
            "name": value(event["Location"]),
            "country": value(event["Country"]),
            "city": value(event["Location"]),
        })

        insert(cursor, "races", {
            "race_id": race_id,
            "season": year,
            "round": int(event["RoundNumber"]),
            "race_name": value(event["EventName"]),
            "circuit_id": circuit_id,
            "race_date": str(value(event["EventDate"])),
        })

        qualifying = fastf1.get_session(year, event["EventName"], "Q")
        qualifying.load(telemetry=False, weather=False, messages=False, laps=False)

        for _, driver in qualifying.results.iterrows():
            driver_id = value(driver["Abbreviation"])
            constructor_id = value(driver["TeamId"])

            insert(cursor, "drivers", {
                "driver_id": driver_id,
                "driver_number": value(driver["DriverNumber"]),
                "full_name": value(driver["FullName"]),
                "abbreviation": value(driver["Abbreviation"]),
                "nationality": value(driver["CountryCode"]),
            })

            insert(cursor, "constructors", {
                "constructor_id": constructor_id,
                "name": value(driver["TeamName"]),
            })

            insert(cursor, "qualifying_results", {
                "race_id": race_id,
                "driver_id": driver_id,
                "constructor_id": constructor_id,
                "position": value(driver["Position"]),
                "q1": value(driver["Q1"]),
                "q2": value(driver["Q2"]),
                "q3": value(driver["Q3"]),
            })

        race = fastf1.get_session(year, event["EventName"], "R")
        race.load(telemetry=False, weather=False, messages=False, laps=False)

        for _, driver in race.results.iterrows():
            insert(cursor, "race_results", {
                "race_id": race_id,
                "driver_id": value(driver["Abbreviation"]),
                "constructor_id": value(driver["TeamId"]),
                "grid_position": value(driver["GridPosition"]),
                "finish_position": value(driver["Position"]),
                "points": value(driver["Points"]),
                "laps": None,
                "status": value(driver["Status"]),
                "fastest_lap_time": None,
            })

connection.commit()
connection.close()

print("Done. Data inserted into f1_data.db")
