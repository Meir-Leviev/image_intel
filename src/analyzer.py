from math import radians, cos, sin, asin, sqrt
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.distance import geodesic


def date_range(img_data: list[dict]) -> dict:
    start = min(img_data, key=lambda d: d["datetime"])
    start_date = start["datetime"].split()

    end = max(img_data, key=lambda d: d["datetime"])
    end_date = end["datetime"].split()

    return {"start": start_date[0], "end": end_date[0]}


def total_images(img_data: list[dict]) -> int:
    return len(img_data)


def img_with_gps(img_data: list[dict]) -> int:
    return sum(1 for img in img_data if img["has_gps"])


def img_with_datetime(img_data: list[dict]) -> int:
    return sum(1 for img in img_data if img["datetime"])


def unique_cameras(img_data: list[dict]) -> set:
    return set(f"{img['camera_make']} {img['camera_model']}" for img in img_data)


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)

    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * R * asin(sqrt(a))


def detect_camera_switches(sorted_images):
    switches = []

    for i in range(1, len(sorted_images)):
        prev_cam = sorted_images[i - 1].get("camera_model")
        curr_cam = sorted_images[i].get("camera_model")

        if prev_cam and curr_cam and prev_cam != curr_cam:
            switches.append({
                "date": sorted_images[i]["datetime"],
                "from": prev_cam,
                "to": curr_cam
            })

    return switches


def camera_switches_as_str(switches: list[dict]) -> str:
    switches_str = ''

    for s in switches:
        switches_str += f"On {s['date']} the agent switched from {s['from']} to {s['to']}\n"

    return switches_str


def get_city_from_coords(lat, lon):
    geolocator = Nominatim(user_agent="image_analyzer")
    location = geolocator.reverse(f"{lat}, {lon}", language="en")

    if location:
        address = location.raw.get("address", {})
        return address.get("city") or address.get("town") or address.get("village")

    return "Unknown Area"


def check_if_close(coord1, coord2, max_distance_km):
    distance = geodesic(coord1, coord2).km
    return distance <= max_distance_km


def find_geo_clusters(images_data, max_distance=1):
    geo_data = [x for x in images_data if x.get("latitude") is not None and x.get("longitude") is not None]

    sorted_data = sorted(geo_data, key=lambda x: (x["latitude"], x["longitude"]))

    out_dict = {}

    for i in range(1, len(sorted_data)):
        curr_img = sorted_data[i]
        prev_img = sorted_data[i - 1]

        coord1 = (prev_img["latitude"], prev_img["longitude"])
        coord2 = (curr_img["latitude"], curr_img["longitude"])

        if check_if_close(coord1, coord2, max_distance):
            city = get_city_from_coords(coord1[0], coord1[1])
            out_dict[city] = out_dict.get(city, 1) + 1

    return out_dict


def detect_location_returns(sorted_images, threshold_km=1.0, min_gap_hours=2):
    returns = []
    fmt = "%Y-%m-%d %H:%M:%S"

    geo_images = [img for img in sorted_images if "latitude" in img and "longitude" in img]

    for i in range(len(geo_images)):
        curr_img = geo_images[i]
        curr_time = datetime.strptime(curr_img["datetime"], fmt)

        for j in range(i):
            prev_img = geo_images[j]
            prev_time = datetime.strptime(prev_img["datetime"], fmt)

            time_diff = (curr_time - prev_time).total_seconds() / 3600

            if time_diff >= min_gap_hours:
                dist = calculate_distance(
                    curr_img["latitude"], curr_img["longitude"],
                    prev_img["latitude"], prev_img["longitude"]
                )

                if dist <= threshold_km:
                    returns.append({
                        "filename": curr_img.get("filename"),
                        "date": curr_img["datetime"],
                        "original_date": prev_img["datetime"],
                        "dist_m": int(dist * 1000)
                    })

                    break

    return returns


def analyze_agent_activity(images_data):
    sorted_images = sorted(
        [img for img in images_data if img.get("datetime")],
        key=lambda x: x["datetime"]
    )

    if not sorted_images:
        return {"error": "No valid data"}

    images = total_images(sorted_images)
    gps = img_with_gps(sorted_images)
    datetime_imgs = img_with_datetime(sorted_images)
    cameras = list(unique_cameras(sorted_images))
    date_rang = date_range(sorted_images)

    switches = detect_camera_switches(sorted_images)
    switches_insights = camera_switches_as_str(switches)

    clusters = find_geo_clusters(images_data)
    returns = detect_location_returns(sorted_images)

    insights = [
        f"Found {len(cameras)} different devices - the agent may have switched devices",
        switches_insights
    ]

    for k, v in clusters.items():
        insights.append(f"A cluster of {v} photos in the {k} area")

    return {
        "total_images": images,
        "images_with_gps": gps,
        "images_with_datetime": datetime_imgs,
        "unique_cameras": cameras,
        "date_range": date_rang,
        "insights": insights
    }