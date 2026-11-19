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
        "Connection": "keep-alive",
    }

    for url, default_cat in sources:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8", errors="ignore")

            parser = TableParser()
            parser.feed(html)
            added_from_url = 0

            for cols in parser.rows:
                if len(cols) < 3:
                    continue
                raw_name = re.sub(r"\s+(Open|Closed|Upcoming|Listed)$", "", cols[0], flags=re.I).strip()
                if len(raw_name) < 4 or any(w in raw_name.lower() for w in ("company", "ipo name", "stock", "total")):
                    continue

                key = re.sub(r"[^a-z0-9]", "", raw_name.lower())[:12]
                if not key or any(key in re.sub(r"[^a-z0-9]", "", ex.lower()) for ex in existing_names):
                    continue

                # Find plausible issue price (typically 25 to 25000) and GMP from numeric cells
                nums = [extract_num(c, None) for c in cols[1:]]
                nums = [n for n in nums if n is not None]
                if not nums:
                    continue

                price_candidates = [int(n) for n in nums if 20 <= n <= 25000]
                if not price_candidates:
                    continue

                price = price_candidates[-1] if len(price_candidates) > 1 else price_candidates[0]
                gmp_candidates = [int(n) for n in nums if n != price and -2000 <= n <= 5000]
                gmp = gmp_candidates[0] if gmp_candidates else 0

                cat = "SME" if "sme" in raw_name.lower() else default_cat
                reg, reg_url = detect_registrar(raw_name)
                est_list = price + gmp
                gain = round((gmp / price) * 100, 2) if price > 0 else 0.0
                lot_size = max(int(15000 // price), 1) if cat == "Mainboard" else max(int(120000 // price), 100)
                slug = re.sub(r"[^a-z0-9]+", "-", raw_name.lower()).strip("-")

                new_items.append({
                    "id": f"live-{len(new_items)+1}-{slug}",
                    "companyName": raw_name,
                    "symbol": "".join([w[0] for w in raw_name.split()[:3] if w and w[0].isalnum()]).upper() or "IPO",
                    "category": cat,
                    "subCategory": "NSE SME" if cat == "SME" else "Mainboard",
                    "status": "Upcoming",
                    "statusNote": "Check dates",
                    "openDate": "TBA",
                    "closeDate": "TBA",
                    "allotmentDate": "TBA",
                    "listingDate": "TBA",
                    "minPrice": max(price - 5, 1),
                    "maxPrice": price,
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
                    "subscription": {"qib": 0.0, "nii": 0.0, "retail": 0.0, "total": 0.0}
                })
                existing_names.add(raw_name)
                added_from_url += 1

            print(f"Fetched {added_from_url} new IPOs from {url} (total rows scanned: {len(parser.rows)})")
        except Exception as e:
            print(f"Live merge error for {url}: {e}")

    return new_items
