"""
Downloads real OSM administrative boundaries for all 11 Southern Punjab districts.
Saves individual .shp files + combined GeoJSON for the frontend map.
"""

import osmnx as ox
import geopandas as gpd
import json
import os
import time

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data", "shapefiles")
GEOJSON_OUT = os.path.join(os.path.dirname(__file__), "data", "southern_punjab.geojson")

os.makedirs(OUTPUT_DIR, exist_ok=True)

DISTRICTS = [
    {"id": "multan",          "query": "Multan District, Punjab, Pakistan"},
    {"id": "khanewal",        "query": "Khanewal District, Punjab, Pakistan"},
    {"id": "lodhran",         "query": "Lodhran District, Punjab, Pakistan"},
    {"id": "vehari",          "query": "Vehari District, Punjab, Pakistan"},
    {"id": "bahawalpur",      "query": "Bahawalpur District, Punjab, Pakistan"},
    {"id": "bahawalnagar",    "query": "Bahawalnagar District, Punjab, Pakistan"},
    {"id": "rahim_yar_khan",  "query": "Rahim Yar Khan District, Punjab, Pakistan"},
    {"id": "dg_khan",         "query": "Dera Ghazi Khan District, Punjab, Pakistan"},
    {"id": "muzaffargarh",    "query": "Muzaffargarh District, Punjab, Pakistan"},
    {"id": "layyah",          "query": "Layyah District, Punjab, Pakistan"},
    {"id": "rajanpur",        "query": "Rajanpur District, Punjab, Pakistan"},
]

all_features = []
failed = []

for d in DISTRICTS:
    print(f"\nFetching: {d['query']} ...")
    try:
        gdf = ox.geocode_to_gdf(d['query'])

        # Clean column types — shapefiles can't handle list/dict columns
        for col in gdf.columns:
            if gdf[col].apply(lambda x: isinstance(x, (list, dict))).any():
                gdf[col] = gdf[col].astype(str)

        # Ensure CRS is WGS84
        gdf = gdf.to_crs(epsg=4326)

        # Add district_id property
        gdf["district_id"] = d["id"]

        # Save individual shapefile
        shp_path = os.path.join(OUTPUT_DIR, f"{d['id']}.shp")
        gdf.to_file(shp_path)
        print(f"  [OK] Saved shapefile: {shp_path}")

        # Collect for combined GeoJSON
        geojson_str = gdf.to_json()
        geojson_obj = json.loads(geojson_str)
        for feat in geojson_obj["features"]:
            feat["properties"]["district_id"] = d["id"]
            all_features.append(feat)

        time.sleep(1.5)  # be polite to Nominatim

    except Exception as e:
        print(f"  [FAIL] {e}")
        failed.append(d["id"])

# Save combined GeoJSON
combined = {"type": "FeatureCollection", "features": all_features}
with open(GEOJSON_OUT, "w", encoding="utf-8") as f:
    json.dump(combined, f)

print(f"\n{'='*50}")
print(f"Done. {len(all_features)} district(s) downloaded.")
if failed:
    print(f"Failed: {failed}")
print(f"Combined GeoJSON saved to:\n  {GEOJSON_OUT}")
print(f"Individual shapefiles in:\n  {OUTPUT_DIR}")
