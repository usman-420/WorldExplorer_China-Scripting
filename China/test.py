from WorldExplorer.api_clients import get_climate_data, get_attractions, get_country_info
from WorldExplorer.config import REGIONS

# test 1 - climate for Beijing
coords = REGIONS["Beijing"]["coords"]
climate = get_climate_data(coords[0], coords[1])
print("climate keys:", climate.keys())

# test 2 - attractions for Beijing
attractions = get_attractions(coords[0], coords[1])
print("attractions found:", len(attractions))
if attractions:
    print("first attraction:", attractions[0])

# test 3 - country info
info = get_country_info()
print("country info:", info)