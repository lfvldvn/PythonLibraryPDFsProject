from pdf2image import convert_from_path
import os

PDF_FOLDER = "PDFbooks"  # sua pasta local
THUMB_FOLDER = "thumbnails"

os.makedirs(THUMB_FOLDER, exist_ok=True)

def generate_thumbnail(pdf_path, output_path):
    try:
        pages = convert_from_path(pdf_path, first_page=1, last_page=1)
        if pages:
            page = pages[0]
            page.save(output_path, 'PNG')
            print(f"✅ Thumb criada: {output_path}")
    except Exception as e:
        print(f"❌ Erro em {pdf_path}: {e}")


def main():
    for file in os.listdir(PDF_FOLDER):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(PDF_FOLDER, file)

            name = os.path.splitext(file)[0]
            thumb_path = os.path.join(THUMB_FOLDER, f"{name}.png")

            if not os.path.exists(thumb_path):
                generate_thumbnail(pdf_path, thumb_path)
            else:
                print(f"⏭️ Já existe: {thumb_path}")


if __name__ == "__main__":
    main()