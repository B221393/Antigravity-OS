import pypdfium2 as pdfium
import re
from pathlib import Path
from typing import Optional

class PDFParser:
    """PDFからテキストを抽出・整形するクラス"""

    def extract_text(self, pdf_path: Path) -> Optional[str]:
        """PDF全ページからテキストを抽出する"""
        if not pdf_path.exists():
            return None
        
        try:
            pdf = pdfium.PdfDocument(str(pdf_path))
            full_text = []
            for i in range(len(pdf)):
                page = pdf[i]
                textpage = page.get_textpage()
                text = textpage.get_text_range()
                full_text.append(text)
                
            return self._clean_text("\n".join(full_text))
        except Exception as e:
            print(f"Error parsing PDF {pdf_path}: {e}")
            return None

    def _clean_text(self, text: str) -> str:
        """テキストのノイズを除去する"""
        # ハイフネーションによる単語の分割を結合 (例: "ex- \nample" -> "example")
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        
        # 文中の不要な改行をスペースに置換 (段落間の空行は保持)
        # 1つの改行はスペースに、2つ以上の改行は段落区切りとして保持
        paragraphs = text.split('\r\n\r\n')
        cleaned_paragraphs = []
        for p in paragraphs:
            # 各段落内の単一の改行をスペースに
            p = p.replace('\r\n', ' ').replace('\n', ' ')
            # 連続するスペースを1つに
            p = re.sub(r'\s+', ' ', p).strip()
            cleaned_paragraphs.append(p)
            
        return "\n\n".join(cleaned_paragraphs)

if __name__ == "__main__":
    # 単体テスト
    import sys
    if len(sys.argv) > 1:
        parser = PDFParser()
        result = parser.extract_text(Path(sys.argv[1]))
        if result:
            print(result[:1000] + "...")
