from flask import Flask, render_template, request
import os

# הגדרת האפליקציה + תיקיית templates
app = Flask(__name__, template_folder="templates")


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/analyze', methods=['POST'])
def analyze_images():
    """מקבל קבצים שהמשתמש העלה, מריץ את כל המודולים, מחזיר דו"ח"""

    uploaded_files = request.files.getlist("photos")
    if not uploaded_files:
        return "לא נבחרו קבצים", 400

    # שמירה זמנית של הקבצים בספרייה זמנית
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdirname:
        for f in uploaded_files:
            file_path = os.path.join(tmpdirname, f.filename)
            f.save(file_path)

        # שלב 1: שליפת נתונים
        from extractor import extract_all
        images_data = extract_all(tmpdirname)

        # שלב 2: יצירת מפה
        from map_view import create_map
        map_html = create_map(images_data)

        # שלב 3: ציר זמן
        from timeline import create_timeline
        timeline_html = create_timeline(images_data)

        # שלב 4: ניתוח
        from analyzer import analyze
        analysis = analyze(images_data)

        # # שלב 5: הרכבת דו"ח
        # from report import create_report
        # report_html = create_report(images_data, map_html, timeline_html, analysis)

        return timeline_html


if __name__ == "__main__":
    app.run(debug=True)