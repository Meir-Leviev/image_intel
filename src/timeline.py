import datetime


def get_day_color(date_str):
    # Generate a background color based on the date string
    colors = [
        "#aed9e0",  # muted blue
        "#ffb6b9",  # muted pink
        "#b8e0d2",  # muted green
        "#fae3b0",  # muted yellow
        "#d4c4fb",  # muted purple
        "#a8e6cf",  # muted teal
        "#ffdac1",  # muted peach
        "#e2f0cb",  # muted lime
        "#c3bef0",  # muted periwinkle
        "#ffb7b2"  # muted salmon
    ]
    day_hash = sum(ord(c) for c in date_str)
    return colors[day_hash % len(colors)]

def create_timeline(images_data):
    # Filter out images that do not have a datetime value
    dated_images = [img for img in images_data if img.get("datetime")]

    # Sort the remaining images chronologically
    dated_images.sort(key=lambda x: x["datetime"])

    # Include inline CSS for hover effects and layout
    html = '''
    <style>
        body { font-family: sans-serif; background: #fafafa; }
        .timeline-container { position:relative; padding:20px; max-width: 600px; margin: auto; }
        .center-line { position:absolute; left:50%; width:2px; height:100%; background:#ccc; }
        .timeline-item { 
            margin: 20px 0; 
            padding: 15px; 
            border-radius: 8px; 
            transition: transform 0.2s, box-shadow 0.2s; 
            width: 40%;
            position: relative;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .timeline-item:hover { 
            transform: scale(1.05); 
            box-shadow: 0 6px 12px rgba(0,0,0,0.15); 
            z-index: 10;
        }
        .left { float: left; clear: both; text-align: right; margin-right: 10%; }
        .right { float: right; clear: both; text-align: left; margin-left: 10%; }
        .gap-alert { text-align: center; color: #d9534f; font-weight: bold; font-size: 0.85em; clear: both; margin: 15px 0; background: #fdf5f5; padding: 5px; border-radius: 4px;}
        .hover-details { display: none; font-size: 0.8em; color: #555; margin-top: 10px; border-top: 1px solid #ddd; padding-top: 5px; }
        .timeline-item:hover .hover-details { display: block; }
        .clearfix::after { content: ""; clear: both; display: table; }
    </style>
    <div class="timeline-container clearfix">
        <div class="center-line"></div>
    '''

    prev_dt = None

    # Loop through the sorted images to create timeline items
    for i, img in enumerate(dated_images):
        # Parse the datetime string into a datetime object
        dt_obj = datetime.datetime.strptime(img["datetime"], "%Y-%m-%d %H:%M:%S")
        date_only = dt_obj.strftime("%Y-%m-%d")

        # Check for time gaps greater than 12 hours
        if prev_dt:
            diff = dt_obj - prev_dt
            if diff.total_seconds() > 12 * 3600:
                html += f'<div class="gap-alert">Gap of over 12 hours! ({diff})</div>\n'

        prev_dt = dt_obj

        # Determine visual properties
        side_class = "left" if i % 2 == 0 else "right"
        bg_color = get_day_color(date_only)

        # Extract location data for the hover details
        lat = img.get("latitude", "N/A")
        lon = img.get("longitude", "N/A")
        gps_status = 'Yes' if img.get('has_gps') else 'No'

        # Append the HTML string for the current image
        html += f'''
        <div class="timeline-item {side_class}" style="background-color: {bg_color};">
            <strong>{img["datetime"]}</strong><br>
            {img["filename"]}<br>
            <small>{img.get("camera_model", "Unknown")}</small>
            <div class="hover-details">
                <strong>Location:</strong> {lat}, {lon}<br>
                <strong>GPS:</strong> {gps_status}
            </div>
        </div>
        '''

    html += '</div>\n'
    return html


if __name__ == "__main__":
    fake_data = [{'camera_make': 'Samsung',
  'camera_model': 'Galaxy S23',
  'datetime': '2025-01-12 08:30:00',
  'filename': 'IMG_001.jpg',
  'has_gps': True,
  'latitude': 32.0853,
  'longitude': 34.7818},
 {'camera_make': 'Samsung',
  'camera_model': 'Galaxy S23',
  'datetime': '2025-01-12 14:00:00',
  'filename': 'IMG_003.jpg',
  'has_gps': True,
  'latitude': 32.0667,
  'longitude': 34.7667},
 {'camera_make': 'Samsung',
  'camera_model': 'Galaxy S23',
  'datetime': '2025-01-12 11:15:00',
  'filename': 'IMG_002.jpg',
  'has_gps': True,
  'latitude': 32.0804,
  'longitude': 34.7805},
 {'camera_make': 'Apple',
  'camera_model': 'iPhone 15 Pro',
  'datetime': '2025-01-16 15:30:00',
  'filename': 'IMG_012.jpg',
  'has_gps': True,
  'latitude': 29.54,
  'longitude': 34.9415},
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
 {'camera_make': 'Apple',
  'camera_model': 'iPhone 15 Pro',
  'datetime': '2025-01-13 12:30:00',
  'filename': 'IMG_005.jpg',
  'has_gps': True,
  'latitude': 31.778,
  'longitude': 35.2354},
 {'camera_make': 'Samsung',
  'camera_model': 'Galaxy S23',
  'datetime': '2025-01-16 11:00:00',
  'filename': 'IMG_011.jpg',
  'has_gps': True,
  'latitude': 29.5569,
  'longitude': 34.9498},
 {'camera_make': 'Samsung',
  'camera_model': 'Galaxy S23',
  'datetime': '2025-01-15 14:00:00',
  'filename': 'IMG_010.jpg',
  'has_gps': True,
  'latitude': 31.262,
  'longitude': 34.8013},
 {'camera_make': 'Apple',
  'camera_model': 'iPhone 15 Pro',
  'datetime': '2025-01-13 09:00:00',
  'filename': 'IMG_004.jpg',
  'has_gps': True,
  'latitude': 31.7683,
  'longitude': 35.2137},
 {'camera_make': 'Samsung',
  'camera_model': 'Galaxy S23',
  'datetime': '2025-01-15 09:30:00',
  'filename': 'IMG_009.jpg',
  'has_gps': True,
  'latitude': 31.253,
  'longitude': 34.7915},
 {'camera_make': 'Canon',
  'camera_model': 'EOS R5',
  'datetime': '2025-01-14 13:30:00',
  'filename': 'IMG_008.jpg',
  'has_gps': True,
  'latitude': 32.8115,
  'longitude': 34.9986}]
    html = create_timeline(fake_data)
    with open("test_timeline.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("timeline saved to test_timeline.html")
