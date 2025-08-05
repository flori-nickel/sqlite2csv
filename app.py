from flask import Flask, send_file, request, render_template, jsonify
import sqlite3, pandas as pd, datetime, os, tempfile

app = Flask(__name__)

def filetime_to_datetime(ft):
    if ft is None:
        return None
    try:
        return datetime.datetime.utcfromtimestamp(ft / 10_000_000 - 11644473600)
    except:
        return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/export", methods=["POST"])
def export():
    file = request.files.get("db_file")
    if not file:
        return jsonify({"status": "error", "message": "Keine Datei empfangen."})

    try:
        temp_path = os.path.join(tempfile.gettempdir(), file.filename)
        file.save(temp_path)

        conn = sqlite3.connect(temp_path)
        df = pd.read_sql_query("SELECT EventText, Value2, RaiseTime FROM LoggedAlarm", conn)
        df["RaiseTime"] = pd.to_numeric(df["RaiseTime"], errors="coerce").apply(filetime_to_datetime)

        output_path = os.path.join(tempfile.gettempdir(), "LoggedAlarm_export.csv")
        df.to_csv(output_path, index=False, encoding="utf-8")
        conn.close()

        return send_file(
            output_path,
            as_attachment=True,
            download_name="LoggedAlarm_export.csv",
            mimetype="text/csv"
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
