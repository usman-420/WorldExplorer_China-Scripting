# config.py
# All the China-specific settings for WorldExplorer
# Other files import from here so nothing is hardcoded

COUNTRY = "China"
CURRENCY = "Yuan (CNY)"

# The 8 regions we support with their basic info
# coords = (latitude, longitude) for map and weather API calls
REGIONS = {
    "Beijing": {
        "coords": (39.9042, 116.4074),
        "airport": "PEK",
        "airport_distance_km": 25,
        "tags": ["culture_history", "citytrip", "gastronomy"],
        "budget": "mid_range",
        "description": "Ancient capital with the Great Wall and Forbidden City.",
        "avg_cost_night": 80,
    },
    "Shanghai": {
        "coords": (31.2304, 121.4737),
        "airport": "PVG",
        "airport_distance_km": 30,
        "tags": ["citytrip", "gastronomy", "wellness_spa"],
        "budget": "luxury",
        "description": "Modern megacity with iconic skyline, street food and nightlife.",
        "avg_cost_night": 120,
    },
    "Yunnan": {
        "coords": (25.0453, 102.7098),
        "airport": "KMG",
        "airport_distance_km": 15,
        "tags": ["nature_wildlife", "adventure", "culture_history", "backpacker"],
        "budget": "backpacker",
        "description": "Mountains, ethnic villages and the famous Tiger Leaping Gorge.",
        "avg_cost_night": 30,
    },
    "Sichuan": {
        "coords": (30.6524, 104.0658),
        "airport": "CTU",
        "airport_distance_km": 16,
        "tags": ["nature_wildlife", "gastronomy", "adventure"],
        "budget": "mid_range",
        "description": "Giant pandas, spicy hotpot and sacred Buddhist mountains.",
        "avg_cost_night": 50,
    },
    "Guilin": {
        "coords": (25.2736, 110.2900),
        "airport": "KWL",
        "airport_distance_km": 28,
        "tags": ["nature_wildlife", "adventure", "backpacker"],
        "budget": "backpacker",
        "description": "Karst peaks and the Li River — one of China's most scenic regions.",
        "avg_cost_night": 35,
    },
    "Hainan": {
        "coords": (20.0458, 110.3417),
        "airport": "HAK",
        "airport_distance_km": 25,
        "tags": ["sun_sea", "wellness_spa", "gastronomy"],
        "budget": "mid_range",
        "description": "China's tropical island with beaches, surf and spa resorts.",
        "avg_cost_night": 70,
    },
    "Xian": {
        "coords": (34.3416, 108.9398),
        "airport": "XIY",
        "airport_distance_km": 47,
        "tags": ["culture_history", "gastronomy"],
        "budget": "mid_range",
        "description": "Silk Road city famous for the Terracotta Army and Muslim Quarter food.",
        "avg_cost_night": 55,
    },
    "Tibet": {
        "coords": (29.6465, 91.1171),
        "airport": "LXA",
        "airport_distance_km": 62,
        "tags": ["adventure", "culture_history", "nature_wildlife", "wellness_spa"],
        "budget": "mid_range",
        "description": "The Roof of the World — monasteries, high altitude and raw nature.",
        "avg_cost_night": 60,
    },
    "Zhangjiajie": {
        "coords": (29.1255, 110.4794),
        "airport": "DYG",
        "airport_distance_km": 30,
        "tags": ["nature_wildlife", "adventure"],
        "budget": "mid_range",
        "description": "The floating Avatar mountains and glass bridge capital of China.",
        "avg_cost_night": 45,
    },
    "Hangzhou": {
        "coords": (30.2741, 120.1551),
        "airport": "HGH",
        "airport_distance_km": 30,
        "tags": ["wellness_spa", "nature_wildlife", "culture_history"],
        "budget": "mid_range",
        "description": "West Lake, tea plantations and one of China's most relaxing cities.",
        "avg_cost_night": 65,
    },
}

# The 8 traveller profiles from the assignment
# key = used in code, label = shown to the user
PROFILES = {
    "sun_sea":         "Sun & Sea",
    "adventure":       "Adventure",
    "culture_history": "Culture & History",
    "nature_wildlife": "Nature & Wildlife",
    "citytrip":        "Citytrip",
    "gastronomy":      "Gastronomy",
    "wellness_spa":    "Wellness & Spa",
    "backpacker":      "Backpacker/Budget",
}

# Colours for the folium map markers — one per profile
PROFILE_COLOURS = {
    "sun_sea":         "blue",
    "adventure":       "orange",
    "culture_history": "red",
    "nature_wildlife": "green",
    "citytrip":        "purple",
    "gastronomy":      "beige",
    "wellness_spa":    "pink",
    "backpacker":      "gray",
}

# Budget options
BUDGETS = {
    "backpacker": "Backpacker  (under €30/night)",
    "mid_range":  "Mid-range   (€30 – €100/night)",
    "luxury":     "Luxury      (over €100/night)",
}

# Travel company options
COMPANY = {
    "solo":         "Solo",
    "couple":       "Couple",
    "family_kids":  "Family with kids",
    "friend_group": "Friend group",
}

# How they want to get around
MOBILITY = {
    "public_transport": "Public transport",
    "rent_car":         "Rent a car",
    "cycling":          "Cycling",
}

# Month names — used for travel period selection
MONTHS = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]