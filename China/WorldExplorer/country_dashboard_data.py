# country_dashboard_data.py
# collects all data and exports it to csv files for the node-red dashboard
# also does some basic quality checks on the data

import os
import pandas as pd
import sqlite3
import logging
from WorldExplorer.config import REGIONS, PROFILES
from WorldExplorer.scraper import scrape_region
from WorldExplorer.api_clients import get_attractions, get_country_info

# setup a simple logger so we can track warnings and issues
logging.basicConfig(
    filename="data/dashboard_log.txt",
    level=logging.WARNING,
    format="%(asctime)s - %(message)s"
)


def country_dashboard_data(profile=None):
    """
    main function - gathers all data and exports to csv files
    if a profile is given, exports are filtered for that traveller type
    """
    print("\ngathering dashboard data...")
    os.makedirs("data", exist_ok=True)

    # get basic country info
    country_info = get_country_info()
    print(f"  country: {country_info.get('name', 'China')}")

    # scrape all regions
    all_regions = scrape_all_regions()

    # build the different datasets
    attractions_df  = build_attractions_data(profile)
    budget_df       = build_budget_data(all_regions)
    mustsee_df      = build_mustsee_data(all_regions)
    stats_df        = build_stats(all_regions, attractions_df)

    # quality check before saving
    quality_check(attractions_df, "attractions")
    quality_check(budget_df,      "budget")
    quality_check(mustsee_df,     "must-sees")

    # save to csv
    save_csv(attractions_df, "data/dashboard_attractions.csv")
    save_csv(budget_df,      "data/dashboard_budget.csv")
    save_csv(mustsee_df,     "data/dashboard_mustsees.csv")
    save_csv(stats_df,       "data/dashboard_stats.csv")

    # also save to sqlite so node-red can query it
    save_to_db(attractions_df, budget_df, mustsee_df, stats_df)

    print("\nall exports done!")
    print("files saved:")
    print("  data/dashboard_attractions.csv")
    print("  data/dashboard_budget.csv")
    print("  data/dashboard_mustsees.csv")
    print("  data/dashboard_stats.csv")
    print("  data/worldexplorer.db")

    return {
        "attractions": attractions_df,
        "budget":      budget_df,
        "mustsees":    mustsee_df,
        "stats":       stats_df,
    }


def scrape_all_regions():
    # scrapes wikivoyage and numbeo for all regions
    # returns a list of dicts with region data
    results = []
    for name in REGIONS:
        print(f"  scraping {name}...")
        data = scrape_region(name)
        data["region"] = name
        results.append(data)
    return results


def build_attractions_data(profile=None):
    # fetches attractions from opentripmap for all regions
    # filters by profile if given
    rows = []

    for name, region_data in REGIONS.items():
        lat, lon = region_data["coords"]
        places   = get_attractions(lat, lon)

        for p in places:
            place_name = p.get("name", "").strip()
            if not place_name:
                continue

            kinds    = p.get("kinds", "")
            category = guess_category(kinds)

            # filter by profile interests if given
            if profile and category not in profile["interests"]:
                continue

            rows.append({
                "region":   name,
                "name":     place_name,
                "category": category,
                "lat":      p["point"]["lat"],
                "lon":      p["point"]["lon"],
                "rating":   p.get("rate", 0),
                "kinds":    kinds,
            })

    df = pd.DataFrame(rows)
    return df


def build_budget_data(all_regions):
    # builds a table of accommodation and meal costs per region
    rows = []

    for data in all_regions:
        region = data["region"]
        prices = data.get("prices", {})

        # get avg cost per night from config
        avg_night = REGIONS[region]["avg_cost_night"]

        # get meal prices from numbeo scrape
        cheap_meal  = ""
        midrange    = ""
        fastfood    = ""

        for key, val in prices.items():
            if "Inexpensive" in key:
                cheap_meal = val
            elif "Mid-Range" in key:
                midrange = val
            elif "McMeal" in key or "Fast" in key:
                fastfood = val

        rows.append({
            "region":           region,
            "budget_level":     REGIONS[region]["budget"],
            "avg_cost_night":   avg_night,
            "cheap_meal":       cheap_meal,
            "midrange_meal":    midrange,
            "fastfood_meal":    fastfood,
        })

    return pd.DataFrame(rows)


def build_mustsee_data(all_regions):
    # builds the must-sees vs hidden gems table
    # must-sees = well known highlights from config
    # hidden gems = less obvious spots from wikivoyage scrape
    rows = []

    for data in all_regions:
        region = data["region"]

        # highlights from config are the well known must-sees
        highlights = REGIONS[region].get("highlights", [])
        for h in highlights:
            rows.append({
                "region":   region,
                "name":     h,
                "type":     "must-see",
                "tags":     ", ".join(REGIONS[region]["tags"]),
            })

        # things to see from wikivoyage are more specific/niche
        for item in data.get("things_to_see", []):
            if item not in highlights:
                rows.append({
                    "region":   region,
                    "name":     item,
                    "type":     "hidden gem",
                    "tags":     ", ".join(REGIONS[region]["tags"]),
                })

    return pd.DataFrame(rows)


def build_stats(all_regions, attractions_df):
    # calculates summary statistics per region
    rows = []

    for data in all_regions:
        region = data["region"]

        # count attractions per region from the api data
        if not attractions_df.empty and "region" in attractions_df.columns:
            region_attractions = attractions_df[attractions_df["region"] == region]
            attraction_count   = len(region_attractions)
            avg_rating         = round(region_attractions["rating"].mean(), 1) if not region_attractions.empty else 0
        else:
            attraction_count = 0
            avg_rating       = 0

        rows.append({
            "region":            region,
            "attraction_count":  attraction_count,
            "avg_rating":        avg_rating,
            "things_to_see":     len(data.get("things_to_see", [])),
            "things_to_do":      len(data.get("things_to_do", [])),
            "avg_cost_night":    REGIONS[region]["avg_cost_night"],
            "budget_level":      REGIONS[region]["budget"],
            "profile_tags":      ", ".join(REGIONS[region]["tags"]),
        })

    return pd.DataFrame(rows)


def quality_check(df, name):
    # checks for missing values and logs warnings
    if df is None or df.empty:
        logging.warning(f"{name} dataframe is empty")
        print(f"  warning: {name} data is empty")
        return

    missing = df.isnull().sum()
    for col, count in missing.items():
        if count > 0:
            logging.warning(f"{name} - column '{col}' has {count} missing values")
            print(f"  warning: {name}.{col} has {count} missing values")

    print(f"  quality check passed for {name} ({len(df)} rows)")


def save_csv(df, path):
    # saves a dataframe to csv, skips if empty
    if df is None or df.empty:
        print(f"  skipping {path} - no data")
        return
    df.to_csv(path, index=False)
    print(f"  saved {path} ({len(df)} rows)")


def save_to_db(attractions, budget, mustsees, stats):
    # saves all dataframes to a sqlite database
    # node-red can query this directly
    db_path = "data/worldexplorer.db"

    try:
        conn = sqlite3.connect(db_path)

        if not attractions.empty:
            attractions.to_sql("attractions", conn, if_exists="replace", index=False)
        if not budget.empty:
            budget.to_sql("budget", conn, if_exists="replace", index=False)
        if not mustsees.empty:
            mustsees.to_sql("mustsees", conn, if_exists="replace", index=False)
        if not stats.empty:
            stats.to_sql("stats", conn, if_exists="replace", index=False)

        conn.close()
        print(f"  saved to {db_path}")

    except Exception as e:
        print(f"  db save failed: {e}")
        logging.error(f"db save failed: {e}")


def guess_category(kinds):
    # same as in attractions_map.py - maps opentripmap kinds to our categories
    k = kinds.lower()

    if any(w in k for w in ["beach", "water", "diving"]):
        return "sun_sea"
    elif any(w in k for w in ["hiking", "climbing", "sport"]):
        return "adventure"
    elif any(w in k for w in ["museum", "historic", "monument", "temple"]):
        return "culture_history"
    elif any(w in k for w in ["nature", "park", "wildlife", "forest"]):
        return "nature_wildlife"
    elif any(w in k for w in ["architecture", "urban", "city"]):
        return "citytrip"
    elif any(w in k for w in ["restaurant", "food", "market"]):
        return "gastronomy"
    elif any(w in k for w in ["spa", "wellness"]):
        return "wellness_spa"
    else:
        return "culture_history"