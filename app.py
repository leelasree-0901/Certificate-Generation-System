from flask import Flask, render_template, request, redirect, url_for
import os, csv, uuid
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
app.secret_key = 'secret'
os.makedirs('uploads', exist_ok=True)
os.makedirs('static/certificates', exist_ok=True)

@app.route('/')
def dashboard():
    count = len(os.listdir('static/certificates'))
    return render_template('dashboard.html', count=count)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username')=='admin':
            return redirect(url_for('upload'))
    return render_template('login.html')

@app.route('/upload', methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        path = os.path.join('uploads', file.filename)
        file.save(path)
        count=0
        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = list(row.values())[0].strip()
                if not name: continue
                cid = str(uuid.uuid4())[:8]

                img = Image.open('static/template.jpg').convert("RGB")
                W,H = img.size
                draw = ImageDraw.Draw(img)
                # Cover any old name text
                draw.rectangle([int(W*0.18), int(H*0.38), int(W*0.82), int(H*0.58)], fill=(249,243,232))

                try:
                    name_font = ImageFont.truetype("arial.ttf", int(W*0.08))
                    id_font = ImageFont.truetype("arial.ttf", int(W*0.018))
                except:
                    name_font = ImageFont.load_default()
                    id_font = ImageFont.load_default()

                # Gold cursive name
                bbox = draw.textbbox((0,0), name, font=name_font)
                tw = bbox[2]-bbox[0]
                x = (W-tw)//2
                y = int(H*0.40)
                draw.text((x, y), name, fill='#8B6A2A', font=name_font)

                # ID at bottom
                draw.text((60, H-60), f"ID: {cid} | Verify at /verify", fill='#777', font=id_font)

                img.save(f'static/certificates/{name}_{cid}.jpg', quality=95)
                count+=1
        return f"<h1>{count} Certificates Generated!</h1><a href='/'>Dashboard</a> | <a href='/verify'>Verify</a>"
    return render_template('upload.html')

@app.route('/verify', methods=['GET','POST'])
def verify():
    certs = os.listdir('static/certificates')
    result = None
    if request.method == 'POST':
        s = request.form.get('cert_id','').lower()
        found = [c for c in certs if s in c.lower()]
        result = f"VALID - {found[0]}" if found else "INVALID"
    return render_template('verify.html', certs=certs, result=result)

app.run(debug=True)