import PyPDF2
import os

def extract_text_from_pdf(pdf_path, output_dir):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                # Page might be empty or have no extractable text
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        base_name = os.path.basename(pdf_path)
        output_filename = os.path.splitext(base_name)[0] + ".txt"
        output_path = os.path.join(output_dir, output_filename)

        os.makedirs(output_dir, exist_ok=True) # Ensure output directory exists

        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(text)
        print(f"Text extracted from {pdf_path} to {output_path}")
        return True
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return False

def main():
    input_dir = 'companypdf'
    output_dir = 'extracted_texts'

    # Check if input_dir exists
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' not found.")
        return

    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print(f"No PDF files found in '{input_dir}' directory.")
        return

    print(f"Found {len(pdf_files)} PDF files in '{input_dir}'. Starting text extraction...")
    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_dir, pdf_file)
        extract_text_from_pdf(pdf_path, output_dir)
    print("Text extraction complete.")

if __name__ == "__main__":
    main()
