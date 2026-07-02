"""
fetch_settlements.py
Fetches real settlement coordinates (city/town/village/hamlet) from OSM Overpass API
for Southern Punjab districts, with population tags where available.
Output: data/settlements.json
"""

import json
import time
import requests
from pathlib import Path

# ── District bounding boxes [south, west, north, east] ──────────────────────
# Covering all 11 districts of Southern Punjab (3 divisions)
DISTRICTS = {
    # Multan Division
    "multan":       {"name":"Multan",          "bbox": [29.80, 71.25, 30.75, 72.05], "division": "Multan"},
    "khanewal":     {"name":"Khanewal",        "bbox": [29.80, 71.55, 30.55, 72.35], "division": "Multan"},
    "lodhran":      {"name":"Lodhran",         "bbox": [29.25, 71.35, 29.90, 72.10], "division": "Multan"},
    "vehari":       {"name":"Vehari",          "bbox": [29.25, 71.65, 30.30, 72.65], "division": "Multan"},

    # Bahawalpur Division
    "bahawalpur":   {"name":"Bahawalpur",      "bbox": [28.65, 70.60, 29.75, 72.50], "division": "Bahawalpur"},
    "bahawalnagar": {"name":"Bahawalnagar",    "bbox": [29.50, 72.60, 30.60, 74.00], "division": "Bahawalpur"},
    "ry_khan":      {"name":"Rahim Yar Khan",  "bbox": [27.40, 69.90, 29.00, 71.50], "division": "Bahawalpur"},

    # DG Khan Division
    "dg_khan":      {"name":"Dera Ghazi Khan", "bbox": [29.60, 70.10, 31.10, 71.30], "division": "DG Khan"},
    "muzaffargarh": {"name":"Muzaffargarh",    "bbox": [29.55, 70.80, 30.60, 71.70], "division": "DG Khan"},
    "layyah":       {"name":"Layyah",          "bbox": [30.40, 70.60, 31.30, 71.50], "division": "DG Khan"},
    "rajanpur":     {"name":"Rajanpur",        "bbox": [28.90, 69.70, 30.10, 70.90], "division": "DG Khan"},
}

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

PLACE_TYPES = ["city", "town", "village", "hamlet", "suburb", "neighbourhood"]


def build_query(bbox: list, place_types: list) -> str:
    s, w, n, e = bbox
    union_parts = "\n".join(
        f'  node["place"="{pt}"]({s},{w},{n},{e});'
        for pt in place_types
    )
    return f"""[out:json][timeout:60];
(
{union_parts}
);
out body;"""


def fetch_overpass(query: str, retries: int = 3) -> dict:
    for attempt in range(1, retries + 1):
        try:
            r = requests.post(
                OVERPASS_URL,
                data={'data': query},
                headers={'User-Agent': 'BlackSky-Settlements/1.0'},
                timeout=90,
            )
            if r.status_code == 429:
                wait = 30 * attempt
                print(f"    Rate limited. Waiting {wait}s...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt == retries:
                raise
            print(f"    Error ({e}), retry {attempt}/{retries}...")
            time.sleep(10)
    return {"elements": []}


def parse_settlement(element: dict, district: str, division: str) -> dict | None:
    tags = element.get("tags", {})
    lat = element.get("lat")
    lon = element.get("lon")
    if lat is None or lon is None:
        return None

    name = tags.get("name:en") or tags.get("name") or "Unknown"
    place_type = tags.get("place", "unknown")

    # Population: use OSM tag if present, else estimate by place type
    pop_tag = tags.get("population", "")
    try:
        population = int(pop_tag.replace(",", "").strip())
        pop_is_estimated = False
    except (ValueError, AttributeError):
        estimates = {
            "city": 200000, "town": 30000, "village": 5000,
            "hamlet": 500, "suburb": 15000, "neighbourhood": 3000
        }
        population = estimates.get(place_type, 1000)
        pop_is_estimated = True

    return {
        "name":                 name,
        "district_id":          district,   # matches real_scores.json IDs
        "division":             division,
        "lat":                  lat,
        "lon":                  lon,
        "place_type":           place_type,
        "population":           population,
        "osm_id":               element.get("id"),
        "population_is_estimated": pop_is_estimated,
    }


def main():
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "settlements.json"

    all_settlements = []
    total_districts = len(DISTRICTS)

    print(f"Fetching settlements for {total_districts} districts in Southern Punjab...\n")

    for i, (district_id, meta) in enumerate(DISTRICTS.items(), 1):
        print(f"[{i}/{total_districts}] {meta['name']} ({meta['division']})...")

        query = build_query(meta["bbox"], PLACE_TYPES)

        try:
            result = fetch_overpass(query)
        except Exception as e:
            print(f"    FAILED: {e}")
            continue

        elements = result.get("elements", [])
        parsed = []
        for el in elements:
            s = parse_settlement(el, district_id, meta["division"])
            if s:
                s["district_name"] = meta["name"]
                parsed.append(s)

        # Deduplicate by osm_id (some settlements sit on division borders)
        seen_ids = set()
        unique = []
        for s in parsed:
            if s["osm_id"] not in seen_ids:
                seen_ids.add(s["osm_id"])
                unique.append(s)

        all_settlements.extend(unique)
        real_pop = sum(1 for s in unique if not s["population_is_estimated"])
        print(f"    Found {len(unique)} settlements  ({real_pop} with real OSM population tags)")

        # Be polite to Overpass API
        if i < total_districts:
            time.sleep(4)

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"\n{'='*50}")
    print(f"Total settlements fetched: {len(all_settlements)}")
    by_type: dict[str, int] = {}
    for s in all_settlements:
        by_type[s["place_type"]] = by_type.get(s["place_type"], 0) + 1
    for pt, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {pt:20s}: {count}")

    real_pop_total = sum(1 for s in all_settlements if not s["population_is_estimated"])
    print(f"\nSettlements with real OSM population tags: {real_pop_total}/{len(all_settlements)}")
    print(f"\nSaving to {output_path}...")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {
                "region": "Southern Punjab, Pakistan",
                "districts": list(DISTRICTS.keys()),
                "total_settlements": len(all_settlements),
                "place_types_queried": PLACE_TYPES,
                "source": "OpenStreetMap via Overpass API",
                "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
            "settlements": all_settlements,
        }, f, indent=2, ensure_ascii=False)

    print(f"Done. {output_path} written ({output_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
