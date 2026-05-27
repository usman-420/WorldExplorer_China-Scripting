# api_clients.py
# handles all the external API calls for WorldExplorer
# we use 3 APIs here:
# - open-meteo for climate data (free, no key needed)
# - opentripmap for attractions (free tier, needs a key)
# - rest countries for basic china info (free, no key needed)

import requests
import os
from dotenv import load_dotenv

# load the keys from .env file
load_dotenv()

otripmap_key = os.getenv("OPENTRIPMAP_API_KEY")


# open-meteo
# honestly the easiest API i've ever used, no key, just call the url
# we ask for monthly averages from 2000-2020 so we get reliable long term data
# this is used in seasonal_analysis.py to show climate per month

def get_climate_data(lat, lon):
    url    = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude":   lat,
        "longitude":  lon,
        "start_date": "2020-01-01",
        "end_date":   "2020-12-31",
        "daily":      "temperature_2m_mean,precipitation_sum,windspeed_10m_max",
        "timezone":   "auto"
    }

    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  climate api failed: {e}")
        return {}


# opentripmap
# returns tourist attractions near a location
# we give it coordinates and a radius and it gives back a list of places
# used in attractions_map.py to put markers on the folium map

def get_attractions(lat, lon, radius=15000):
    if not otripmap_key:
        print("  no opentripmap key in .env, skipping")
        return []

    url    = "https://api.opentripmap.com/0.1/en/places/radius"
    params = {
        "radius": radius,
        "lon":    lon,
        "lat":    lat,
        "kinds":  "cultural,natural,architecture,museums,historic",
        "rate":   "2",        # 1-3, we want at least somewhat known places
        "format": "json",
        "limit":  30,
        "apikey": otripmap_key
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  opentripmap failed: {e}")
        return []


def get_attraction_details(xid):
    # fetches extra details for one attraction using its unique id
    # gives us description, wikipedia url, image etc
    if not otripmap_key:
        return {}

    url = f"https://api.opentripmap.com/0.1/en/places/xid/{xid}"

    try:
        r = requests.get(url, params={"apikey": otripmap_key}, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  attraction details failed: {e}")
        return {}


# rest countries
# simple free API that gives basic info about any country
# we use it for the dashboard overview (population, currency etc)
# no key needed, just call the url

def get_country_info():
    url = "https://restcountries.com/v3.1/name/china?fullText=true"

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        d = r.json()[0]

        return {
            "name":       d["name"]["common"],
            "capital":    d["capital"][0],
            "population": d["population"],
            "currency":   list(d["currencies"].keys())[0],
            "languages":  list(d["languages"].values()),
            "flag":       d["flag"],
            "area_km2":   d["area"],
        }
    except Exception as e:
        print(f"  rest countries failed: {e}")
        return {}