# WorldExplorer — China 🇨🇳

A smart travel guide for China built as a take-home scripting exam project.
You fill in your travel profile and the package finds the best destinations for you.

## What it does

- Asks you a few questions about your travel style (budget, interests, travel month etc.)
- Scores all regions in China and gives you a personalised top 5
- Shows an interactive map with attractions near your top destinations
- Analyses the climate per region and tells you the best time to go
- Generates a Node-RED dashboard so you can explore everything visually

## Project structure

China/
├── WorldExplorer/
│   ├── config.py                  # all China regions and settings
│   ├── traveller_profile.py       # asks the user questions and builds a profile
│   ├── scraper.py                 # scrapes WikiVoyage, Numbeo and Wikipedia
│   ├── api_clients.py             # Open-Meteo, OpenTripMap, REST Countries
│   ├── match_destinations.py      # scores regions and returns top 5
│   ├── attractions_map.py         # builds a folium map with attractions
│   ├── seasonal_analysis.py       # climate graphs and travel tips
│   └── country_dashboard_data.py  # exports data to CSV and SQLite
├── data/                          # all exported CSV files and database
├── node-red/                      # Node-RED dashboard flow and screenshot
├── demo.ipynb                     # run this to see everything in action
├── run_match.py                   # called by Node-RED to run the scoring
└── requirements.txt

## How to run it

1. Clone the repo and go into the China folder:
```bash
git clone https://github.com/usman-420/WorldExplorer_China-Scripting.git
cd WorldExplorer_China-Scripting/China
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:

OPENTRIPMAP_API_KEY=your_key
GROQ_API_KEY=your_key

4. Open `demo.ipynb` in Jupyter and run all cells

## Data sources

| Source | What we get |
|---|---|
| WikiVoyage | Region descriptions, things to see and do |
| Numbeo | Meal prices and budget info per city |
| Wikipedia | Climate descriptions |
| Open-Meteo | Historical weather data (free, no key needed) |
| OpenTripMap | Geolocated tourist attractions |
| REST Countries | General country info |
| Public Holidays API | Chinese public holidays and festivals |
| Groq (Llama 3) | AI-generated travel tips and destination motivations |

## Node-RED dashboard

Make sure Node-RED is installed, then:
```bash
node-red
```

Import `node-red/node_red_flow.json` and open `http://localhost:1880/ui`

## Notes

- Built with Python 3.14
- Free APIs only, no paywalled sources
- Scraping done respectfully with delays and proper headers