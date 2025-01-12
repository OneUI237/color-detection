from flask import Flask, request, jsonify, render_template
from PIL import Image
import cv2
import pandas as pd
import numpy as np
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# Pastikan folder untuk menyimpan gambar ada
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Membaca file CSV warna
index = ["color", "color_name", "hex", "R", "G", "B"]
csv = pd.read_csv("colors.csv", names=index, header=None)

# Fungsi untuk mendapatkan nama warna berdasarkan nilai RGB
def getColorName(R, G, B):
    minimum = 10000
    cname = "Unknown"
    for i in range(len(csv)):
        d = abs(R - int(csv.loc[i, "R"])) + abs(G - int(csv.loc[i, "G"])) + abs(B - int(csv.loc[i, "B"]))
        if d <= minimum:
            minimum = d
            cname = csv.loc[i, "color_name"]
    return cname

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        print("Tidak ada file dalam permintaan.")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["image"]
    if file.filename == "":
        print("Tidak ada file yang dipilih.")
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    print(f"Nama file: {filename}")
    print(f"File path absolut: {filepath}")

    try:
        file.save(filepath)
        print(f"File berhasil disimpan ke: {filepath}")
        return jsonify({"message": "Image uploaded successfully", "filepath": filepath})
    except Exception as e:
        print(f"Kesalahan saat menyimpan file: {e}")
        return jsonify({"error": "File could not be saved"}), 500


@app.route("/get_color", methods=["POST"])
def get_color():
    data = request.json
    filepath = data.get("filepath")
    x = data.get("x")
    y = data.get("y")

    # Debugging
    print("Data diterima dari frontend:", data)
    print("File absolute path:", os.path.abspath(filepath))

    if not filepath or x is None or y is None:
        return jsonify({"error": "Invalid data"}), 400

    # Membaca gambar menggunakan OpenCV
    filepath = os.path.abspath(filepath)
    img = cv2.imread(filepath)
    if img is None:
        return jsonify({"error": "Image not found"}), 404
    

    # Validasi koordinat
    height, width, _ = img.shape
    if not (0 <= x < width and 0 <= y < height):
        return jsonify({"error": "Coordinates out of bounds"}), 400

    # Mendapatkan warna pada koordinat (x, y)
    b, g, r = img[y, x]
    color_name = getColorName(r, g, b)

    return jsonify({
        "color_name": color_name,
        "rgb": {"r": int(r), "g": int(g), "b": int(b)}
    })

if __name__ == "__main__":
    app.run(debug=True)
