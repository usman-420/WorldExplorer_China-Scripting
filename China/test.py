from WorldExplorer.traveller_profile import traveller_profile
from WorldExplorer.match_destinations import match_destinations

profile = traveller_profile()
df = match_destinations(profile)
print(df)