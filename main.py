from glob import glob
import os
import time
import requests
import pandas as pd
import json
from string import Template
from dataclasses import dataclass

def get_data():
    def get_state_data(state):
        print("Grabbing data for " + state)
        state = state.lower().replace(" ", "-")
        url = Template("https://static01.nyt.com/elections-assets/2024/data/api/2024-11-05/state-page/${state}.json")
        response = requests.get(url.substitute(state=state))
        data = response.json()['data']
        return data
    state_name_list = "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
    states = [state for state in state_name_list]
    df_list = [get_state_data(state) for state in states]
    for index, i in enumerate(df_list):
        if not os.path.exists("data"): os.mkdir("data")
        with open(f"data/{states[index]}.json", "w") as f:
            f.write(json.dumps(i, indent=4))


@dataclass
class Candidate:
    name: str
    key: str
    electoral: int
    popular: int

def process_data(file_list):
    cannidates = []
    for i in file_list:
        x = json.load(open(i))
        for race in x['races']:
            if race["race_name"] == "President":
                for candidate in race['candidates']:
                    name = candidate['last_name']
                    key = candidate['candidate_key']
                    electoral = candidate['electoral_votes']
                    popular = candidate['votes']
                    found = False
                    for i in cannidates:
                        if i.name == name:
                            i.electoral += electoral
                            i.popular += popular
                            found = True
                    if not found:
                        cannidates.append(
                            Candidate(name, key, electoral, popular)
                        )
    # sort candidates by electoral votes
    cannidates.sort(key=lambda x: x.electoral, reverse=True)
    with open("Electoral.txt", "w") as f:
        for index, i in enumerate(cannidates):
            if index > 2: break
            f.write(f"{i.name} - {i.electoral}\n")
    # sort candidates by popular votes
    cannidates.sort(key=lambda x: x.popular, reverse=True)
    with open("Popular.txt", "w") as f:
        for index, i in enumerate(cannidates):
            if index > 2: break
            f.write(f"{i.name} - {i.popular}\n")
    print("Data Processed")

if __name__ == "__main__":
    last = 0
    while True:
        if time.time() > last+ (5 * 60 * 60) or os.path.exists("data") == False:
            get_data()
        process_data(glob(os.path.join("data", "*.json")))
        
        time.sleep(60 * 60)