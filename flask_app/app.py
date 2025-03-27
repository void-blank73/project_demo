from flask import Flask, render_template, request, jsonify, send_file
import os
import config
from ocr import process_pdfs
from evaluation import evaluate_answers

app = Flask(__name__, static_folder="static")

app.config["UPLOAD_FOLDER"] = config.UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = config.OUTPUT_FOLDER

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_files():
    question_paper = request.files.get("question_paper")
    answer_sheet = request.files.get("answer_sheet")

    if not question_paper or not answer_sheet:
        return jsonify({"error": "Both files are required!"}), 400

    q_path = os.path.join(app.config["UPLOAD_FOLDER"], "question_paper.pdf")
    a_path = os.path.join(app.config["UPLOAD_FOLDER"], "answer_sheet.pdf")

    question_paper.save(q_path)
    answer_sheet.save(a_path)

    return jsonify({"message": "Files uploaded successfully!"})

@app.route("/process", methods=["POST"])
def process():
    try:
        excel_path = process_pdfs()
        doc_path = evaluate_answers(excel_path)
        return jsonify({"message": "Processing completed!", "excel": excel_path, "doc": doc_path})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join(app.config["OUTPUT_FOLDER"], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "File not found!"}), 404

if __name__ == "__main__":
    app.run(debug=True)
