# attractions_map.py
# builds an interactive folium map with tourist attractions
# markers are colour coded by travel profile
# heatmap layer shows how popular/busy each area is

import folium
import time
from folium.plugins import HeatMap
from WorldExplorer.config import REGIONS, PROFILES, PROFILE_COLOURS
from WorldExplorer.api_clients import get_attractions, get_attraction_details


def attractions_map(profile=None, region=None):
    """
    generates an interactive folium map with attractions
    filtered by profile and/or region if provided
    saves result as html file
    """

    # decide which regions to show
    if region:
        regions_to_show = {region: REGIONS[region]}
    else:
        regions_to_show = REGIONS

    # centre map on China
    m = folium.Map(location=(35.8617, 104.1954), zoom_start=5, tiles="CartoDB positron")

    # add title
    title = "WorldExplorer — China"
    if profile:
        title += f" | {', '.join(profile['interests'])}"

    m.get_root().html.add_child(folium.Element(f"""
        <div style="position:fixed; top:10px; left:50%; transform:translateX(-50%);
        z-index:1000; background:white; padding:10px 20px; border-radius:8px;
        box-shadow:0 2px 6px rgba(0,0,0,0.3); font-family:Arial; font-size:14px; font-weight:bold;">
        {title}
        </div>
    """))

    # add legend
    m.get_root().html.add_child(folium.Element(make_legend()))

    heatmap_points  = []
    category_counts = {}
    total           = 0

    print("\nbuilding map...")

    for region_name, region_data in regions_to_show.items():
        lat, lon = region_data["coords"]
        print(f"  getting attractions for {region_name}...")

        places = get_attractions(lat, lon, radius=20000)
        time.sleep(0.5)

        if not places:
            continue

        for place in places:
            name  = place.get("name", "").strip()
            kinds = place.get("kinds", "")
            plat  = place["point"]["lat"]
            plon  = place["point"]["lon"]

            if not name:
                continue

            category = map_category(kinds)

            # if profile given, skip attractions that don't match interests
            if profile and category not in profile["interests"]:
                continue

            category_counts[category] = category_counts.get(category, 0) + 1
            colour = PROFILE_COLOURS.get(category, "gray")

            # get extra details for the popup
            xid     = place.get("xid", "")
            details = get_attraction_details(xid) if xid else {}
            time.sleep(0.3)

            folium.Marker(
                location=[plat, plon],
                popup=folium.Popup(make_popup(name, category, details, region_name), max_width=280),
                tooltip=name,
                icon=folium.Icon(color=colour, icon="info-sign")
            ).add_to(m)

            heatmap_points.append([plat, plon, place.get("rate", 1)])
            total += 1

    # heatmap layer
    if heatmap_points:
        HeatMap(heatmap_points, radius=25, blur=15, name="Popularity").add_to(m)

    folium.LayerControl().add_to(m)

    # info bar showing counts per category (only when profile is given)
    if profile and category_counts:
        m.get_root().html.add_child(folium.Element(make_info_bar(category_counts)))

    output = "data/attractions_map.html"
    m.save(output)

    print(f"map saved to {output}")
    print(f"total markers: {total}")

    if category_counts:
        for cat, count in category_counts.items():
            print(f"  {PROFILES.get(cat, cat)}: {count}")

    return m


def map_category(kinds):
    k = kinds.lower()

    if any(w in k for w in ["beach", "water", "diving", "surf"]):
        return "sun_sea"
    elif any(w in k for w in ["hiking", "climbing", "sport", "adventure"]):
        return "adventure"
    elif any(w in k for w in ["museum", "historic", "monument", "unesco", "temple", "castle", "fort", "ruins"]):
        return "culture_history"
    elif any(w in k for w in ["nature", "park", "wildlife", "forest", "mountain", "garden"]):
        return "nature_wildlife"
    elif any(w in k for w in ["architecture", "urban", "city", "street", "tower"]):
        return "citytrip"
    elif any(w in k for w in ["restaurant", "food", "market"]):
        return "gastronomy"
    elif any(w in k for w in ["spa", "wellness", "yoga", "hot_spring"]):
        return "wellness_spa"
    elif any(w in k for w in ["interesting_places", "tourist"]):
        # interesting_places is the most common opentripmap tag
        # assign it to culture_history as a sensible default
        return "culture_history"
    else:
        return "culture_history"

def make_popup(name, category, details, region):
    # builds the popup html for each marker
    label       = PROFILES.get(category, category)
    description = ""
    rating      = "n/a"
    link        = ""

    if details:
        wiki = details.get("wikipedia_extracts", {})
        if wiki:
            description = wiki.get("text", "")[:200] + "..."
        rating = details.get("rate", "n/a")
        url    = details.get("url", "")
        if url:
            link = f'<a href="{url}" target="_blank">more info</a>'

    return f"""
    <div style="font-family:Arial; font-size:12px; width:250px;">
        <b style="font-size:14px;">{name}</b><br>
        <span style="color:gray;">{region}</span><br><br>
        <b>Category:</b> {label}<br>
        <b>Rating:</b> {rating}<br><br>
        <p style="color:#444;">{description}</p>
        {link}
    </div>
    """


def make_legend():
    # colour legend bottom left of the map
    items = ""
    for key, label in PROFILES.items():
        colour = PROFILE_COLOURS.get(key, "gray")
        items += f"""
        <div style="display:flex; align-items:center; margin:4px 0;">
            <div style="width:12px; height:12px; background:{colour};
            border-radius:50%; margin-right:8px;"></div>
            <span>{label}</span>
        </div>
        """

    return f"""
    <div style="position:fixed; bottom:30px; left:10px; z-index:1000;
    background:white; padding:12px; border-radius:8px;
    box-shadow:0 2px 6px rgba(0,0,0,0.3); font-family:Arial; font-size:12px;">
        <b>Categories</b><br><br>{items}
    </div>
    """


def make_info_bar(category_counts):
    # small bar at the top showing how many attractions per category
    items = ""
    for cat, count in category_counts.items():
        colour = PROFILE_COLOURS.get(cat, "gray")
        label  = PROFILES.get(cat, cat)
        items += f"""
        <div style="display:inline-block; margin:0 10px; text-align:center;">
            <div style="width:10px; height:10px; background:{colour};
            border-radius:50%; display:inline-block; margin-right:4px;"></div>
            <b>{label}:</b> {count}
        </div>
        """

    return f"""
    <div style="position:fixed; top:60px; left:50%; transform:translateX(-50%);
    z-index:1000; background:white; padding:8px 16px; border-radius:8px;
    box-shadow:0 2px 6px rgba(0,0,0,0.3); font-family:Arial; font-size:12px;">
        <b>Attractions found:</b> {items}
    </div>
    """