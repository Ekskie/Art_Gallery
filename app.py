import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from supabase import create_client
from dotenv import load_dotenv
import sys

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supa = create_client(SUPABASE_URL, SUPABASE_KEY)

# Allowed file types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Check allowed file type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    response = supa.table("artworks").select("*").execute()
    artworks = response.data if response.data else []
    return render_template('index.html', artworks=artworks)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    print("Upload function triggered!", file=sys.stderr)

    if request.method == 'POST':
        print("POST request received", file=sys.stderr)

        if 'file' not in request.files:
            print("No file found in request", file=sys.stderr)
            return "No file part", 400
        
        file = request.files['file']
        title = request.form.get('title', '').strip()
        artist = request.form.get('artist', '').strip()

        print(f"Received title: {title}, artist: {artist}", file=sys.stderr)

        if file.filename == '' or not allowed_file(file.filename):
            print("Invalid file", file=sys.stderr)
            return "Invalid file", 400

        filename = secure_filename(file.filename)
        bucket_name = "artworks"
        file_path = f"{filename}"  # File path inside the bucket

        # ✅ **Read the file as bytes**
        file_data = file.read()

        # ✅ **Upload file using bytes**
        upload_response = supa.storage.from_(bucket_name).upload(file_path, file_data, {"content-type": file.content_type})

        print(f"Upload response: {upload_response}", file=sys.stderr)

        if not upload_response:
            print("Upload failed", file=sys.stderr)
            return "Upload failed", 500

        # ✅ **Insert into Supabase Database**
        response = supa.table("artworks").insert({"title": title, "artist": artist, "filename": filename}).execute()

        print(f"Database insert response: {response}", file=sys.stderr)

        if response.data is None:
            print("Failed to insert into database", file=sys.stderr)
            return "Failed to insert into database", 500

        return redirect(url_for('index'))
    
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
