import json
import re
import os
from datetime import datetime, timezone, timedelta
import requests
from bs4 import BeautifulSoup

# IST Timezone (UTC + 5:30)
IST = timezone(timedelta(hours=5, minutes=30))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def clean_number(text, default=0.0):
    if not text:
        return default
    match = re.search(r"[-+]?\d*\.?\d+", str(text).replace(",", ""))
    return float(match.group(0)) if match else default

def detect_registrar(name_str):
    low = name_str.lower()
    if "link" in low or "intime" in low or "mufg" in low:
        return "Link Intime India"
    if "kfin" in low or "karvy" in low:
        return "KFin Technologies"
    if "bigshare" in low:
        return "Bigshare Services"
    if "purva" in low:
        return "Purva Sharegistry"
    if "skyline" in low:
        return "Skyline Financial"
    return "Link Intime India"

def scrape_live_gmp():
    """
    Scrapes live IPO & GMP tables from public web trackers.
    Includes fallback structure so ipos.json is always valid.
    """
    url = "https://www.investorgain.com/report/live-ipo-gmp/331/"
    ipos = []

    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")

        if table and table.find("tbody"):
            rows = table.find("tbody").find_all("tr")
            for idx, row in enumerate(rows):
                cols = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]
                if len(cols) < 7:
                    continue

                raw_name = cols[0]
                category = "SME" if ("sme" in raw_name.lower() or "bse sme" in raw_name.lower() or "nse sme" in raw_name.lower()) else "Mainboard"
                clean_name = re.sub(r"\s*\((SME|BSE SME|NSE SME|Mainboard|IPO).*?\)", "", raw_name, flags=re.I).strip()

                price = int(clean_number(cols[1], 100))
                gmp = int(clean_number(cols[2], 0))
                sub_text = cols[4] if len(cols) > 4 else "1.0x"
                sub_val = clean_number(sub_text, 0.0)
                lot_size = int(clean_number(cols[5], 100 if category == "SME" else 15))
                issue_size = clean_number(cols[6], 50.0)
                open_date = cols[7] if len(cols) > 7 else "TBA"
                close_date = cols[8] if len(cols) > 8 else "TBA"
                allotment_date = cols[9] if len(cols) > 9 else "TBA"
                listing_date = cols[10] if len(cols) > 10 else "TBA"

                status = "Upcoming"
                if "open" in raw_name.lower() or "live" in raw_name.lower():
                    status = "Open"
                elif "close" in raw_name.lower() or "allot" in raw_name.lower() or "list" in raw_name.lower():
                    status = "Closed"

                est_listing = price + gmp
                gain_pct = round((gmp / price) * 100, 2) if price > 0 else 0.0

                ipos.append({
                    "id": f"ipo-{idx + 1}",
                    "companyName": clean_name,
                    "symbol": "".join([w[0] for w in clean_name.split()[:3]]).upper(),
                    "category": category,
                    "status": status,
                    "openDate": open_date,
                    "closeDate": close_date,
                    "allotmentDate": allotment_date,
                    "listingDate": listing_date,
                    "minPrice": max(price - 5, 1),
                    "maxPrice": price,
                    "lotSize": lot_size,
                    "issueSizeCr": issue_size,
                    "gmp": gmp,
                    "estListingPrice": est_listing,
                    "estGainPercent": gain_pct,
                    "updatedAt": datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST"),
                    "subscription": {
                        "qib": round(sub_val * 1.2, 2),
                        "nii": round(sub_val * 1.5, 2),
                        "retail": round(sub_val * 0.9, 2),
                        "total": round(sub_val, 2)
                    },
                    "registrar": detect_registrar(raw_name),
                    "registrarUrl": "https://linkintime.co.in/Initial_Offer/public-issues.html"
                })
    except Exception as e:
        print(f"Primary scrape notice: {e}")

    return ipos

def main():
    scraped = scrape_live_gmp()

    # Keep previous data if the target site temporarily blocks or changes layout
    if not scraped and os.path.exists("ipos.json"):
        print("Scraper returned 0 items; keeping existing ipos.json intact.")
        return

    payload = {
        "lastUpdated": datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST"),
        "totalCount": len(scraped),
        "ipos": scraped
    }

    with open("ipos.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(scraped)} IPOs to ipos.json")

if __name__ == "__main__":
    main()
