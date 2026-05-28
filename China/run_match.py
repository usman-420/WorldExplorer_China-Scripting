# run_match.py
# this script is called by node-red when the user submits the profile form
# it reads the profile from a json file, runs match_destinations and saves the csv

import sys
import json
import os

# make sure we can import from WorldExplorer package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from WorldExplorer.match_destinations import match_destinations

# read the profile from a json file that node-red writes
profile_path = os.path.join(os.path.dirname(__file__), "data", "node_red_profile.json")

try:
    with open(profile_path, "r") as f:
        profile = json.load(f)

    print(f"running match for profile: {profile}")
    df = match_destinations(profile)
    print("done")

except Exception as e:
    print(f"error: {e}")
    sys.exit(1)