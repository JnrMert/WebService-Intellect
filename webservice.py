from flask import Flask, request, render_template, jsonify
import requests
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
TARGET_URL = "http://test12.probizyazilim.com/Intellect/ExecuteTransaction.asmx/ExecuteTransaction"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# 📌 1️⃣ Kullanıcıya Dosya Yükleme Formunu Göster
@app.route("/")
def upload_form():
    return render_template("upload.html")

# 📌 2️⃣ Dosya Yükleme İşlemi
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "Dosya seçilmedi!"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Dosya adı geçersiz!"}), 400

    if not file.filename.endswith(".xml"):
        return jsonify({"error": "Sadece XML dosyaları kabul edilir!"}), 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    return jsonify({"message": "Dosya yüklendi!", "filename": file.filename})

# 📌 3️⃣ Yüklenen XML Dosyasını Gönderme
@app.route("/send", methods=["POST"])
def send_xml():
    file_name = request.json.get("filename")

    if not file_name:
        return jsonify({"error": "Dosya adı belirtilmedi!"}), 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file_name)

    if not os.path.exists(file_path):
        return jsonify({"error": "Dosya bulunamadı!"}), 404

    with open(file_path, "r", encoding="utf-8") as file:
        xml_data = file.read()

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(TARGET_URL, headers=headers, data={"Request": xml_data})

    return jsonify({"status": response.status_code, "response": response.text})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
