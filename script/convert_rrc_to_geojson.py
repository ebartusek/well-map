import pandas as pd
import json
import requests
import zipfile
import os

# Download RRC Drilling Permits ZIP
url = "https://www.rrc.texas.gov/media/vcydow4v/drillingpermitscurrentyear.zip"
zip_path = "permits.zip"
csv_name = "drillingpermitscurrentyear.csv"

print("Downloading ZIP...")
r = requests.get(url)
if r.status_code != 200:
    raise Exception(f"Failed to download file. Status code: {r.status_code}")

with open(zip_path, "wb") as f:
    f.write(r.content)

print("Extracting ZIP...")
with zipfile.ZipFile(zip_path, "r") as zip_ref:
    zip_ref.extractall(".")

if not os.path.exists(csv_name):
    raise FileNotFoundError(f"Expected file {csv_name} not found after unzip.")

print("Loading data...")
df = pd.read_csv(csv_name)

df = df.dropna(subset=["Latitude", "Longitude"])
df = df[df["Latitude"].between(25, 37) & df["Longitude"].between(-107, -93)]

print(f"Found {len(df)} valid wells with coordinates.")

features = []
for _, row in df.iterrows():
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [row["Longitude"], row["Latitude"]],
        },
        "properties": {
            "api": row.get("API Number", ""),
            "operator": row.get("Operator Name", ""),
            "well_name": row.get("Lease Name", ""),
        }
    })

geojson = {
    "type": "FeatureCollection",
    "features": features
}

print("Writing wells.geojson...")
with open("wells.geojson", "w") as f:
    json.dump(geojson, f, indent=2)

print("Done.")
