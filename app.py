from flask import Flask, render_template, redirect, url_for, session, flash, request, Response
import os
import requests
=======
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, flash, abort
import os
import secrets
from werkzeug.utils import secure_filename, safe_join
>>>>>>> d67995e (Harden PDF upload security)
from werkzeug.security import check_password_hash, generate_password_hash
from urllib.parse import quote

# 🔥 BASE URLs
PDF_BASE_URL = "https://aphilly.com/libraryProject/PDFbooks/"
THUMBNAIL_BASE_URL = "https://aphilly.com/libraryProject/thumbnails/"
DEFAULT_THUMB = "https://via.placeholder.com/150x220?text=PDF"

app = Flask(__name__)
<<<<<<< HEAD
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')
=======
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

admin_password_hash = os.environ.get('ADMIN_PASSWORD_HASH')
admin_password_plain = os.environ.get('ADMIN_PASSWORD')
if admin_password_hash:
    ADMIN_PASSWORD_HASH = admin_password_hash
elif admin_password_plain:
    ADMIN_PASSWORD_HASH = generate_password_hash(admin_password_plain)
else:
    raise RuntimeError('Configure ADMIN_PASSWORD_HASH ou ADMIN_PASSWORD nas variaveis de ambiente.')
>>>>>>> d67995e (Harden PDF upload security)

# 🔐 senha admin (⚠️ depois vamos mover pra ENV)
admin_password = generate_password_hash('1Q@Z0OkM*')

<<<<<<< HEAD
=======

def _resolve_pdf_path(filename):
    resolved_path = safe_join(app.config['UPLOAD_FOLDER'], filename)
    if not resolved_path:
        abort(400)

    if os.path.basename(filename) != filename:
        abort(400)

    return resolved_path


def _get_or_create_csrf_token():
    token = session.get('csrf_token')
    if not token:
        token = secrets.token_hex(16)
        session['csrf_token'] = token
    return token


def _validate_csrf_token(token):
    expected = session.get('csrf_token')
    return bool(expected and token and secrets.compare_digest(expected, token))


@app.context_processor
def inject_csrf_token():
    return {'csrf_token': _get_or_create_csrf_token()}

def get_thumbnail_path(pdf_file):
    return os.path.join('static/thumbnails', f"{os.path.splitext(pdf_file)[0]}.png")
>>>>>>> d67995e (Harden PDF upload security)

# 📚 LISTA COMPLETA DOS PDFs
def get_pdf_files():
    try:
        with open('books.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar JSON: {e}")
        return []


# 🔗 URL DO PDF
def get_pdf_url(filename):
    return f"{PDF_BASE_URL}{quote(filename)}"


# 🖼️ URL DO THUMB
def get_thumbnail_url(filename):
    name = os.path.splitext(filename)[0]
    return f"{THUMBNAIL_BASE_URL}{quote(name)}.png"


# 🏠 HOME
@app.route('/')
def index():
    pdf_files = get_pdf_files()
    logged_in = session.get('logged_in', False)

<<<<<<< HEAD
    pdfs = [
        {
            "name": pdf,
            "url": get_pdf_url(pdf),
            "thumbnail": get_thumbnail_url(pdf)
        }
        for pdf in pdf_files
    ]
=======
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not session.get('logged_in'):
        flash('Voce precisa fazer login para enviar arquivos.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        if not _validate_csrf_token(request.form.get('csrf_token')):
            abort(400)

        uploaded_file = request.files.get('file')
        if not uploaded_file or not uploaded_file.filename:
            flash('Selecione um arquivo PDF.', 'error')
            return redirect(url_for('upload'))

        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)
            uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('Arquivo enviado com sucesso.', 'success')
            return redirect(url_for('index'))
        flash('Formato invalido. Envie apenas arquivos PDF.', 'error')
    return render_template('upload.html')
>>>>>>> d67995e (Harden PDF upload security)

    return render_template(
        'index.html',
        pdfs=pdfs,
        logged_in=logged_in,
        default_thumb=DEFAULT_THUMB
    )


# 🔐 LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not _validate_csrf_token(request.form.get('csrf_token')):
            abort(400)

        password = request.form['password']
<<<<<<< HEAD

        if check_password_hash(admin_password, password):
=======
        if check_password_hash(ADMIN_PASSWORD_HASH, password):
>>>>>>> d67995e (Harden PDF upload security)
            session['logged_in'] = True
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Senha incorreta!', 'error')

    return render_template('login.html')


# 🚪 LOGOUT
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Você foi desconectado.', 'success')
    return redirect(url_for('index'))

<<<<<<< HEAD

# 🔥 DOWNLOAD FORÇADO (STREAM)
@app.route('/download/<path:filename>')
def download_file(filename):
    pdf_url = get_pdf_url(filename)

    r = requests.get(pdf_url, stream=True)

    def generate():
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                yield chunk

    return Response(
        generate(),
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        },
        content_type='application/pdf'
    )


# ❌ DELETE (SIMBÓLICO)
@app.route('/delete/<path:filename>')
=======
@app.route('/delete/<path:filename>', methods=['POST'])
>>>>>>> d67995e (Harden PDF upload security)
def delete_file(filename):
    if not session.get('logged_in'):
        flash('Você precisa fazer login para excluir arquivos.', 'error')
        return redirect(url_for('login'))

<<<<<<< HEAD
    flash(f'O arquivo {filename} precisa ser removido diretamente no servidor aphilly.', 'warning')
    return redirect(url_for('index'))

=======
    if not _validate_csrf_token(request.form.get('csrf_token')):
        abort(400)

    file_path = _resolve_pdf_path(filename)
    thumbnail_path = get_thumbnail_path(filename)

    if os.path.exists(file_path):
        os.remove(file_path)

    if os.path.exists(thumbnail_path):
        os.remove(thumbnail_path)

    flash(f'O arquivo {filename} foi excluído com sucesso.', 'success')
    return redirect(url_for('index'))

def get_pdf_files():
    pdf_directory = 'pdfs'
    pdf_files = [f for f in os.listdir(pdf_directory) if f.lower().endswith('.pdf')]
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
d67995e (Harden PDF upload security)

# 🚀 RUN
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
