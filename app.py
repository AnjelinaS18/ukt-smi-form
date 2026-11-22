import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import openpyxl

app = Flask(__name__)
app.secret_key = 'kunci_rahasia_ukt_smi_desember_2026'

# Konfigurasi Database & Folder Upload Foto
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///peserta.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Struktur Tabel Database
class Peserta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama_lengkap = db.Column(db.String(150), nullable=False)
    jenis_kelamin = db.Column(db.String(20), nullable=False)
    ttl = db.Column(db.String(100), nullable=False)
    alamat = db.Column(db.Text, nullable=False)
    agama = db.Column(db.String(50), nullable=False)
    tingkatan_sabuk = db.Column(db.String(50), nullable=False)
    ukuran_jersey = db.Column(db.String(10), nullable=False)
    no_hp = db.Column(db.String(20), nullable=False)
    asal_unit = db.Column(db.String(100), nullable=False)
    foto_filename = db.Column(db.String(200), nullable=False)
    nama_jersey = db.Column(db.String(50), nullable=False)

with app.app_context():
    db.create_all()

# Halaman Peserta (Formulir Pendaftaran)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('foto')
        filename = ''
        if file and file.filename != '':
            filename = f"{int(datetime.now().timestamp())}_{secure_filename(file.filename)}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        peserta_baru = Peserta(
            nama_lengkap=request.form['nama_lengkap'],
            jenis_kelamin=request.form['jenis_kelamin'],
            ttl=request.form['ttl'],
            alamat=request.form['alamat'],
            agama=request.form['agama'],
            tingkatan_sabuk=request.form['tingkatan_sabuk'],
            ukuran_jersey=request.form['ukuran_jersey'],
            no_hp=request.form['no_hp'],
            asal_unit=request.form['asal_unit'],
            foto_filename=filename,
            nama_jersey=request.form['nama_jersey']
        )
        db.session.add(peserta_baru)
        db.session.commit()
        return render_template('sukses.html', nama=request.form['nama_lengkap'])
    
    return render_template('index.html')

# Halaman Login Admin
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'silat123':
            session['admin'] = True
            return redirect(url_for('admin'))
    return render_template('login.html')

# Halaman Dashboard Admin
@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))
    semua_peserta = Peserta.query.all()
    return render_template('admin.html', peserta=semua_peserta)

# Fitur Edit Data oleh Admin
@app.route('/admin/edit/<int:id>', methods=['POST'])
def edit_peserta(id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    data = Peserta.query.get_or_404(id)
    data.nama_lengkap = request.form['nama_lengkap']
    data.tingkatan_sabuk = request.form['tingkatan_sabuk']
    data.ukuran_jersey = request.form['ukuran_jersey']
    data.nama_jersey = request.form['nama_jersey']
    data.no_hp = request.form['no_hp']
    db.session.commit()
    return redirect(url_for('admin'))

# Fitur Download Excel (.xlsx)
@app.route('/admin/export')
def export_excel():
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Data Peserta UKT SMI"
    
    headers = ['No', 'Nama Lengkap', 'Jenis Kelamin', 'TTL', 'Alamat', 'Agama', 
               'Tingkatan Sabuk', 'Ukuran Jersey', 'No HP', 'Asal Unit', 'Nama di Jersey', 'Link Foto']
    ws.append(headers)

    semua_peserta = Peserta.query.all()
    for idx, p in enumerate(semua_peserta, start=1):
        link_foto = url_for('static', filename=f'uploads/{p.foto_filename}', _external=True)
        ws.append([idx, p.nama_lengkap, p.jenis_kelamin, p.ttl, p.alamat, p.agama,
                   p.tingkatan_sabuk, p.ukuran_jersey, p.no_hp, p.asal_unit, p.nama_jersey, link_foto])

    file_excel = "Data_Peserta_UKT_SMI.xlsx"
    wb.save(file_excel)
    return send_file(file_excel, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)