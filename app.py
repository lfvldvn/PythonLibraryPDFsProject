from flask import Flask, render_template, redirect, url_for, session, flash, request, Response
import os
import requests
import json
from werkzeug.security import check_password_hash, generate_password_hash
from urllib.parse import quote

# 🔥 BASE URLs
PDF_BASE_URL = "https://aphilly.com/libraryProject/PDFbooks/"
THUMBNAIL_BASE_URL = "https://aphilly.com/libraryProject/thumbnails/"
DEFAULT_THUMB = "https://via.placeholder.com/150x220?text=PDF"

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

# 🔐 senha admin (gerada uma vez ao iniciar)
admin_password_hash = generate_password_hash('1Q@Z0OkM*')


# 📚 LISTA DE PDFs (JSON)
def get_pdf_files():
    try:
        with open('books.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

            # segurança: garante que sempre seja lista
            if isinstance(data, list):
                return data
            else:
                print("JSON inválido (não é lista)")
                return []

    except FileNotFoundError:
        print("books.json não encontrado")
        return []

    except json.JSONDecodeError:
        print("Erro ao decodificar JSON")
        return []

    except Exception as e:
        print(f"Erro inesperado: {e}")
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

    pdfs = []
    for pdf in pdf_files:
        pdfs.append({
            "name": pdf,
            "url": get_pdf_url(pdf),
            "thumbnail": get_thumbnail_url(pdf)
        })

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
        password = request.form.get('password', '')

        if check_password_hash(admin_password_hash, password):
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


# 🔥 DOWNLOAD FORÇADO (STREAM)
@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        pdf_url = get_pdf_url(filename)
        r = requests.get(pdf_url, stream=True, timeout=10)

        if r.status_code != 200:
            flash("Erro ao baixar o arquivo.", "error")
            return redirect(url_for('index'))

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

    except Exception as e:
        print(f"Erro no download: {e}")
        flash("Erro inesperado no download.", "error")
        return redirect(url_for('index'))


# ❌ DELETE (SIMBÓLICO)
@app.route('/delete/<path:filename>')
def delete_file(filename):
    if not session.get('logged_in'):
        flash('Você precisa fazer login para excluir arquivos.', 'error')
        return redirect(url_for('login'))

    flash(f'O arquivo "{filename}" deve ser removido diretamente no servidor aphilly.', 'warning')
    return redirect(url_for('index'))


# 🚀 RUN
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
