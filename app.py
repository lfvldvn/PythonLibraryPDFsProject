from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from werkzeug.security import check_password_hash, generate_password_hash

# 🔥 NOVO: URL BASE DOS PDFs (SEU SERVIDOR)
PDF_BASE_URL = "https://aphilly.com/libraryProject/PDFbooks/"

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

# 🔐 senha admin
admin_password = generate_password_hash('1Q@Z0OkM*')


# 📌 LISTA DE PDFs (AGORA VEM DO SEU SERVIDOR)
def get_pdf_files():
    """
    🔥 IMPORTANTE:
    Como o Render não acessa diretório local persistente,
    você precisa manter manualmente ou via API a lista de PDFs.
    """

    return [
        "livro1.pdf",
        "livro2.pdf",
        "livro3.pdf"
    ]


# 📌 GERAR URL COMPLETA DO PDF
def get_pdf_url(filename):
    return f"{PDF_BASE_URL}{filename}"


# 🏠 HOME
@app.route('/')
def index():
    pdf_files = get_pdf_files()
    logged_in = session.get('logged_in', False)

    # 🔥 monta lista com URL completa
    pdfs = [
        {
            "name": pdf,
            "url": get_pdf_url(pdf)
        }
        for pdf in pdf_files
    ]

    return render_template(
        'index.html',
        pdfs=pdfs,
        logged_in=logged_in
    )


# 👁️ VISUALIZAR PDF (REDIRECIONA PARA SEU SERVIDOR)
@app.route('/view/<path:filename>')
def view_pdf(filename):
    pdf_url = get_pdf_url(filename)
    return redirect(pdf_url)


# 🔐 LOGIN
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


# 🚪 LOGOUT
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Você foi desconectado.', 'success')
    return redirect(url_for('index'))


# ❌ DELETE (AGORA APENAS SIMBÓLICO)
@app.route('/delete/<path:filename>')
def delete_file(filename):
    if not session.get('logged_in'):
        flash('Você precisa fazer login para excluir arquivos.', 'error')
        return redirect(url_for('login'))

    # 🔥 IMPORTANTE:
    # Como os arquivos estão no aphilly, você não pode deletar direto daqui
    # (a menos que tenha API lá)

    flash(f'O arquivo {filename} foi marcado para exclusão (ação externa necessária).', 'warning')
    return redirect(url_for('index'))


# 🚀 RUN
if __name__ == '__main__':
    app.run(debug=True)
