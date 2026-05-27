# seasonal_analysis.py
# shows climate data and travel conditions per month for a region
# draws a graph with temperature, rainfall and a travelability score
# also pulls in chinese festivals and generates groq travel tips

import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import requests
from groq import Groq
from dotenv import load_dotenv
from WorldExplorer.config import REGIONS
from WorldExplorer.api_clients import get_climate_data

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def seasonal_analysis(region, profile=None):
    """
    main function - analyses a region month by month
    draws a climate + travelability graph and generates groq tips
    """
    if region not in REGIONS:
        print(f"  region '{region}' not found")
        return

    print(f"\nanalyzing {region}...")

    lat, lon = REGIONS[region]["coords"]
    climate  = get_climate_data(lat, lon)

    if not climate or "daily" not in climate:
        print("  climate data not available")
        return

    monthly       = get_monthly_averages(climate)
    travelability = get_travelability(monthly, profile)
    events        = get_events()
    tips          = get_tips(region, monthly, profile)

    draw_graph(region, monthly, travelability, profile, events)

    print("\ntravel tips from groq:")
    print(tips)

    return {
        "region":        region,
        "monthly":       monthly,
        "travelability": travelability,
        "events":        events,
        "tips":          tips,
    }


def get_monthly_averages(climate):
    # takes daily open-meteo data and averages it per month
    times = climate["daily"].get("time", [])
    temps = climate["daily"].get("temperature_2m_mean", [])
    rain  = climate["daily"].get("precipitation_sum", [])

    # group values by month number
    by_month_temp = {i: [] for i in range(1, 13)}
    by_month_rain = {i: [] for i in range(1, 13)}

    for i, date in enumerate(times):
        m = int(date[5:7])
        if i < len(temps) and temps[i] is not None:
            by_month_temp[m].append(temps[i])
        if i < len(rain) and rain[i] is not None:
            by_month_rain[m].append(rain[i])

    # average each month
    avg_temp = []
    avg_rain = []

    for m in range(1, 13):
        t = by_month_temp[m]
        r = by_month_rain[m]
        avg_temp.append(round(sum(t) / len(t), 1) if t else 0)
        avg_rain.append(round(sum(r) / len(r), 1) if r else 0)

    return {"temp": avg_temp, "rain": avg_rain}


def get_travelability(monthly, profile=None):
    # scores each month from 0-10 based on how good it is to travel
    # adjusts the score based on the traveller profile if given
    scores = []

    for i in range(12):
        temp  = monthly["temp"][i]
        rain  = monthly["rain"][i]
        score = 5  # neutral starting point

        # temperature
        if 18 <= temp <= 28:
            score += 3
        elif 12 <= temp <= 32:
            score += 1.5
        elif temp < 5 or temp > 35:
            score -= 2

        # rainfall
        if rain < 2:
            score += 2
        elif rain < 5:
            score += 1
        elif rain > 10:
            score -= 1.5
        elif rain > 15:
            score -= 2.5

        # profile specific tweaks
        if profile:
            interests = profile["interests"]

            if "sun_sea" in interests and temp >= 25:
                score += 1.5
            if "adventure" in interests and 10 <= temp <= 22:
                score += 1
            if "culture_history" in interests and i not in [5, 6, 7]:
                score += 0.5
            if "wellness_spa" in interests and 15 <= temp <= 25:
                score += 1

        scores.append(round(min(max(score, 0), 10), 1))

    return scores


def get_events():
    # grabs chinese public holidays from a free api (no key needed)
    # and adds some well known festivals manually
    events = []

    try:
        r = requests.get("https://date.nager.at/api/v3/PublicHolidays/2024/CN", timeout=10)
        r.raise_for_status()
        for h in r.json():
            events.append({
                "name":  h["name"],
                "month": int(h["date"][5:7]),
            })
    except Exception as e:
        print(f"  holidays api failed: {e}")

    # these big festivals are not always in the public api so we add them manually
    events += [
        {"name": "Spring Festival",        "month": 2},
        {"name": "Harbin Ice Festival",    "month": 1},
        {"name": "Dragon Boat Festival",   "month": 6},
        {"name": "Mid-Autumn Festival",    "month": 9},
        {"name": "Golden Week",            "month": 10},
        {"name": "Lantern Festival",       "month": 2},
        {"name": "Qingming Festival",      "month": 4},
    ]

    return events


def get_tips(region, monthly, profile=None):
    # asks groq for practical seasonal tips tailored to the profile
    temps = monthly["temp"]

    spring = round(sum(temps[2:5]) / 3, 1)
    summer = round(sum(temps[5:8]) / 3, 1)
    autumn = round(sum(temps[8:11]) / 3, 1)
    winter = round(sum(temps[11:12] + temps[0:2]) / 3, 1)

    interests = ", ".join(profile["interests"]) if profile else "general travel"
    company   = profile["company"] if profile else "any traveller"

    prompt = f"""
    Write short seasonal travel tips for {region}, China.
    Climate: Spring {spring}°C, Summer {summer}°C, Autumn {autumn}°C, Winter {winter}°C.
    Traveller likes: {interests}. Travelling as: {company}.
    Format exactly like this:
    Spring: one or two sentences.
    Summer: one or two sentences.
    Autumn: one or two sentences.
    Winter: one or two sentences.
    Be specific and practical, no fluff.
    """

    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"  groq tips failed: {e}")
        return "Best time to visit is spring (April-May) or autumn (September-October)."


def draw_graph(region, monthly, travelability, profile, events):
    # draws the combined climate + travelability graph and saves as png
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    fig.suptitle(f"Seasonal Analysis — {region}, China", fontsize=16, fontweight="bold")

    x = np.arange(12)

    # top graph - temperature line + rainfall bars
    ax1.plot(x, monthly["temp"], color="#e74c3c", linewidth=2.5,
             marker="o", markersize=5, label="Avg Temp (°C)")
    ax1.set_ylabel("Temperature (°C)", color="#e74c3c")
    ax1.tick_params(axis="y", labelcolor="#e74c3c")

    ax1b = ax1.twinx()
    ax1b.bar(x, monthly["rain"], color="#3498db", alpha=0.4, label="Avg Rain (mm)")
    ax1b.set_ylabel("Rainfall (mm)", color="#3498db")
    ax1b.tick_params(axis="y", labelcolor="#3498db")
    ax1.set_title("Climate", fontsize=12)
    ax1.grid(True, alpha=0.3)

    # add event markers as vertical dotted lines
    for ev in events:
        m = ev["month"] - 1
        ax1.axvline(x=m, color="purple", alpha=0.25, linestyle="--", linewidth=1)
        ax1.text(m + 0.05, max(monthly["temp"]) * 0.95,
                ev["name"][:14], rotation=90, fontsize=6, color="purple", alpha=0.8)

    # bottom graph - travelability bars
    colours = ["#e74c3c" if s < 4 else "#f39c12" if s < 6 else "#27ae60"
               for s in travelability]
    bars = ax2.bar(x, travelability, color=colours, alpha=0.85, edgecolor="white")
    ax2.set_ylabel("Travelability (0-10)")
    ax2.set_ylim(0, 10.5)
    ax2.set_xticks(x)
    ax2.set_xticklabels(MONTH_NAMES)
    ax2.set_title("Travelability Index", fontsize=12)
    ax2.grid(True, alpha=0.3, axis="y")

    # highlight the traveller's preferred months with a star
    if profile:
        month_map = {name[:3].lower(): i for i, name in enumerate(MONTH_NAMES)}
        for month in profile.get("travel_months", []):
            idx = month_map.get(month[:3].lower())
            if idx is not None:
                bars[idx].set_edgecolor("black")
                bars[idx].set_linewidth(2.5)
                ax2.text(idx, travelability[idx] + 0.3, "★",
                        ha="center", fontsize=13, color="black")

    # value labels on bars
    for bar, val in zip(bars, travelability):
        ax2.text(bar.get_x() + bar.get_width() / 2,
                val + 0.1, str(val), ha="center", va="bottom", fontsize=9)

    # legend
    patches = [
        mpatches.Patch(color="#27ae60", label="Great (7-10)"),
        mpatches.Patch(color="#f39c12", label="Ok (4-6)"),
        mpatches.Patch(color="#e74c3c", label="Avoid (0-3)"),
    ]
    ax2.legend(handles=patches, loc="upper right", fontsize=9)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1b.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=9)

    plt.tight_layout()

    os.makedirs("data", exist_ok=True)
    path = f"data/seasonal_{region.lower().replace(' ', '_')}.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"graph saved to {path}")