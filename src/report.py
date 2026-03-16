import os
from datetime import datetime
from extractor import extract_all, get_base64_image
from map_view import create_map
from timeline import create_timeline
from analyzer import analyze_agent_activity


""""זה הדוגמה מהמדריך לקבוצה 3
מומלץ לשנות לאנגלית
"""


def create_report(images_data, map_html, timeline_html, analysis):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir,"icon.jpeg")
    ico = get_base64_image(full_path)
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    insights_html = ""
    for insight in analysis.get("insights", []):
        insights_html += f"<li>{insight}</li>"

    cameras_html = ""
    for cam in analysis.get("unique_cameras", []):
        cameras_html += f"<span class='badge'>{cam}</span> "

    html = f"""
    <!DOCTYPE html>
    <html lang="en" dir="ltr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Image Intel Report</title>
        <style>
            :root {{
                --text-main: #1d1d1f;
                --text-secondary: #86868b;
                --bg-main: #fbfbfd;
                --bg-card: #ffffff;

                /* Group colors based on image_0.png */
                --color-group1: #f3c2bc; 
                --color-group2: #c4d9dc; 
                --color-group3: #f1dfbc; 
                --color-group4: #d6caed; 
                --color-group5: #badfc9; 
            }}

            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background-color: var(--bg-main);
                color: var(--text-main);
                margin: 0;
                padding: 40px 20px;
                line-height: 1.47059;
                font-weight: 400;
                letter-spacing: -.022em;
            }}

            .container {{
                max-width: 980px;
                margin: 0 auto;
            }}

            /* Subtle color gradient in the header for interest */
            .header {{
                text-align: center;
                padding: 60px 20px 40px;
                background: linear-gradient(135deg, var(--color-group1) 0%, var(--color-group5) 100%);
                border-radius: 18px;
                margin-bottom: 30px;
                color: #fff;
            }}

            .header h1 {{
                font-size: 48px;
                font-weight: 700;
                letter-spacing: -0.005em;
                margin: 0 0 8px 0;
                text-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }}

            .header p {{
                font-size: 21px;
                margin: 0;
                color: rgba(255, 255, 255, 0.8);
            }}

            .section {{
                background: var(--bg-card);
                padding: 45px;
                margin-bottom: 30px;
                border-radius: 18px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.02), 0 1px 3px rgba(0,0,0,0.04);
                border-top: 2px solid transparent;
            }}

            .section:nth-of-type(1) {{ border-top-color: var(--color-group1); }}
            .section:nth-of-type(2) {{ border-top-color: var(--color-group2); }}
            .section:nth-of-type(3) {{ border-top-color: var(--color-group3); }}
            .section:nth-of-type(4) {{ border-top-color: var(--color-group4); }}
            .section:nth-of-type(5) {{ border-top-color: var(--color-group5); }}

            .section h2 {{
                text-align: center;
                font-size: 28px;
                font-weight: 600;
                margin-top: 0;
                margin-bottom: 35px;
            }}

            /* Color-coded stats cards */
            .stats {{
                display: flex;
                gap: 20px;
                justify-content: center;
                flex-wrap: wrap;
            }}

            .stat-card {{
                text-align: center;
                flex: 1 1 calc(33.333% - 20px);
                min-width: 250px;
                padding: 30px;
                border-radius: 12px;
                background: rgba(0,0,0,0.01); 
            }}

            .stat-card:nth-child(1) {{ background-color: var(--color-group1); }}
            .stat-card:nth-child(2) {{ background-color: var(--color-group2); }}
            .stat-card:nth-child(3) {{ background-color: var(--color-group3); }}

            .stat-number {{
                font-size: 56px;
                font-weight: 700;
                color: var(--text-main);
                letter-spacing: -0.02em;
                line-height: 1.1;
            }}

            .stat-label {{
                font-size: 14px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                color: var(--text-secondary);
                margin-top: 8px;
            }}

            ul {{
                font-size: 17px;
                padding-left: 20px;
                color: var(--text-main);
            }}

            li {{
                margin-bottom: 12px;
            }}

            /* Custom styles for the Key Insights list */
            .insights-list {{
                list-style: none; 
                padding: 0;
                margin: 0;
                display: flex;
                flex-direction: column;
                gap: 16px; 
            }}

            .insights-list li {{
                background-color: rgba(0, 0, 0, 0.02);
                padding: 18px 24px;
                border-radius: 14px;
                border-left: 6px solid var(--color-group4); 
                margin-bottom: 0; 
                font-size: 17px;
                line-height: 1.5;
                display: flex;
                align-items: flex-start;
                transition: all 0.2s ease;
            }}

            .insights-list li:hover {{
                background-color: rgba(0, 0, 0, 0.04);
                transform: translateX(4px); 
            }}

            .insights-list li::before {{
                content: "💡"; 
                margin-right: 14px;
                font-size: 20px;
                line-height: 1.3;
            }}

            /* Updated badge styling with darker color and center alignment support */
            .badge {{
                color: #ffffff;
                padding: 8px 16px;
                border-radius: 20px;
                margin: 6px;
                display: inline-block;
                background-color: #6a4c93; 
                font-weight: 500;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}

            /* Container to center the badges */
            .badges-container {{
                text-align: center;
                width: 100%;
            }}

            .footer {{
                text-align: center;
                color: var(--text-secondary);
                font-size: 12px;
                margin-top: 60px;
                padding-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Image Intel Report</h1>
                <p>Created: {now}</p>
            </div>

            <div class="section">
                <h2>Summary</h2>
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">{analysis.get('total_images', 0)}</div>
                        <div class="stat-label">Images</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{analysis.get('images_with_gps', 0)}</div>
                        <div class="stat-label">With GPS</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len(analysis.get('unique_cameras', []))}</div>
                        <div class="stat-label">Devices</div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>Key Insights</h2>
                <ul class="insights-list">
                    {insights_html}
                </ul>
            </div>

            <div class="section">
                <h2>Devices</h2>
                <div class="badges-container">
                    {cameras_html}
                </div>
            </div>

            <div class="section">
                <h2>Map</h2>
                {map_html}
            </div>

            <div class="section">
                <h2>Timeline</h2>
                {timeline_html}
            </div>

        </div>

        <div class="footer">
            Image Intel | Team #2<br>
            Yosef Chen | Meir Leviev | Ushi Philip | [The 4th member]<br>
            <h2><b>THANKS TO OUR GREAT TEACHER RONEN SHLIT"A</b></h2>
            <img src="{ico}" alt="Icon" style="width: 577.5px; height: auto; vertical-align: middle; margin-bottom: 150px;"><br>
        </div>
    </body>
    </html>
    """
    return html


if __name__ == "__main__":
    data =  extract_all("/Users/meirleviev/Desktop/PyCharm/image_intel/images/ready")
    map_html = create_map(data)
    timeline = create_timeline(data)
    analysis = analyze_agent_activity(data)

    report = create_report(data, map_html, timeline, analysis)
    with open("test_report.html", "w") as h:
        h.write(report)