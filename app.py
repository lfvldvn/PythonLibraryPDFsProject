from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, flash
import os
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from pdf2image import convert_from_path

UPLOAD_FOLDER = 'pdfs'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')
admin_password = generate_password_hash('1Q@Z0OkM*')  # Hash para a senha 'admin123'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_thumbnail_path(pdf_file):
    return os.path.join('static/thumbnails', f"{os.path.splitext(pdf_file)[0]}.png")

@app.route('/')
def index():
    pdf_files = get_pdf_files()
    generate_thumbnails(pdf_files)
    logged_in = session.get('logged_in', False)
    return render_template('index.html', pdf_files=pdf_files, os=os, logged_in=logged_in)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)
            uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/pdfs/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/view/<path:filename>')
def view_pdf(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, mimetype='application/pdf')
    else:
        flash('Arquivo não encontrado.', 'error')
        return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if check_password_hash(admin_password, password):
            session['logged_in'] = True
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Senha incorreta!', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Você foi desconectado.', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<path:filename>')
def delete_file(filename):
    if not session.get('logged_in'):
        flash('Você precisa fazer login para excluir arquivos.', 'error')
        return redirect(url_for('login'))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    thumbnail_path = get_thumbnail_path(filename)

    if os.path.exists(file_path):
        os.remove(file_path)

    if os.path.exists(thumbnail_path):
        os.remove(thumbnail_path)

    flash(f'O arquivo {filename} foi excluído com sucesso.', 'success')
    return redirect(url_for('index'))

def get_pdf_files():
    pdf_directory = 'pdfs'
    pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
    return pdf_files

def generate_thumbnails(pdf_files):
    pdf_directory = 'pdfs'
    thumbnails_directory = 'static/thumbnails'

    if not os.path.exists(thumbnails_directory):
        os.makedirs(thumbnails_directory)

    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_directory, pdf_file)
        thumbnail_path = get_thumbnail_path(pdf_file)

        if not os.path.exists(thumbnail_path):
            images = convert_from_path(pdf_path, first_page=0, last_page=1)
            if images:
                images[0].save(thumbnail_path, 'PNG')

if __name__ == '__main__':
    app.run(debug=True)
