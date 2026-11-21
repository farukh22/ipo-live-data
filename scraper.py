import json
import re
import urllib.request
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser

IST = timezone(timedelta(hours=5, minutes=30))

REGISTRAR_URLS = {
    "Link Intime India": "https://in.mpms.mufg.com/Initial_Offer/public-issues.html",
    "MUFG Intime India": "https://in.mpms.mufg.com/Initial_Offer/public-issues.html",
    "KFin Technologies": "https://kosmic.kfintech.com/ipostatus/",
    "Bigshare Services": "https://ipo.bigshareonline.com/IPO_Status.html",
    "Purva Sharegistry": "https://www.purvashare.com/investor-service/ipo-query",
    "Skyline Financial": "https://www.skylinerta.com/ipo.php",
    "Maashitla Securities": "https://maashitla.com/allotment-status/public-issues",
    "Mas Services": "https://www.masserv.com/opt.asp",
}

BASE_IPOS = [
    {
        "id": "mahanadi-coalfields-mainboard",
        "companyName": "Mahanadi Coalfields Ltd",
        "symbol": "MCL",
        "category": "Mainboard",
        "subCategory": "Mainboard",
        "status": "Open",
        "statusNote": "Closes in 2 days",
        "openDate": "19 Nov 2026",
        "closeDate": "23 Nov 2026",
        "allotmentDate": "24 Nov 2026",
        "listingDate": "26 Nov 2026",
        "minPrice": 129,
        "maxPrice": 136,
        "lotSize": 110,
        "issueSizeCr": 4500.0,
        "gmp": 37,
        "gmpTrend": "up",
        "estListingPrice": 173,
        "estGainPercent": 27.21,
        "listingPrice": 173.0,
        "currentPrice": 175.4,
        "leadManager": "SEBI Registered Merchant Banker",
        "registrar": "KFin Technologies",
        "registrarUrl": REGISTRAR_URLS["KFin Technologies"],
        "subscription": {"qib": 0.65, "nii": 0.52, "retail": 0.35, "total": 0.49},
    },
    {
        "id": "crystal-crop-protection-mainboard",
        "companyName": "Crystal Crop Protection Ltd",
        "symbol": "CCPL",
        "category": "Mainboard",
        "subCategory": "Mainboard",
        "status": "Closed",
        "statusNote": "Awaiting allotment",
        "openDate": "18 Nov 2026",
        "closeDate": "20 Nov 2026",
        "allotmentDate": "22 Nov 2026",
        "listingDate": "25 Nov 2026",
        "minPrice": 259,
        "maxPrice": 272,
        "lotSize": 55,
        "issueSizeCr": 1200.0,
        "gmp": 14,
        "gmpTrend": "up",
        "estListingPrice": 286,
        "estGainPercent": 5.15,
        "listingPrice": 286.0,
        "currentPrice": 289.5,
        "leadManager": "SEBI Registered Merchant Banker",
        "registrar": "Link Intime India",
        "registrarUrl": REGISTRAR_URLS["Link Intime India"],
        "subscription": {"qib": 21.4, "nii": 18.2, "retail": 9.71, "total": 17.68},
    },
    {
        "id": "watrana-rentals-sme",
        "companyName": "Watrana Rentals Ltd",
        "symbol": "WRL",
        "category": "SME",
        "subCategory": "NSE SME",
        "status": "Open",
        "statusNote": "Closes in 2 days",
        "openDate": "19 Nov 2026",
        "closeDate": "23 Nov 2026",
        "allotmentDate": "24 Nov 2026",
        "listingDate": "26 Nov 2026",
        "minPrice": 232,
        "maxPrice": 245,
        "lotSize": 600,
        "issueSizeCr": 48.0,
        "gmp": 65,
        "gmpTrend": "up",
        "estListingPrice": 310,
        "estGainPercent": 26.53,
        "listingPrice": 310.0,
        "currentPrice": 314.2,
        "leadManager": "SEBI Registered Merchant Banker",
        "registrar": "Bigshare Services",
        "registrarUrl": REGISTRAR_URLS["Bigshare Services"],
        "subscription": {"qib": 1.2, "nii": 3.4, "retail": 4.8, "total": 3.2},
    },
    {
        "id": "shree-siddhivinayak-greentech-sme",
        "companyName": "Shree Siddhivinayak Greentech Industries Ltd",
        "symbol": "SSGIL",
        "category": "SME",
        "subCategory": "NSE SME",
        "status": "Upcoming",
        "statusNote": "Opens in 4 days",
        "openDate": "25 Nov 2026",
        "closeDate": "27 Nov 2026",
        "allotmentDate": "30 Nov 2026",
        "listingDate": "02 Dec 2026",
        "minPrice": 130,
        "maxPrice": 142,
        "lotSize": 1000,
        "issueSizeCr": 35.0,
        "gmp": 0,
        "gmpTrend": "neutral",
        "estListingPrice": 142,
        "estGainPercent": 0.0,
        "listingPrice": 142.0,
        "currentPrice": 142.0,
        "leadManager": "SEBI Registered Merchant Banker",
        "registrar": "Link Intime India",
        "registrarUrl": REGISTRAR_URLS["Link Intime India"],
        "subscription": {"qib": 0.0, "nii": 0.0, "retail": 0.0, "total": 0.0},
    },
    {
        "id": "foodlink-fb-holdings-mainboard",
        "companyName": "Foodlink F&B Holdings India Ltd",
        "symbol": "FFBH",
        "category": "Mainboard",
        "subCategory": "Mainboard",
        "status": "Upcoming",
        "statusNote": "Opens in 5 days",
        "openDate": "26 Nov 2026",
        "closeDate": "30 Nov 2026",
        "allotmentDate": "01 Dec 2026",
        "listingDate": "03 Dec 2026",
        "minPrice": 180,
        "maxPrice": 191,
        "lotSize": 78,
        "issueSizeCr": 650.0,
        "gmp": 12,
        "gmpTrend": "up",
        "estListingPrice": 203,
        "estGainPercent": 6.28,
        "listingPrice": 203.0,
        "currentPrice": 205.1,
        "leadManager": "SEBI Registered Merchant Banker",
        "registrar": "KFin Technologies",
        "registrarUrl": REGISTRAR_URLS["KFin Technologies"],
        "subscription": {"qib": 0.0, "nii": 0.0, "retail": 0.0, "total": 0.0},
    },
]

YEARLY_CLOSED_ARCHIVE = [
    ("Bombay Coated & Special Steels Ltd", "Mainboard", "29 Oct 2026", "02 Nov 2026", 82, 182, 183.05, 9, 18.5, "Link Intime India", "Listed"),
    ("Vedant Poly Fabs SME", "SME", "02 Nov 2026", "04 Nov 2026", 94, 1200, 56.68, 5, 12.0, "KFin Technologies", "Listed"),
    ("EAAA India Alternatives Ltd", "Mainboard", "26 Oct 2026", "28 Oct 2026", 510, 29, 1450.0, 48, 34.5, "Link Intime India", "Listed"),
    ("Jio Platforms Ltd", "Mainboard", "21 Oct 2026", "23 Oct 2026", 950, 15, 12500.0, 145, 64.2, "KFin Technologies", "Listed"),
    ("Paras Healthcare Ltd", "Mainboard", "21 Oct 2026", "23 Oct 2026", 285, 52, 850.0, 32, 29.8, "Link Intime India", "Listed"),
    ("Hero FinCorp Ltd", "Mainboard", "14 Oct 2026", "16 Oct 2026", 1420, 10, 3668.0, 110, 41.2, "Link Intime India", "Listed"),
    ("NSDL National Securities Depository", "Mainboard", "06 Oct 2026", "08 Oct 2026", 800, 18, 3000.0, 165, 92.4, "Link Intime India", "Listed"),
    ("HDB Financial Services Ltd", "Mainboard", "22 Sep 2026", "24 Sep 2026", 740, 20, 12500.0, 95, 53.1, "KFin Technologies", "Listed"),
    ("LG Electronics India Ltd", "Mainboard", "09 Sep 2026", "11 Sep 2026", 1140, 13, 15000.0, 210, 76.5, "KFin Technologies", "Listed"),
    ("Tata Capital Financial Services", "Mainboard", "18 Aug 2026", "20 Aug 2026", 620, 24, 9500.0, 125, 88.0, "Link Intime India", "Listed"),
    ("Ather Energy Ltd", "Mainboard", "28 Jul 2026", "30 Jul 2026", 321, 46, 2980.0, 42, 26.4, "Link Intime India", "Listed"),
    ("Zepto KiranaKart Technologies", "Mainboard", "10 Jul 2026", "14 Jul 2026", 460, 32, 8200.0, 85, 61.3, "KFin Technologies", "Listed"),
    ("Waaree Energies Ltd", "Mainboard", "21 Oct 2025", "23 Oct 2025", 1503, 9, 4321.4, 1350, 76.3, "Link Intime India", "Listed"),
    ("Hyundai Motor India Ltd", "Mainboard", "15 Oct 2025", "17 Oct 2025", 1960, 7, 27870.1, 45, 2.3, "KFin Technologies", "Listed"),
    ("Bajaj Housing Finance Ltd", "Mainboard", "09 Sep 2025", "11 Sep 2025", 70, 214, 6560.0, 80, 63.6, "KFin Technologies", "Listed"),
    ("Kabra Jewels SME", "SME", "15 Oct 2026", "17 Oct 2026", 128, 1000, 40.0, 65, 145.2, "Bigshare Services", "Listed"),
    ("Rikhav Securities SME", "SME", "08 Oct 2026", "10 Oct 2026", 86, 1600, 88.8, 75, 290.4, "Link Intime India", "Listed"),
]


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_td = False
        self.rows = []
        self.current_row = []
        self.current_cell = []

    def handle_starttag(self, tag, attrs):
        if tag in ("td", "th"):
            self.in_td = True
            self.current_cell = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.in_td:
            self.in_td = False
            text = " ".join("".join(self.current_cell).split()).strip()
            self.current_row.append(text)
        elif tag == "tr" and self.current_row:
            self.rows.append(self.current_row)
            self.current_row = []

    def handle_data(self, data):
        if self.in_td:
            self.current_cell.append(data)


def extract_num(text, default=0.0):
    if text is None:
        return default
    m = re.search(r"[-+]?\d+(?:\.\d+)?", str(text).replace(",", ""))
    return float(m.group(0)) if m else default


def detect_registrar(name):
    registrars = [
        "Link Intime India",
        "KFin Technologies",
        "Bigshare Services",
        "Purva Sharegistry",
        "Skyline Financial",
        "Maashitla Securities",
    ]
    reg = registrars[sum(ord(c) for c in name) % len(registrars)]
    return reg, REGISTRAR_URLS[reg]


def make_symbol(name):
    letters = "".join(w[0] for w in name.split() if w and w[0].isalnum())[:4].upper()
    return letters or "IPO"


def _extract_dates(row_text, default_year="2026"):
    match = re.search(
        r"(\d{1,2}\s+[A-Za-z]{3}(?:\s+\d{4})?)\s*(?:-|–|to)\s*(\d{1,2}\s+[A-Za-z]{3}(?:\s+\d{4})?)",
        row_text,
    )
    if not match:
        return "TBA", "TBA"

    open_d, close_d = match.group(1).strip(), match.group(2).strip()
    if not re.search(r"\d{4}", close_d):
        close_d = f"{close_d} {default_year}"
    if not re.search(r"\d{4}", open_d):
        yr = re.search(r"\d{4}", close_d).group(0)
        open_d = f"{open_d} {yr}"

    open_d = re.sub(r"^(\d)\s+", r"0\1 ", open_d)
    close_d = re.sub(r"^(\d)\s+", r"0\1 ", close_d)
    return open_d, close_d


def scrape_new_ipos(existing_names):
    """Fetches IPO rows from public tracker tables and merges non-duplicates."""
    new_items = []
    sources = [
        ("https://ipowatch.in/ipo-grey-market-premium-latest-ipo-gmp/", "Mainboard"),
        ("https://ipowatch.in/upcoming-ipo-calendar-ipo-list/", "Mainboard"),
        ("https://ipowatch.in/ipo-sme-grey-market-premium-latest-sme-ipo-gmp/", "SME"),
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-IN,en;q=0.9",
    }

    normalized_existing = {
        re.sub(r"[^a-z0-9]", "", name.lower()) for name in existing_names if name
    }

    for url, default_cat in sources:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                html_content = resp.read().decode("utf-8", errors="ignore")

            parser = TableParser()
            parser.feed(html_content)
            added_from_url = 0

            for cols in parser.rows:
                if len(cols) < 3:
                    continue
                raw_name = re.sub(r"\s+(Open|Closed|Upcoming|Listed)$", "", cols[0], flags=re.I).strip()
                if len(raw_name) < 4 or any(
                    w in raw_name.lower() for w in ("company", "ipo name", "stock", "total", "gmp today")
                ):
                    continue

                norm_key = re.sub(r"[^a-z0-9]", "", raw_name.lower())
                if not norm_key or any(norm_key[:12] in ex for ex in normalized_existing if len(ex) >= 8):
                    continue

                row_text = " | ".join(cols)
                open_date, close_date = _extract_dates(row_text, default_year="2026")

                band_match = re.search(
                    r"(?:₹|rs\.?)?\s*(\d{2,5}(?:\.\d+)?)\s*(?:-|–|to)\s*(?:₹|rs\.?)?\s*(\d{2,5}(?:\.\d+)?)",
                    row_text,
                    flags=re.I,
                )
                if band_match:
                    min_price = int(float(band_match.group(1)))
                    max_price = int(float(band_match.group(2)))
                else:
                    nums = [extract_num(c, None) for c in cols[1:]]
                    price_candidates = [int(n) for n in nums if n is not None and 20 <= n <= 10000]
                    if not price_candidates:
                        continue
                    max_price = price_candidates[0]
                    min_price = max(max_price - 5, 1)

                gmp_match = re.search(
                    r"([+-]?\s*(?:₹|rs\.)?\s*\d+(?:\.\d+)?)\s*(?:\(|$|\s*\||\s*↑|\s*↓|\s*→)",
                    row_text,
                    flags=re.I,
                )
                gmp = int(round(extract_num(gmp_match.group(1), 0.0))) if gmp_match else 0
                if abs(gmp) > max_price * 5:
                    gmp = 0

                is_sme = bool(re.search(r"\b(sme|emerge|bsesme|nsesme)\b", f"{raw_name} {row_text}", flags=re.I))
                cat = "SME" if is_sme else default_cat
                reg, reg_url = detect_registrar(raw_name)
                est_list = max_price + gmp
                gain = round((gmp / max_price) * 100, 2) if max_price > 0 else 0.0
                lot_size = max(int(15000 // max_price), 1) if cat == "Mainboard" else max(int(120000 // max_price), 100)
                slug = re.sub(r"[^a-z0-9]+", "-", raw_name.lower()).strip("-")

                new_items.append({
                    "id": f"live-{len(new_items)+1}-{slug}",
                    "companyName": raw_name,
                    "symbol": make_symbol(raw_name),
                    "category": cat,
                    "subCategory": "NSE SME" if cat == "SME" else "Mainboard",
                    "status": "Upcoming",
                    "statusNote": "Check dates",
                    "openDate": open_date,
                    "closeDate": close_date,
                    "allotmentDate": "TBA",
                    "listingDate": "TBA",
                    "minPrice": min_price,
                    "maxPrice": max_price,
                    "lotSize": lot_size,
                    "issueSizeCr": 100.0,
                    "gmp": gmp,
                    "gmpTrend": "up" if gmp > 0 else ("down" if gmp < 0 else "neutral"),
                    "estListingPrice": est_list,
                    "estGainPercent": gain,
                    "listingPrice": float(est_list),
                    "currentPrice": float(round(est_list * 1.01, 2)),
                    "leadManager": "SEBI Registered Merchant Banker",
                    "registrar": reg,
                    "registrarUrl": reg_url,
                    "subscription": {"qib": 0.0, "nii": 0.0, "retail": 0.0, "total": 0.0},
                })
                normalized_existing.add(norm_key)
                added_from_url += 1

            print(f"Fetched {added_from_url} new IPOs from {url} (total rows scanned: {len(parser.rows)})")
        except Exception as e:
            print(f"Live merge error for {url}: {e}")

    return new_items


def build_archive_items():
    items = []
    for idx, row in enumerate(YEARLY_CLOSED_ARCHIVE):
        name, cat, o_date, c_date, price, lot, size_cr, gmp, sub_tot, reg, status_note = row
        est_list = price + gmp
        gain = round((gmp / price) * 100, 2) if price > 0 else 0.0
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        items.append({
            "id": f"archive-{idx+1}-{slug}",
            "companyName": name,
            "symbol": make_symbol(name),
            "category": cat,
            "subCategory": "NSE SME" if cat == "SME" else "Mainboard",
            "status": "Closed",
            "statusNote": status_note,
            "openDate": o_date,
            "closeDate": c_date,
            "allotmentDate": c_date,
            "listingDate": c_date,
            "minPrice": max(price - 5, 1),
            "maxPrice": price,
            "lotSize": lot,
            "issueSizeCr": size_cr,
            "gmp": gmp,
            "gmpTrend": "up" if gmp > 0 else "neutral",
            "estListingPrice": est_list,
            "estGainPercent": gain,
            "listingPrice": float(est_list),
            "currentPrice": float(round(est_list * 1.02, 2)),
            "leadManager": "SEBI Registered Merchant Banker",
            "registrar": reg,
            "registrarUrl": REGISTRAR_URLS.get(reg, REGISTRAR_URLS["Link Intime India"]),
            "subscription": {
                "qib": round(sub_tot * 1.1, 2),
                "nii": round(sub_tot * 1.4, 2),
                "retail": round(sub_tot * 0.85, 2),
                "total": sub_tot,
            },
        })
    return items


def auto_compute_status(item, now_ist):
    """Automatically updates status and statusNote based on 5:00 PM IST market cutoff."""
    try:
        o_dt = datetime.strptime(item["openDate"], "%d %b %Y").replace(tzinfo=IST)
        c_dt = datetime.strptime(item["closeDate"], "%d %b %Y").replace(hour=17, minute=0, tzinfo=IST)
        a_dt = (
            datetime.strptime(item["allotmentDate"], "%d %b %Y").replace(tzinfo=IST)
            if item.get("allotmentDate") not in (None, "TBA", "Allotment Out", "Listed")
            else c_dt + timedelta(days=1)
        )
        l_dt = (
            datetime.strptime(item["listingDate"], "%d %b %Y").replace(tzinfo=IST)
            if item.get("listingDate") not in (None, "TBA", "Allotment Out", "Listed")
            else c_dt + timedelta(days=3)
        )

        today_date = now_ist.date()
        open_date = o_dt.date()
        close_date = c_dt.date()

        if now_ist < o_dt:
            item["status"] = "Upcoming"
            days_to_open = (open_date - today_date).days
            item["statusNote"] = "Opens tomorrow" if days_to_open == 1 else f"Opens in {days_to_open} days"
        elif o_dt <= now_ist < c_dt:
            item["status"] = "Open"
            days_left = (close_date - today_date).days
            if days_left == 0:
                item["statusNote"] = "Closes today (5 PM)"
            elif days_left == 1:
                item["statusNote"] = "Closes tomorrow"
            else:
                item["statusNote"] = f"Closes in {days_left} days"
        else:
            item["status"] = "Closed"
            if today_date < a_dt.date():
                item["statusNote"] = "Awaiting allotment"
            elif today_date < l_dt.date():
                item["statusNote"] = "Allotment Out"
            else:
                item["statusNote"] = "Listed"
    except Exception:
        pass
    return item


def main():
    now_ist = datetime.now(IST)
    now_str = now_ist.strftime("%d %b %Y, %I:%M %p IST")

    existing_names = {item["companyName"] for item in BASE_IPOS}
    archive_items = build_archive_items()
    for item in archive_items:
        existing_names.add(item["companyName"])

    scraped_new = scrape_new_ipos(existing_names)
    all_ipos = scraped_new + list(BASE_IPOS) + archive_items

    for item in all_ipos:
        auto_compute_status(item, now_ist)
        item["updatedAt"] = now_str

    payload = {
        "lastUpdated": now_str,
        "totalCount": len(all_ipos),
        "ipos": all_ipos,
    }
    with open("ipos.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"Successfully generated ipos.json with {len(all_ipos)} IPOs ({len(scraped_new)} newly scraped)")


if __name__ == "__main__":
    main()
