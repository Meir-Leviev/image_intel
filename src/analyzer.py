from math import radians, cos, sin, asin, sqrt
from datetime import datetime


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


def find_geo_clusters(images_data, threshold_km=1.0):
    clusters = []
    # התאמה למפתחות latitude ו-longitude
    geo_images = [img for img in images_data if "latitude" in img and "longitude" in img]
    for i in range(len(geo_images)):
        for j in range(i + 1, len(geo_images)):
            dist = calculate_distance(geo_images[i]["latitude"], geo_images[i]["longitude"],
                                      geo_images[j]["latitude"], geo_images[j]["longitude"])
            if dist <= threshold_km:
                clusters.append({
                    "ids": [geo_images[i].get("filename"), geo_images[j].get("filename")],
                    "distance_km": round(dist, 2)
                })
    return clusters


def detect_time_gaps(sorted_images, gap_hours=12):
    gaps = []
    fmt = "%Y-%m-%d %H:%M:%S"
    for i in range(1, len(sorted_images)):
        t1 = datetime.strptime(sorted_images[i - 1]["datetime"], fmt)
        t2 = datetime.strptime(sorted_images[i]["datetime"], fmt)
        diff = (t2 - t1).total_seconds() / 3600
        if diff >= gap_hours:
            gaps.append({
                "at_date": sorted_images[i - 1]["datetime"],
                "gap_duration": round(diff, 1)
            })
    return gaps


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
    sorted_images = sorted(
        [img for img in images_data if img.get("datetime")],
        key=lambda x: x["datetime"]
    )

    if not sorted_images:
        return {"error": "No valid data"}

    switches = detect_camera_switches(sorted_images)
    gaps = detect_time_gaps(sorted_images)
    clusters = find_geo_clusters(sorted_images)
    returns = detect_location_returns(sorted_images)

    insights = []
    unique_cams = list(set(img.get("camera_model") for img in sorted_images if img.get("camera_model")))
    insights.append(f"מכשירים: {', '.join(unique_cams)}")

    for s in switches:
        insights.append(f"החלפת מכשיר ב-{s['date']}: {s['from']} -> {s['to']}")
    for g in gaps:
        insights.append(f"פער זמן של {g['gap_duration']} שעות ב-{g['at_date']}")
    if clusters:
        insights.append(f"נמצאו {len(clusters)} ריכוזים גיאוגרפיים")
    for r in returns:
        insights.append(f"חזרה למיקום ב-{r['date']} (ביקור קודם: {r['original_date']})")

    return {
        "metadata": {
            "total": len(sorted_images),
            "range": f"{sorted_images[0]['datetime']} - {sorted_images[-1]['datetime']}"
        },
        "insights": insights,
        "raw": {
            "switches": switches,
            "gaps": gaps,
            "clusters": clusters,
            "returns": returns
        }
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

    print("--- מריץ ניתוח על נתוני דוגמה ---")
    results = analyze_agent_activity(mock_data)
    for insight in results['insights']:
        print(f"• {insight}")


if __name__ == "__main__":
    test_system()