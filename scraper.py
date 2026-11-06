import json
import re
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

REGISTRAR_URLS = {
    "Link Intime India": "https://in.mpms.mufg.com/Initial_Offer/public-issues.html",
    "KFin Technologies": "https://kosmic.kfintech.com/ipostatus/",
    "Bigshare Services": "https://ipo.bigshareonline.com/IPO_Status.html",
    "Purva Sharegistry": "https://www.purvashare.com/investor-service/ipo-query",
    "Skyline Financial": "https://www.skylinerta.com/ipo.php",
    "Maashitla Securities": "https://maashitla.com/allotment-status/public-issues",
    "Mas Services": "https://www.masserv.com/opt.asp"
}

BASE_IPOS = [
    {
        "id": "bombay-coated-mainboard",
        "companyName": "Bombay Coated & Special Steels Ltd",
        "symbol": "BCSSL",
        "category": "Mainboard",
        "subCategory": "Mainboard",
        "status": "Open",
        "statusNote": "Closes today (5 PM)",
        "openDate": "29 Oct 2026",
        "closeDate": "02 Nov 2026",
        "allotmentDate": "03 Nov 2026",
        "listingDate": "05 Nov 2026",
        "minPrice": 78,
        "maxPrice": 82,
        "lotSize": 182,
        "issueSizeCr": 183.05,
        "gmp": 9,
        "gmpTrend": "up",
        "estListingPrice": 91,
        "estGainPercent": 10.98,
        "listingPrice": 91.0,
        "currentPrice": 93.5,
        "leadManager": "Smart Horizon Capital Advisors",
        "registrar": "Link Intime India",
        "registrarUrl": REGISTRAR_URLS["Link Intime India"],
        "subscription": {"qib": 12.4, "nii": 28.6, "retail": 19.2, "total": 18.5}
    },
    {
        "id": "vedant-poly-fabs-sme",
        "companyName": "Vedant Poly Fabs Ltd.",
        "symbol": "VPFL",
        "category": "SME",
        "subCategory": "NSE SME",
        "status": "Open",
        "statusNote": "Closes in 2 days",
        "openDate": "02 Nov 2026",
        "closeDate": "04 Nov 2026",
        "allotmentDate": "05 Nov 2026",
        "listingDate": "09 Nov 2026",
        "minPrice": 88,
        "maxPrice": 94,
        "lotSize": 1200,
        "issueSizeCr": 56.68,
        "gmp": 5,
        "gmpTrend": "up",
        "estListingPrice": 99,
        "estGainPercent": 5.32,
        "listingPrice": 99.0,
        "currentPrice": 101.2,
        "leadManager": "Affinity Global Capital Market",
        "registrar": "KFin Technologies",
        "registrarUrl": REGISTRAR_URLS["KFin Technologies"],
        "subscription": {"qib": 0.0, "nii": 0.0, "retail": 0.0, "total": 0.0}
    }
]

YEARLY_CLOSED_ARCHIVE = [
    ("EAAA India Alternatives Ltd", "Mainboard", "26 Oct 2026", "28 Oct 2026", 510, 29, 1450.0, 48, 34.5, "Link Intime India", "Listed"),
    ("Jio Platforms Ltd", "Mainboard", "21 Oct 2026", "23 Oct 2026", 950, 15, 12500.0, 145, 64.2, "KFin Technologies", "Listed"),
    ("Paras Healthcare Ltd", "Mainboard", "21 Oct 2026", "23 Oct 2026", 285, 52, 850.0, 32, 29.8, "Link Intime India", "Listed"),
    ("Hero FinCorp Ltd", "Mainboard", "14 Oct 2026", "16 Oct 2026", 1420, 10, 3668.0, 110, 41.2, "Link Intime India", "Listed"),
    ("NSDL (National Securities Depository)", "Mainboard", "06 Oct 2026", "08 Oct 2026", 800, 18, 3000.0, 165, 92.4, "Link Intime India", "Listed"),
    ("HDB Financial Services Ltd", "Mainboard", "22 Sep 2026", "24 Sep 2026", 740, 20, 12500.0, 95, 53.1, "KFin Technologies", "Listed"),
    ("LG Electronics India Ltd", "Mainboard", "09 Sep 2026", "11 Sep 2026", 1140, 13, 15000.0, 210, 76.5, "KFin Technologies", "Listed"),
    ("Tata Capital Financial Services", "Mainboard", "18 Aug 2026", "20 Aug 2026", 620, 24, 9500.0, 125, 88.0, "Link Intime India", "Listed"),
    ("Ather Energy Ltd", "Mainboard", "28 Jul 2026", "30 Jul 2026", 321, 46, 2980.0, 42, 26.4, "Link Intime India", "Listed"),
    ("Zepto (KiranaKart Technologies)", "Mainboard", "10 Jul 2026", "14 Jul 2026", 460, 32, 8200.0, 85, 61.3, "KFin Technologies", "Listed"),
    ("Waaree Energies Ltd", "Mainboard", "21 Oct 2025", "23 Oct 2025", 1503, 9, 4321.4, 1350, 76.3, "Link Intime India", "Listed"),
    ("Hyundai Motor India Ltd", "Mainboard", "15 Oct 2025", "17 Oct 2025", 1960, 7, 27870.1, 45, 2.3, "KFin Technologies", "Listed"),
    ("Bajaj Housing Finance Ltd", "Mainboard", "09 Sep 2025", "11 Sep 2025", 70, 214, 6560.0, 80, 63.6, "KFin Technologies", "Listed"),
    ("Kabra Jewels SME", "SME", "15 Oct 2026", "17 Oct 2026", 128, 1000, 40.0, 65, 145.2, "Bigshare Services", "Listed"),
    ("Rikhav Securities SME", "SME", "08 Oct 2026", "10 Oct 2026", 86, 1600, 88.8, 75, 290.4, "Link Intime India", "Listed")
]

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
            "symbol": "".join([w[0] for w in name.split()[:3]]).upper(),
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
                "total": sub_tot
            }
        })
    return items

def auto_compute_status(item, now_ist):
    """Automatically updates status and statusNote based on 5:00 PM IST market cutoff."""
    try:
        o_dt = datetime.strptime(item["openDate"], "%d %b %Y").replace(tzinfo=IST)
        c_dt = datetime.strptime(item["closeDate"], "%d %b %Y").replace(hour=17, minute=0, tzinfo=IST)
        a_dt = datetime.strptime(item["allotmentDate"], "%d %b %Y").replace(tzinfo=IST) if item.get("allotmentDate") not in (None, "TBA", "Allotment Out", "Listed") else c_dt + timedelta(days=1)
        l_dt = datetime.strptime(item["listingDate"], "%d %b %Y").replace(tzinfo=IST) if item.get("listingDate") not in (None, "TBA", "Allotment Out", "Listed") else c_dt + timedelta(days=3)

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

    all_ipos = list(BASE_IPOS) + build_archive_items()
    for item in all_ipos:
        auto_compute_status(item, now_ist)
        item["updatedAt"] = now_str

    payload = {
        "lastUpdated": now_str,
        "totalCount": len(all_ipos),
        "ipos": all_ipos
    }
    with open("ipos.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"Successfully generated ipos.json with {len(all_ipos)} IPOs")

if __name__ == "__main__":
    main()
