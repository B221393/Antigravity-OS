import streamlit as st
from pypdf import PdfWriter, PdfReader
from io import BytesIO

st.set_page_config(page_title="PDF Splicer", page_icon="📄")
st.title("📄 PDF Splicer")

uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

if uploaded_files:
    st.write(f"Loaded {len(uploaded_files)} files.")
    
    # Sort functionality could be added here, currently strictly upload order
    
    if st.button("Merge PDFs"):
        merger = PdfWriter()
        for pdf in uploaded_files:
            merger.append(pdf)
        
        output = BytesIO()
        merger.write(output)
        out_bytes = output.getvalue()
        
        st.success("Merged successfully!")
        st.download_button(label="Download Merged PDF", data=out_bytes, file_name="merged.pdf", mime="application/pdf")

st.divider()
st.subheader("Split PDF")
split_file = st.file_uploader("Upload single PDF to split", type="pdf", key="split")
if split_file:
    reader = PdfReader(split_file)
    num_pages = len(reader.pages)
    st.write(f"Total Pages: {num_pages}")
    
    page_range = st.text_input("Page Range (e.g. 1-3, 5)", "1")
    
    if st.button("Extract Pages"):
        try:
            writer = PdfWriter()
            # Simple parser for "1-3, 5" style
            parts = page_range.split(',')
            for part in parts:
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    for i in range(start-1, end):
                        if 0 <= i < num_pages: writer.add_page(reader.pages[i])
                else:
                    idx = int(part) - 1
                    if 0 <= idx < num_pages: writer.add_page(reader.pages[idx])
            
            out_s = BytesIO()
            writer.write(out_s)
            st.download_button("Download Extracted", out_s.getvalue(), "extracted.pdf", "application/pdf")
        except Exception as e:
            st.error(f"Error: {e}")
