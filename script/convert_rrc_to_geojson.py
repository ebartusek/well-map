import pandas as pd
import json
import requests

# Download the latest RRC Drilling Permits file
url = "https://www.rrc.texas.gov/media/vcydow4v/drillingpermitscurrentyear.zip"
csv_filename = "drillingpermits.csv"

r = requests.get(url)
with open("permits.zip", "wb") as f:
    f.write(r.content)

import zipfile
with zipfile.ZipFile("permits.zip", "r") as zip_ref:
    zip_ref.extractall(".")

df = pd.read_csv(csv_filename)

df = df.dropna(subset=["Latitude", "Longitude"])
df = df[df["Latitude"].between(25, 37) & df["Longitude"].between(-107, -93)]

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

with open("wells.geojson", "w") as f:
    json.dump(geojson, f, indent=2)
