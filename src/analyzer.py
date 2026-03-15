from math import radians, cos, sin, asin, sqrt
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
"""
example output:
{
    "total_images": 12,
    "images_with_gps": 10,
    "images_with_datetime": 11,
    "unique_cameras": ["Samsung Galaxy S23", "Apple iPhone 15 Pro", "Canon EOS R5"],
    "date_range": {"start": "2025-01-12", "end": "2025-01-16"},
    "insights": [
        "נמצאו 3 מכשירים שונים - ייתכן שהסוכן החליף מכשירים",
        "ב-13/01 הסוכן עבר ממכשיר Samsung ל-iPhone",
        "ריכוז של 3 תמונות באזור תל אביב",
        "המצלמה המקצועית (Canon) הופיעה רק פעם אחת - בנמל חיפה"
    ]
}
"""
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
    return set(f"{img["camera_make"]} {img["camera_model"]}" for img in img_data)


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
        switches_str += f"On {s["date"]} the agent switched from {s["from"]} to {s["to"]}\n"
    return switches_str


def get_city_from_coords(lat, lon):
    # Initialize Nominatim API
    geolocator = Nominatim(user_agent="my_app")

    # Get location details
    location = geolocator.reverse(f"{lat}, {lon}", language="en")

    if location:
        address = location.raw.get("address", {})
        return address.get("city") or address.get("town") or address.get("village")

    return "Unknown Area"


def check_if_close(coord1, coord2, max_distance_km):
    # Calculate distance between two coordinates in kilometers
    distance = geodesic(coord1, coord2).km
    return distance <= max_distance_km


def find_geo_clusters(images_data, max_distance=1):
    sorted_data = sorted(images_data, key=lambda x: (x["latitude"], x["longitude"]))
    out_dict = {}
    for i in range(1, len(sorted_data)):
        curr_img = sorted_data[i]
        prev_img = sorted_data[i - 1]

        coord1 = (prev_img["latitude"], prev_img["longitude"])
        coord2 = (curr_img["latitude"], curr_img["longitude"])

        if check_if_close(coord1, coord2, max_distance):
            # If they are close, get the city and increment
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
                dist = calculate_distance(curr_img["latitude"], curr_img["longitude"],
                                          prev_img["latitude"], prev_img["longitude"])
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
    print("--- Analyzing Images Data ---")
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

    insights = [f"Found {len(cameras)} different devices - the agent may have switched devices", f"{switches_insights}"]

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


def test_system():
    mock_data = [
        {'camera_make': 'Samsung',
         'camera_model': 'Galaxy S23',
         'datetime': '2025-01-12 08:30:00',
         'filename': 'IMG_001.jpg',
         'has_gps': True,
         'latitude': 32.0853,
         'longitude': 34.7818},
        {'camera_make': 'Samsung',
         'camera_model': 'Galaxy S23',
         'datetime': '2025-01-12 11:15:00',
         'filename': 'IMG_002.jpg',
         'has_gps': True,
         'latitude': 32.0804,
         'longitude': 34.7805},
        {'camera_make': 'Samsung',
         'camera_model': 'Galaxy S23',
         'datetime': '2025-01-12 14:00:00',
         'filename': 'IMG_003.jpg',
         'has_gps': True,
         'latitude': 32.0667,
         'longitude': 34.7667},
        {'camera_make': 'Apple',
         'camera_model': 'iPhone 15 Pro',
         'datetime': '2025-01-13 09:00:00',
         'filename': 'IMG_004.jpg',
         'has_gps': True,
         'latitude': 31.7683,
         'longitude': 35.2137},
        {'camera_make': 'Apple',
         'camera_model': 'iPhone 15 Pro',
         'datetime': '2025-01-13 12:30:00',
         'filename': 'IMG_005.jpg',
         'has_gps': True,
         'latitude': 31.778,
         'longitude': 35.2354},
        {'camera_make': 'Apple',
         'camera_model': 'iPhone 15 Pro',
         'datetime': '2025-01-13 16:45:00',
         'filename': 'IMG_006.jpg',
         'has_gps': True,
         'latitude': 31.7742,
         'longitude': 35.2258},
        {'camera_make': 'Apple',
         'camera_model': 'iPhone 15 Pro',
         'datetime': '2025-01-14 10:00:00',
         'filename': 'IMG_007.jpg',
         'has_gps': True,
         'latitude': 32.794,
         'longitude': 34.9896},
        {'camera_make': 'Canon',
         'camera_model': 'EOS R5',
         'datetime': '2025-01-14 13:30:00',
         'filename': 'IMG_008.jpg',
         'has_gps': True,
         'latitude': 32.8115,
         'longitude': 34.9986},
        {'camera_make': 'Samsung',
         'camera_model': 'Galaxy S23',
         'datetime': '2025-01-15 09:30:00',
         'filename': 'IMG_009.jpg',
         'has_gps': True,
         'latitude': 31.253,
         'longitude': 34.7915},
        {'camera_make': 'Samsung',
         'camera_model': 'Galaxy S23',
         'datetime': '2025-01-15 14:00:00',
         'filename': 'IMG_010.jpg',
         'has_gps': True,
         'latitude': 31.262,
         'longitude': 34.8013},
        {'camera_make': 'Samsung',
         'camera_model': 'Galaxy S23',
         'datetime': '2025-01-16 11:00:00',
         'filename': 'IMG_011.jpg',
         'has_gps': True,
         'latitude': 29.5569,
         'longitude': 34.9498},
        {'camera_make': 'Apple',
         'camera_model': 'iPhone 15 Pro',
         'datetime': '2025-01-16 15:30:00',
         'filename': 'IMG_012.jpg',
         'has_gps': True,
         'latitude': 29.54,
         'longitude': 34.9415}
    ]
    results = analyze_agent_activity(mock_data)
    for insight in results['insights']:
        print(f"• {insight}")


if __name__ == "__main__":
    test_system()