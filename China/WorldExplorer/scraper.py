# scraper.py
# scraping data from 3 websites for WorldExplorer
# wikivoyage, numbeo and travelchinaguide

import requests
import time
from bs4 import BeautifulSoup


# just a basic header so we don't get blocked right away
HEADERS = {
    "User-Agent": "Usman/420"
}


def get_page(url):
    # wait a bit between requests, otherwise sites block you
    time.sleep(1.5)
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"failed to load {url} - {e}")
        return None


# --- wikivoyage ---
# good free source, has info on basically every city in China

def scrape_wikivoyage(region):
    url  = f"https://en.wikivoyage.org/wiki/{region.replace(' ', '_')}"
    soup = get_page(url)

    if not soup:
        return {}

    data = {
        "description":   "",
        "things_to_see": [],
        "things_to_do":  [],
        "highlights":    [],
    }

    for div in soup.find_all("div", {"class": "mw-heading"}):
        title = div.get_text(strip=True).replace("[edit]", "").strip()

        if title == "Understand":
            # description is inside the first section under Understand
            sib = div.find_next_sibling()
            while sib:
                if sib.name == "div" and "mw-heading" in sib.get("class", []):
                    break
                if sib.name == "section":
                    text = sib.get_text(strip=True)
                    text = text.replace("[edit]", "").strip()
                    # skip climate and orientation sections
                    if len(text) > 100 and not text.startswith("Climate") and not text.startswith("Orientation"):
                        # clean the heading word from the start
                        for word in ["History", "People", "Understand"]:
                            if text.startswith(word):
                                text = text[len(word):].strip()
                        data["description"] = text[:400]
                        break
                sib = sib.find_next_sibling()

        elif title == "See":
            sib = div.find_next_sibling()
            while sib:
                if sib.name == "div" and "mw-heading" in sib.get("class", []):
                    break
                if sib.name == "section":
                    heading = sib.find(["h2", "h3", "h4"])
                    if heading:
                        name = heading.get_text(strip=True).replace("[edit]", "").strip()
                        if name:
                            data["things_to_see"].append(name)
                sib = sib.find_next_sibling()

        elif title == "Do":
            data["things_to_do"] = grab_list(div)

        elif title in ("Eat", "Buy"):
            # grab paragraph text and section headings as highlights
            sib = div.find_next_sibling()
            while sib:
                if sib.name == "div" and "mw-heading" in sib.get("class", []):
                    break
                if sib.name == "p":
                    text = sib.get_text(strip=True)
                    if len(text) > 30:
                        data["highlights"].append(text[:80])
                if sib.name == "section":
                    heading = sib.find(["h2", "h3", "h4"])
                    if heading:
                        name = heading.get_text(strip=True).replace("[edit]", "").strip()
                        if name and len(name) > 3:
                            data["highlights"].append(name)
                sib = sib.find_next_sibling()

        if len(data["highlights"]) >= 10:
            break

    return data


def grab_list(heading):
    items   = []
    sibling = heading.find_next_sibling()

    while sibling:
        if sibling.name == "div" and "mw-heading" in sibling.get("class", []):
            break

        if sibling.name in ("ul", "dl"):
            for li in sibling.find_all(["li", "dt"], recursive=False):
                text = li.get_text(strip=True)
                # cut at colon if there is one
                if ":" in text:
                    text = text.split(":")[0].strip()
                # also cut at newline
                text = text.split("\n")[0].strip()
                # skip if too short or too long
                if 3 < len(text) < 80:
                    items.append(text)

        sibling = sibling.find_next_sibling()

    return items[:10]

# --- numbeo ---
# has cost of living data per city, useful for budget scoring

def scrape_numbeo(city):
    url  = f"https://www.numbeo.com/cost-of-living/in/{city.replace(' ', '-')}"
    soup = get_page(url)

    if not soup:
        return {}

    prices = {}

    table = soup.find("table", {"class": "data_wide_table"})
    if not table:
        return {}

    for row in table.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) >= 2:
            name  = cols[0].get_text(strip=True)
            price = cols[1].get_text(strip=True)

            # only keep the stuff that's relevant for travellers
            if any(word in name for word in ["Meal", "Hotel", "McMeal", "water", "beer"]):
                prices[name] = price

    return prices


# --- wikipedia ---
# replaced travelchinaguide which blocked us (403)

def scrape_wikipedia(region):
    url  = f"https://en.wikipedia.org/wiki/{region.replace(' ', '_')}"
    soup = get_page(url)

    if not soup:
        return {}

    data = {"best_time": ""}

    content = soup.find("div", {"id": "mw-content-text"})
    if not content:
        return data

    # just grab climate info, that's all wikipedia is reliable for here
    for p in content.find_all("p"):
        text = p.get_text(strip=True)
        if "climate" in text.lower() and len(text) > 80:
            data["best_time"] = text[:300]
            break

    return data

# --- main function ---
# this is what the other files will call

def scrape_region(region):
    print(f"scraping data for {region}...")

    wiki = scrape_wikivoyage(region)
    numb = scrape_numbeo(region)
    wp   = scrape_wikipedia(region)

    return {
        "region":        region,
        "description":   wiki.get("description", ""),
        "things_to_see": wiki.get("things_to_see", []),
        "things_to_do":  wiki.get("things_to_do", []),
        "highlights":    wiki.get("highlights", []),
        "prices":        numb,
        "best_time":     wp.get("best_time", ""),
    }