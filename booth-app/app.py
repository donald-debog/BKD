from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import uuid
from PIL import Image, ImageEnhance
import qrcode
from datetime import datetime
import subprocess

session_map = {}

app = Flask(__name__)
UPLOAD_FOLDER = "photos/current"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def generate_short_code():
    timestamp = datetime.now().strftime("%H%M%S")  # HHMMSS (24-hour)
    return f"bk-formal-{timestamp}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start_session():
    session_id = str(uuid.uuid4())
    short_code = generate_short_code()

    session_map[session_id] = short_code  # store mapping

    session_path = os.path.join(UPLOAD_FOLDER, session_id)
    os.makedirs(session_path, exist_ok=True)

    return redirect(url_for("session", session_id=session_id))

@app.route("/session/<session_id>")
def session(session_id):
    session_path = os.path.join(UPLOAD_FOLDER, session_id)
    if not os.path.isdir(session_path):
        return "Session not found", 404
    photo_files = os.listdir(session_path)
    return render_template("session.html", session_id=session_id, photo_files=photo_files)

@app.route("/finish/<session_id>", methods=["POST"])
def finish(session_id):
    session_path = os.path.join(UPLOAD_FOLDER, session_id)
    if not os.path.isdir(session_path):
        return "Session not found", 404

    print(">> Starting camera import...")

    try:
        # First command: Get all files from the camera
        result = subprocess.run([
            "gphoto2",
            "--camera", "Canon EOS 1D X",
            "--folder", "/store_00010001/DCIM/100EOS1D",
            "--get-all-files",
            "--filename", os.path.join(session_path, "photo_%n.%C"),
            "--force-overwrite"
        ], capture_output=True, text=True, check=True)
        print(f"Camera import output: {result.stdout}")
        
        # Check if files were downloaded before deleting
        photos = [f for f in os.listdir(session_path) if f.lower().endswith(".jpg")]
        if photos:
            print(f"Successfully downloaded {len(photos)} photos. Now deleting from camera...")
            # Second command: Delete files after successful download
            delete_result = subprocess.run([
                "gphoto2",
                "--camera", "Canon EOS 1D X",
                "--folder", "/store_00010001/DCIM/100EOS1D",
                "--delete-all-files"
            ], capture_output=True, text=True, check=False)
            print(f"Delete result: {delete_result.stdout}")
        else:
            print("No photos were downloaded, skipping delete operation")
            
    except subprocess.CalledProcessError as e:
        print(f"Error running gphoto2: {e}")
        print(f"Error output: {e.stderr}")

    print(">> Done importing from camera.")

    # ✅ Enhance and overwrite each photo
    photos = [
        os.path.join(session_path, f)
        for f in os.listdir(session_path)
        if f.lower().endswith(".jpg")
    ]

    for path in photos:
        img = Image.open(path)
        img = ImageEnhance.Contrast(img).enhance(1.2)
        img = ImageEnhance.Brightness(img).enhance(1.1)
        img = ImageEnhance.Sharpness(img).enhance(1.5)
        img.save(path, quality=90)  # Overwrites original

    # ✅ Upload photos to Supabase
    try:
        from supabase_uploader import upload_session_photos
        print(">> Uploading photos to Supabase...")
        upload_session_photos(session_path, short_code)
        print(">> Done uploading to Supabase.")
    except Exception as e:
        print(f"Error uploading to Supabase: {e}")

    # ✅ Create QR with short code
    short_code = session_map.get(session_id, session_id)
    qr_url = f"https://bkd-photo.vercel.app/photo/{short_code}"
    qr = qrcode.make(qr_url)
    qr_path = os.path.join(session_path, "qr.png")
    qr.save(qr_path)

    qr_web_path = f"photos/current/{session_id}/qr.png"
    return render_template("qr.html", session_id=session_id, qr_image=qr_web_path)

@app.route('/photos/<path:filename>')
def serve_photo_file(filename):
    return send_from_directory('photos', filename)

if __name__ == "__main__":
    app.run(debug=True)
