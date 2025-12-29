"""
HSK PDF Generator - Streamlit Web App (FIXED v3 - Simple Direct Drawing)
Approccio semplificato e robusto con posizioni assolute
"""

import streamlit as st
import requests
from typing import List, Dict
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.pdfgen import canvas
import io

st.set_page_config(
    page_title="HSK PDF Generator",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("🇨🇳 HSK Character Writing Practice Generator")
st.write("Genera PDF personalizzati per pratica di scrittura HSK 2 e 3")

with st.sidebar:
    st.header("⚙️ Opzioni")
    hsk_level = st.radio("Quale livello?", ["HSK 2", "HSK 3", "Entrambi"])
    chars_per_page = st.slider("Caratteri per pagina", 4, 12, 9)
    grid_cols = st.slider("Colonne nella griglia", 2, 4, 3)

class HSKCharacterFetcher:
    """Fetch HSK character data"""
    
    @staticmethod
    def get_embedded_hsk2():
        """Embedded HSK 2 characters"""
        return [
            {'char': '我', 'pinyin': 'wǒ', 'meaning': 'I, me', 'strokes': 7},
            {'char': '的', 'pinyin': 'de', 'meaning': 'possessive', 'strokes': 8},
            {'char': '不', 'pinyin': 'bù', 'meaning': 'not, no', 'strokes': 4},
            {'char': '你', 'pinyin': 'nǐ', 'meaning': 'you', 'strokes': 6},
            {'char': '他', 'pinyin': 'tā', 'meaning': 'he, him', 'strokes': 5},
            {'char': '是', 'pinyin': 'shì', 'meaning': 'be, is', 'strokes': 9},
            {'char': '有', 'pinyin': 'yǒu', 'meaning': 'have', 'strokes': 6},
            {'char': '一', 'pinyin': 'yī', 'meaning': 'one', 'strokes': 1},
            {'char': '在', 'pinyin': 'zài', 'meaning': 'at, in', 'strokes': 6},
            {'char': '人', 'pinyin': 'rén', 'meaning': 'person', 'strokes': 2},
            {'char': '这', 'pinyin': 'zhè', 'meaning': 'this', 'strokes': 7},
            {'char': '中', 'pinyin': 'zhōng', 'meaning': 'middle', 'strokes': 4},
            {'char': '大', 'pinyin': 'dà', 'meaning': 'big, large', 'strokes': 3},
            {'char': '为', 'pinyin': 'wéi', 'meaning': 'for', 'strokes': 4},
            {'char': '上', 'pinyin': 'shàng', 'meaning': 'up, above', 'strokes': 3},
            {'char': '个', 'pinyin': 'gè', 'meaning': 'measure word', 'strokes': 3},
            {'char': '国', 'pinyin': 'guó', 'meaning': 'country', 'strokes': 8},
            {'char': '到', 'pinyin': 'dào', 'meaning': 'arrive', 'strokes': 8},
            {'char': '说', 'pinyin': 'shuō', 'meaning': 'say', 'strokes': 9},
            {'char': '和', 'pinyin': 'hé', 'meaning': 'and, with', 'strokes': 8},
        ]
    
    @staticmethod
    def get_embedded_hsk3():
        """Embedded HSK 3 characters"""
        hsk2 = HSKCharacterFetcher.get_embedded_hsk2()
        hsk3_new = [
            {'char': '爸', 'pinyin': 'bà', 'meaning': 'father', 'strokes': 8},
            {'char': '拔', 'pinyin': 'báy', 'meaning': 'pull out', 'strokes': 8},
            {'char': '坝', 'pinyin': 'bà', 'meaning': 'dam', 'strokes': 8},
            {'char': '百', 'pinyin': 'bǎi', 'meaning': 'hundred', 'strokes': 6},
            {'char': '班', 'pinyin': 'bān', 'meaning': 'class', 'strokes': 10},
        ]
        return hsk2 + hsk3_new
    
    @staticmethod
    def fetch_from_github():
        try:
            hsk2_url = "https://raw.githubusercontent.com/drkameleon/complete-hsk-vocabulary/main/wordlists/inclusive/new/2.json"
            hsk3_url = "https://raw.githubusercontent.com/drkameleon/complete-hsk-vocabulary/main/wordlists/inclusive/new/3.json"
            
            response2 = requests.get(hsk2_url, timeout=10)
            response3 = requests.get(hsk3_url, timeout=10)
            
            hsk2_chars = []
            hsk3_chars = []
            
            if response2.status_code == 200:
                hsk2_data = response2.json()
                hsk2_chars = [{
                    'char': item.get('simplified', ''),
                    'pinyin': item.get('pinyin', ''),
                    'meaning': item.get('meanings', [{}])[0].get('meaning', '')[:15],
                    'strokes': item.get('strokes', 0),
                } for item in hsk2_data if item.get('simplified')][:80]
            
            if response3.status_code == 200:
                hsk3_data = response3.json()
                hsk3_chars = [{
                    'char': item.get('simplified', ''),
                    'pinyin': item.get('pinyin', ''),
                    'meaning': item.get('meanings', [{}])[0].get('meaning', '')[:15],
                    'strokes': item.get('strokes', 0),
                } for item in hsk3_data if item.get('simplified')][:80]
            
            if hsk2_chars and hsk3_chars:
                return hsk2_chars, hsk3_chars
        except:
            pass
        
        return (
            HSKCharacterFetcher.get_embedded_hsk2(),
            HSKCharacterFetcher.get_embedded_hsk3()
        )


class HSKPDFGenerator:
    """Simple, direct PDF generation with canvas"""
    
    def __init__(self, title: str, level: int):
        self.title = title
        self.level = level
    
    def generate_pdf_bytes(self, characters: List[Dict], 
                          chars_per_page: int = 9,
                          grid_cols: int = 3) -> bytes:
        """Generate PDF"""
        grid_rows = max(1, chars_per_page // grid_cols)
        
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        
        # Page dimensions (in points, default for canvas)
        page_width, page_height = 595, 842  # A4 in points
        
        # Draw cover
        c.setFont("Helvetica-Bold", 48)
        c.drawCentredString(page_width / 2, page_height - 200, f"HSK {self.level}")
        
        c.setFont("Helvetica", 24)
        c.drawCentredString(page_width / 2, page_height - 280, "汉语水平考试")
        
        c.setFont("Helvetica", 16)
        c.drawCentredString(page_width / 2, page_height - 350, "Chinese Character Writing Practice")
        
        c.showPage()
        
        # Character pages
        for page_idx in range(0, len(characters), chars_per_page):
            page_chars = characters[page_idx:page_idx + chars_per_page]
            
            # Page header
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, page_height - 40, 
                        f"Characters {page_idx + 1} - {min(page_idx + len(page_chars), len(characters))}")
            
            # Calculate cell dimensions
            margin = 30
            available_width = page_width - (2 * margin)
            available_height = page_height - 100
            
            cell_width = available_width / grid_cols
            cell_height = available_height / grid_rows
            
            # Draw grid cells
            char_count = 0
            for row in range(grid_rows):
                for col in range(grid_cols):
                    if char_count < len(page_chars):
                        x = margin + (col * cell_width)
                        y = page_height - 80 - (row * cell_height)
                        
                        self._draw_cell(c, x, y, cell_width, cell_height, 
                                       page_chars[char_count])
                        char_count += 1
            
            c.showPage()
        
        c.save()
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
    
    def _draw_cell(self, c, x: float, y: float, width: float, height: float, 
                   char_info: Dict):
        """Draw a single cell"""
        
        # Border
        c.setLineWidth(1)
        c.setStrokeColorRGB(0.5, 0.5, 0.5)
        c.rect(x, y - height, width, height)
        
        # Split: top for character, bottom for grid
        mid_y = y - (height / 2)
        
        # TOP SECTION: Character
        char = char_info['char']
        pinyin = char_info['pinyin']
        meaning = char_info['meaning']
        strokes = char_info.get('strokes', 0)
        
        # Draw character large
        c.setFont("SimSun", 60)  # Try native Chinese font
        c.setFillColorRGB(0, 0, 0)
        
        try:
            c.drawCentredString(x + width/2, y - height/4 - 10, char)
        except:
            # Fallback if font not available
            c.setFont("Helvetica-Bold", 48)
            c.drawCentredString(x + width/2, y - height/4 - 10, char)
        
        # Small info
        c.setFont("Helvetica", 7)
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.drawCentredString(x + width/2, y - height/4 - 25, pinyin)
        c.drawCentredString(x + width/2, y - height/4 - 32, meaning[:12])
        c.drawCentredString(x + width/2, y - height/4 - 38, f"S:{strokes}")
        
        # BOTTOM SECTION: Practice grid
        # Draw 4x4 grid for handwriting
        grid_margin = 5
        grid_left = x + grid_margin
        grid_right = x + width - grid_margin
        grid_top = mid_y - grid_margin
        grid_bottom = y - height + grid_margin
        
        grid_width = grid_right - grid_left
        grid_height = grid_top - grid_bottom
        
        sq_width = grid_width / 4
        sq_height = grid_height / 4
        
        c.setLineWidth(0.5)
        c.setStrokeColorRGB(0.7, 0.7, 0.7)
        
        # Draw grid
        for row in range(5):
            y_pos = grid_top - (row * sq_height)
            c.line(grid_left, y_pos, grid_right, y_pos)
        
        for col in range(5):
            x_pos = grid_left + (col * sq_width)
            c.line(x_pos, grid_top, x_pos, grid_bottom)
        
        # Draw diagonal guides
        c.setLineWidth(0.2)
        c.setStrokeColorRGB(0.85, 0.85, 0.85)
        
        for row in range(4):
            for col in range(4):
                x_pos = grid_left + (col * sq_width)
                y_pos = grid_top - (row * sq_height)
                
                # Diagonals for handwriting guide
                c.line(x_pos, y_pos, x_pos + sq_width, y_pos - sq_height)
                c.line(x_pos + sq_width, y_pos, x_pos, y_pos - sq_height)


@st.cache_data
def load_hsk_data():
    fetcher = HSKCharacterFetcher()
    return fetcher.fetch_from_github()

st.header("📥 Caricamento dati...")
with st.spinner("Scaricamento dati HSK..."):
    hsk2_chars, hsk3_chars = load_hsk_data()

if hsk2_chars and hsk3_chars:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("HSK 2", f"{len(hsk2_chars)} caratteri")
    with col2:
        st.metric("HSK 3", f"{len(hsk3_chars)} caratteri")

    st.divider()

    if st.button("📄 Genera PDF", use_container_width=True, type="primary"):
        with st.spinner("Generazione in corso..."):
            
            if hsk_level in ["HSK 2", "Entrambi"]:
                st.write("🔄 Generazione HSK 2...")
                gen2 = HSKPDFGenerator("HSK 2 Writing Practice", 2)
                pdf2 = gen2.generate_pdf_bytes(hsk2_chars, chars_per_page, grid_cols)
                
                st.download_button(
                    label="⬇️ Scarica HSK 2 PDF",
                    data=pdf2,
                    file_name="HSK_2_Practice.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            if hsk_level in ["HSK 3", "Entrambi"]:
                st.write("🔄 Generazione HSK 3...")
                gen3 = HSKPDFGenerator("HSK 3 Writing Practice", 3)
                pdf3 = gen3.generate_pdf_bytes(hsk3_chars, chars_per_page, grid_cols)
                
                st.download_button(
                    label="⬇️ Scarica HSK 3 PDF",
                    data=pdf3,
                    file_name="HSK_3_Practice.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            st.success("✅ PDF generati con successo!")

    st.divider()
    st.info("💡 **Suggerimento:** Prova diverse combinazioni di caratteri per pagina e colonne!")

