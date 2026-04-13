import io

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from models import db, User
from utils import analyze_file
import os

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------- REGISTER --------
@app.route('/register', methods=['POST'])
def register():
    data = request.json

    username = data.get("username")
    password = data.get("password")

    existing = User.query.filter_by(username=username).first()
    if existing:
        return jsonify({"message": "User already exists"}), 400

    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Registered successfully"})


# -------- LOGIN --------
@app.route('/login', methods=['POST'])
def login():
    data = request.json

    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username, password=password).first()

    if user:
        return jsonify({"message": "Login success"})
    else:
        return jsonify({"message": "Invalid credentials"}), 401


# -------- FILE UPLOAD + ANALYZE --------
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    result = analyze_file(path)

    return jsonify(result)


# -------- PDF REPORT --------
from flask import send_file, request
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
import io

@app.route('/report', methods=['POST'])
def report():
    data = request.json

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()

    content = [
        Paragraph(f"Rows: {data['rows']}", styles['Normal']),
        Paragraph(f"Columns: {data['cols']}", styles['Normal']),
        Paragraph(f"Rows with Errors: {data['error_rows']}", styles['Normal']),
        Paragraph(f"Total Errors: {data['errors']}", styles['Normal']),
        Paragraph(f"Quality Score: {data['quality']}%", styles['Normal']),
        Paragraph("---- Error List ----", styles['Normal'])
    ]

    for err in data["error_list"]:
        content.append(Paragraph(str(err), styles['Normal']))

    doc.build(content)

    buffer.seek(0)  # ✅ VERY IMPORTANT (only once)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="report.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))