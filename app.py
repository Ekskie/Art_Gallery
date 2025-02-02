from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
import supabase

app = Flask(__name__)

# Supabase configuration
SUPABASE_URL = "https://kurxmuewzwtecbpixamh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt1cnhtdWV3end0ZWNicGl4YW1oIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg0Nzk2NTksImV4cCI6MjA1NDA1NTY1OX0.ZfvBRIHTqWiMdDH5pXfe7HYQWxImPFqoXfGqPDqWVqU"
supa = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

# File upload configuration
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    response = supa.table("artworks").select("*").execute()
    artworks = response.data if response.data else []
    return render_template('index.html', artworks=artworks)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        title = request.form['title']
        artist = request.form['artist']
        if file.filename == '' or not allowed_file(file.filename):
            return redirect(request.url)
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        supa.table("artworks").insert({"title": title, "artist": artist, "filename": filename}).execute()
        return redirect(url_for('index'))
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
