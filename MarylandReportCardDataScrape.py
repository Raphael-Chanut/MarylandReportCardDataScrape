# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 08:52:48 2025

@author: raph
"""

import requests
import pandas as pd
from itertools import product
import time

url = "https://reportcard.msde.maryland.gov/Assessments/GetElaPerformanceBarChart"

# --- Define your dropdowns ---
years = ["2019", "2022", "2023", "2024", "2025"]
assessments = ["3ELA", "4ELA", "5ELA", "6ELA", "7ELA", "8ELA", "10ELA", "AELAA"]
genders = ["All Students", "Male", "Female"]
special_services = [
    "All Students", "ADA 504", "Economically Disadvantaged", "Non-economically Disadvantaged",
    "FARMS", "Multilingual Learner", "Students with Disabilities", "Students without Disabilities",
    "Title 1", "Homeless", "Foster Care", "Military Connected"
]
races = ["All Students", "Am. Ind/AK", "Asian", "African Am.", "Hispanic",
          "HI/Pac. Isl.", "2+", "White"]

# --- Helper: convert dropdowns to FILTER string ---
def make_payload(assessment, gender, special_service, race, year, school_id="XXXX"):
    assessment_lookup = {
            "3ELA":"3",
            "4ELA":"4",
            "5ELA":"5",
            "6ELA":"6",
            "7ELA":"7",
            "8ELA":"8",
            "10ELA":"10",
            "AELAA":"A"
        }
    x1 = assessment_lookup[assessment]

    special_service_lookup = {
        "All Students":"1",
        "ADA 504":"6",
        "Economically Disadvantaged":"11",
        "Non-economically Disadvantaged":"14",
        "FARMS":"3",
        "Multilingual Learner":"4",
        "Students with Disabilities":"2",
        "Students without Disabilities":"13",
        "Title 1":"5",
        "Homeless":"8",
        "Foster Care":"9",
        "Military Connected":"10"
    }
    x2 = special_service_lookup[special_service]

    race_lookup = {
        "All Students":"6",
        "Am. Ind/AK":"8",
        "Asian":"9",
        "African Am.":"10",
        "Hispanic":"7",
        "HI/Pac. Isl.":"11",
        "2+":"13",
        "White":"12"
        }
    x3 = race_lookup[race]

    gender_lookup = {
        "All Students":"3",
        "Male":"1",
        "Female":"2"
        }
    x4 = gender_lookup[gender]

    filterx = f"/{assessment}/{x1}/{x3}/{x4}/{x2}/15/{school_id}/{year}"
    print(filterx)


    payload = {
                "LEA": "15",
                "SCHOOLID": "XXXX",
                "YEAR": year,
                "SEXCODE": x4,
                "RACECODE": x3,
                "GRADE": x1,
                "TypeName": "Current",
                "SUBJECTID": assessment,
                "SPCL_SVC_KEY": x2,
                }

    return payload

# --- Request helper ---
def fetch_ela_data(payload, year):

    resp = requests.post(url, json=payload)
    if not resp.ok:
        print(f"Failed for {payload} → {resp.status_code}")
        return None

    data = resp.json()
    try:
        graph_data = data["graphs"][0]["GraphData"]
        rows = [{item["Name"]: item["Value"] for item in row} for row in graph_data]
        df = pd.DataFrame(rows)
        # df["FilterString"] = filters
        df["Year"] = year
        return df
    except Exception as e:
        print(f"No data for {payload}: {e}")
        return None

# --- Loop through combinations ---
all_dfs = []

for (year, assessment, gender, service, race) in product(years, assessments, genders, special_services, races):
    payload = make_payload(assessment, gender, service, race, year)
    df = fetch_ela_data(payload, year)
    if df is not None:
        df["Assessment"] = assessment
        df["Gender"] = gender
        df["Service"] = service
        df["Race"] = race
        all_dfs.append(df)

        time.sleep(1)  # polite delay

# --- Combine all into one DataFrame ---
if all_dfs:
    full_df = pd.concat(all_dfs, ignore_index=True)
    print(full_df)
else:
    print("No data returned.")


combined_df = pd.concat(all_dfs, ignore_index=True)
combined_df.to_csv("reportcard_msde_maryland.csv", index=False)




































