# match_destinations.py
# scores all regions against the traveller profile and returns the top 5
# score is out of 100, split across 4 criteria


import profile
import time


import pandas as pd
import os
from dotenv import load_dotenv
from WorldExplorer.config import REGIONS
from WorldExplorer.api_clients import get_climate_data
load_dotenv()

# switched to groq - 
from groq import Groq
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))







def match_destinations(profile):
    """
    main function - scores every region and returns top 5 as a dataframe
    also saves results to csv for the node-red dashboard
    """
    print("\nfinding your best matches...")

    scores = []

    for name, data in REGIONS.items():
        total, breakdown = get_score(name, data, profile)
        scores.append({
            "region":    name,
            "score":     total,
            "breakdown": breakdown,
        })

    # sort high to low
    scores.sort(key=lambda x: x["score"], reverse=True)
    top5 = scores[:5]

    # add extra info and gemini motivation for each
    print("generating motivations...")
    # in match_destinations function, replace the motivation loop with this:
    import time
    for r in top5:
            region_data          = REGIONS[r["region"]]
            r["motivation"] = ask_groq(r["region"], r["score"], profile)
            r["avg_cost_night"]  = region_data["avg_cost_night"]
            r["airport"]         = region_data["airport"]
            r["airport_km"]      = region_data["airport_distance_km"]
            r["description"]     = region_data["description"]
            time.sleep(4)

    df = pd.DataFrame(top5)

        # save full version for python use
    os.makedirs("data", exist_ok=True)
    

        # save clean version for node-red - no breakdown column, no commas inside fields
    clean_df = pd.DataFrame([{
            "region":         r["region"],
            "score":          r["score"],
            "avg_cost_night": r["avg_cost_night"],
            "airport":        r["airport"],
            "airport_km":     r["airport_km"],
            "motivation":     r["motivation"][:100] if r["motivation"] else "",
        } for r in top5])
    clean_df.to_csv("data/top5_destinations.csv", index=False)
    print("results saved to data/top5_destinations.csv")

        # save profile
    profile_df = pd.DataFrame([{
            "budget":        profile["budget"],
            "travel_months": ", ".join(profile["travel_months"]),
            "days":          profile["days"],
            "interests":     ", ".join(profile["interests"]),
            "company":       profile["company"],
            "mobility":      profile["mobility"],
        }])
    profile_df.to_csv("data/current_profile.csv", index=False)

    show_results(top5)

    return df


# scoring - 4 criteria, max 100 points total

def get_score(name, data, profile):
    breakdown = {}
    total     = 0

    # interests - 40 points
    s, note = interests_score(data, profile)
    breakdown["interests"] = f"{s}/40 - {note}"
    total += s

    # budget - 20 points
    s, note = budget_score(data, profile)
    breakdown["budget"] = f"{s}/20 - {note}"
    total += s

    # climate - 25 points
    s, note = climate_score(data, profile)
    breakdown["climate"] = f"{s}/25 - {note}"
    total += s

    # travel company - 15 points
    s, note = company_score(data, profile)
    breakdown["company"] = f"{s}/15 - {note}"
    total += s

    return min(total, 100), breakdown


def interests_score(data, profile):
    region_tags    = set(data["tags"])
    user_interests = set(profile["interests"])
    overlap        = region_tags & user_interests

    if not user_interests:
        return 0, "no interests selected"

    ratio = len(overlap) / len(user_interests)
    score = round(ratio * 40)
    note  = f"matches: {', '.join(overlap)}" if overlap else "no overlap"

    return score, note


def budget_score(data, profile):
    levels = {"backpacker": 0, "mid_range": 1, "luxury": 2}
    diff   = abs(levels.get(data["budget"], 1) - levels.get(profile["budget"], 1))

    if diff == 0:
        return 20, "perfect match"
    elif diff == 1:
        return 10, "close match"
    else:
        return 0, "too far apart"


def climate_score(data, profile):
    coords  = data["coords"]
    climate = get_climate_data(coords[0], coords[1])

    if not climate or "daily" not in climate:
        return 12, "no climate data"

    temps = climate["daily"].get("temperature_2m_mean", [])
    times = climate["daily"].get("time", [])

    if not temps or not times:
        return 12, "no temperature data"

    month_map = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12
    }

    selected = [month_map[m.lower()] for m in profile["travel_months"] if m.lower() in month_map]

    month_temps = []
    for i, date in enumerate(times):
        # date is like "2020-04-01", grab the month part and convert to int
        month_num = int(date[5:7])
        if month_num in selected and i < len(temps) and temps[i] is not None:
            month_temps.append(temps[i])

    if not month_temps:
        return 12, "no data for selected months"

    avg = sum(month_temps) / len(month_temps)

    if 18 <= avg <= 28:
        return 25, f"great temp ({avg:.1f}°C)"
    elif 12 <= avg <= 32:
        return 17, f"ok temp ({avg:.1f}°C)"
    elif 5 <= avg <= 35:
        return 8, f"not ideal ({avg:.1f}°C)"
    else:
        return 3, f"too extreme ({avg:.1f}°C)"
    

def company_score(data, profile):
    # which region tags suit each type of travel company
    good_for = {
        "family_kids":  ["sun_sea", "nature_wildlife", "culture_history"],
        "couple":       ["wellness_spa", "gastronomy", "citytrip", "sun_sea"],
        "solo":         ["backpacker", "adventure", "culture_history"],
        "friend_group": ["adventure", "citytrip", "gastronomy", "backpacker"],
    }

    suitable = good_for.get(profile["company"], [])
    matches  = [t for t in data["tags"] if t in suitable]

    if len(matches) >= 2:
        return 15, f"great for {profile['company'].replace('_', ' ')}"
    elif len(matches) == 1:
        return 8,  f"ok for {profile['company'].replace('_', ' ')}"
    else:
        return 3,  f"not ideal for {profile['company'].replace('_', ' ')}"


def ask_groq(region, score, profile):
    interests = ", ".join(profile["interests"])
    months    = ", ".join(profile["travel_months"])

    prompt = f"""
    Write 2-3 short sentences explaining why {region} in China is a good travel match.
    The traveller likes: {interests}.
    Travelling in {months} with a {profile["budget"]} budget as a {profile["company"]}.
    Match score: {score}/100. Be enthusiastic but keep it short and natural.
    """

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"  groq failed for {region}: {e}")
        return f"{region} is a great match for your travel style!"


def show_results(top5):
    print("\n" + "=" * 50)
    print("your top 5 destinations in China")
    print("=" * 50)

    for i, r in enumerate(top5, 1):
        print(f"\n{i}. {r['region']} — {r['score']}/100")
        print(f"   airport: {r['airport']} ({r['airport_km']} km away)")
        print(f"   avg cost per night: €{r['avg_cost_night']}")
        print(f"   {r['motivation']}")
        print(f"   score breakdown:")
        for k, v in r["breakdown"].items():
            print(f"     {k}: {v}")