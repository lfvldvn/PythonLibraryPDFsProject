from flask import Flask, render_template, redirect, url_for, session, flash, request, Response
import os
import requests
from werkzeug.security import check_password_hash, generate_password_hash
from urllib.parse import quote

# 🔥 BASE URLs
PDF_BASE_URL = "https://aphilly.com/libraryProject/PDFbooks/"
THUMBNAIL_BASE_URL = "https://aphilly.com/libraryProject/thumbnails/"
DEFAULT_THUMB = "https://via.placeholder.com/150x220?text=PDF"

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

# 🔐 senha admin (⚠️ depois vamos mover pra ENV)
admin_password = generate_password_hash('1Q@Z0OkM*')


# 📚 LISTA COMPLETA DOS PDFs
def get_pdf_files():
    return [
        "12 Meses para enriquecer o plano da virada - Marcelo Silvestre.pdf",
        "12 Regras para a Vida - Jordan B. Peterson.pdf",
        "13 Coisas que as pessoas mentalmente fortes não fazem- Amy Morin.pdf",
        "20 Ferramentas para Hardware Hacking (Julio Della Flora).pdf",
        "27 Poderes de persuasão - Chris St. Hilaire & Lynette Padwa.pdf",
        "3 Passos Infalíveis para Abordar e Conversar com Todo Mundo no Mundo Todo - Gabriel Ponzi.pdf",
        "A experiência da mesa - Devi Titus.pdf",
        "All in Legado - Bem vindo ao operacional.pdf",
        "All in Legado - HTML para email marketing.pdf",
        "Ame pessoas, use coisas.pdf",
        "As cinco linguagens do amor 3 - Gary Chapman.pdf",
        "Café com Deus pai 2024.pdf",
        "Como aumentar sua produtividade.pdf",
        "Dominando o jogo da Persuasão.pdf",
        "Domínio da mente e da memória.pdf",
        "Fundamentos de marketing.pdf",
        "Gestão de Vendas.pdf",
        "Hardware Hacking Vol 2.pdf",
        "Imaginacao X Conhecimento.pdf",
        "Liderança é um contrato - Vince Molinaro.pdf",
        "Marketing 3.pdf",
        "Marketing 4.pdf",
        "Marketing 5.pdf",
        "Networking.pdf",
        "Os 7 Hábitos das Pessoas Altamente Eficazes - Stephen R Covey.pdf",
        "Os Sete hábitos das pessoas muito eficazes - Stephen R Covey.pdf",
        "Princípios de Marketing - Philip Kotler - Gary Armstrong.pdf",
        "Quebre as Regras e Reivente - Seth Godin.pdf",
        "Quem Mexeu no Meu Queijo - Spencer Johnson.pdf",
        "Quem Pensa Enriquece - Napoleon Hill.pdf",
        "Rápido e Devagar - Daniel Kahneman.pdf",
        "Scrum - A Arte de Fazer o Dobro - Jeff Sutherland.pdf",
        "Seja Foda! - Caio Carneiro.pdf",
        "Sem medo de Vencer - Roberto Shinyashiki.pdf",
        "Supercérebro - Deepak Chopra.pdf",
        "The Anarchist Cookbook - William Powell.pdf",
        "Trabalhe 4 Horas por Semana - Timothy Ferriss.pdf",
        "Trabalho Focado - Cal Newport.pdf",
        "Tudo é Óbvio - Duncan J. Watts.pdf",
        "Use sua Mente - Tony Buzan.pdf",
        "Vai Lá e Faz - Tiago Mattos.pdf",
        "Vencedores não criam desculpas.pdf"
    ]


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

    pdfs = [
        {
            "name": pdf,
            "url": get_pdf_url(pdf),
            "thumbnail": get_thumbnail_url(pdf)
        }
        for pdf in pdf_files
    ]

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
def delete_file(filename):
    if not session.get('logged_in'):
        flash('Você precisa fazer login para excluir arquivos.', 'error')
        return redirect(url_for('login'))

    flash(f'O arquivo {filename} precisa ser removido diretamente no servidor aphilly.', 'warning')
    return redirect(url_for('index'))


# 🚀 RUN
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
