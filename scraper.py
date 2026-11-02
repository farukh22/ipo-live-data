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
