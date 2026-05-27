from WorldExplorer.traveller_profile import traveller_profile
from WorldExplorer.country_dashboard_data import country_dashboard_data

profile = traveller_profile()
data    = country_dashboard_data(profile=profile)

print("\nstats table:")
print(data["stats"])

print("\nmustsees table:")
print(data["mustsees"])