"""
HSK PDF Generator - Streamlit Web App (FIXED - Canvas Drawing)
Disegna griglie e caratteri direttamente con canvas per migliore resa
"""

import streamlit as st
import requests
from typing import List, Dict
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
from datetime import datetime

st.set_page_config(
    page_title="HSK PDF Generator",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("🇨🇳 HSK Character Writing Practice Generator")
st.write("Genera PDF personalizzati per pratica di scrittura HSK 2 e 3")

# Sidebar per opzioni
with st.sidebar:
    st.header("⚙️ Opzioni")
    hsk_level = st.radio("Quale livello?", ["HSK 2", "HSK 3", "Entrambi"])
    chars_per_page = st.slider("Caratteri per pagina", 4, 12, 9)
    grid_cols = st.slider("Colonne nella griglia", 2, 4, 3)

class HSKCharacterFetcher:
    """Fetch HSK character data with multiple fallbacks"""
    
    @staticmethod
    def get_embedded_hsk2():
        """Embedded HSK 2 characters (top 150 most common for demo)"""
        return [
            {'char': '我', 'pinyin': 'wǒ', 'meaning': 'I, me', 'strokes': 7},
            {'char': '的', 'pinyin': 'de', 'meaning': 'possessive particle', 'strokes': 8},
            {'char': '不', 'pinyin': 'bù', 'meaning': 'not, no', 'strokes': 4},
            {'char': '你', 'pinyin': 'nǐ', 'meaning': 'you', 'strokes': 6},
            {'char': '他', 'pinyin': 'tā', 'meaning': 'he, him', 'strokes': 5},
            {'char': '是', 'pinyin': 'shì', 'meaning': 'be, is', 'strokes': 9},
            {'char': '有', 'pinyin': 'yǒu', 'meaning': 'have, has', 'strokes': 6},
            {'char': '一', 'pinyin': 'yī', 'meaning': 'one', 'strokes': 1},
            {'char': '在', 'pinyin': 'zài', 'meaning': 'at, in, exist', 'strokes': 6},
            {'char': '人', 'pinyin': 'rén', 'meaning': 'person, people', 'strokes': 2},
            {'char': '这', 'pinyin': 'zhè', 'meaning': 'this', 'strokes': 7},
            {'char': '中', 'pinyin': 'zhōng', 'meaning': 'middle, China', 'strokes': 4},
            {'char': '大', 'pinyin': 'dà', 'meaning': 'big, large', 'strokes': 3},
            {'char': '为', 'pinyin': 'wéi', 'meaning': 'for, be', 'strokes': 4},
            {'char': '上', 'pinyin': 'shàng', 'meaning': 'up, above, on', 'strokes': 3},
            {'char': '个', 'pinyin': 'gè', 'meaning': 'measure word', 'strokes': 3},
            {'char': '国', 'pinyin': 'guó', 'meaning': 'country, nation', 'strokes': 8},
            {'char': '到', 'pinyin': 'dào', 'meaning': 'arrive, reach', 'strokes': 8},
            {'char': '说', 'pinyin': 'shuō', 'meaning': 'say, speak', 'strokes': 9},
            {'char': '和', 'pinyin': 'hé', 'meaning': 'and, with', 'strokes': 8},
            {'char': '了', 'pinyin': 'le', 'meaning': 'particle', 'strokes': 2},
            {'char': '对', 'pinyin': 'duì', 'meaning': 'correct, to', 'strokes': 5},
            {'char': '生', 'pinyin': 'shēng', 'meaning': 'birth, life', 'strokes': 5},
            {'char': '能', 'pinyin': 'néng', 'meaning': 'can, able', 'strokes': 10},
            {'char': '去', 'pinyin': 'qù', 'meaning': 'go', 'strokes': 5},
            {'char': '年', 'pinyin': 'nián', 'meaning': 'year', 'strokes': 4},
            {'char': '来', 'pinyin': 'lái', 'meaning': 'come', 'strokes': 7},
            {'char': '也', 'pinyin': 'yě', 'meaning': 'also, too', 'strokes': 3},
            {'char': '很', 'pinyin': 'hěn', 'meaning': 'very', 'strokes': 9},
            {'char': '好', 'pinyin': 'hǎo', 'meaning': 'good', 'strokes': 6},
            {'char': '会', 'pinyin': 'huì', 'meaning': 'can, will', 'strokes': 6},
            {'char': '多', 'pinyin': 'duō', 'meaning': 'many, more', 'strokes': 6},
            {'char': '出', 'pinyin': 'chū', 'meaning': 'go out, exit', 'strokes': 5},
            {'char': '事', 'pinyin': 'shì', 'meaning': 'matter, affair', 'strokes': 8},
            {'char': '时', 'pinyin': 'shí', 'meaning': 'time', 'strokes': 10},
            {'char': '因', 'pinyin': 'yīn', 'meaning': 'because', 'strokes': 6},
            {'char': '成', 'pinyin': 'chéng', 'meaning': 'become', 'strokes': 6},
            {'char': '高', 'pinyin': 'gāo', 'meaning': 'high, tall', 'strokes': 10},
            {'char': '用', 'pinyin': 'yòng', 'meaning': 'use', 'strokes': 5},
            {'char': '方', 'pinyin': 'fāng', 'meaning': 'way, direction', 'strokes': 4},
            {'char': '就', 'pinyin': 'jiù', 'meaning': 'then, only', 'strokes': 12},
            {'char': '间', 'pinyin': 'jiān', 'meaning': 'space, between', 'strokes': 7},
            {'char': '家', 'pinyin': 'jiā', 'meaning': 'home, family', 'strokes': 10},
            {'char': '会', 'pinyin': 'huì', 'meaning': 'can, will, meet', 'strokes': 6},
            {'char': '子', 'pinyin': 'zǐ', 'meaning': 'child, son', 'strokes': 3},
            {'char': '天', 'pinyin': 'tiān', 'meaning': 'day, sky', 'strokes': 4},
            {'char': '当', 'pinyin': 'dāng', 'meaning': 'when, as', 'strokes': 6},
            {'char': '开', 'pinyin': 'kāi', 'meaning': 'open', 'strokes': 4},
            {'char': '名', 'pinyin': 'míng', 'meaning': 'name, famous', 'strokes': 6},
            {'char': '把', 'pinyin': 'bǎ', 'meaning': 'grasp, hold', 'strokes': 7},
            {'char': '想', 'pinyin': 'xiǎng', 'meaning': 'think, want', 'strokes': 13},
            {'char': '见', 'pinyin': 'jiàn', 'meaning': 'see, meet', 'strokes': 4},
            {'char': '可', 'pinyin': 'kě', 'meaning': 'can, may', 'strokes': 5},
            {'char': '她', 'pinyin': 'tā', 'meaning': 'she, her', 'strokes': 6},
            {'char': '让', 'pinyin': 'ràng', 'meaning': 'let, allow', 'strokes': 5},
            {'char': '通', 'pinyin': 'tōng', 'meaning': 'pass, connect', 'strokes': 10},
            {'char': '过', 'pinyin': 'guò', 'meaning': 'pass, excessive', 'strokes': 6},
            {'char': '面', 'pinyin': 'miàn', 'meaning': 'face, side', 'strokes': 9},
            {'char': '后', 'pinyin': 'hòu', 'meaning': 'after, behind', 'strokes': 6},
            {'char': '里', 'pinyin': 'lǐ', 'meaning': 'inside, village', 'strokes': 7},
            {'char': '最', 'pinyin': 'zuì', 'meaning': 'most', 'strokes': 12},
            {'char': '工', 'pinyin': 'gōng', 'meaning': 'work', 'strokes': 3},
            {'char': '下', 'pinyin': 'xià', 'meaning': 'down, below', 'strokes': 3},
            {'char': '老', 'pinyin': 'lǎo', 'meaning': 'old, venerable', 'strokes': 6},
            {'char': '还', 'pinyin': 'háishi', 'meaning': 'still, yet', 'strokes': 7},
            {'char': '才', 'pinyin': 'cái', 'meaning': 'talent, only', 'strokes': 3},
            {'char': '面', 'pinyin': 'miàn', 'meaning': 'face, surface', 'strokes': 9},
            {'char': '小', 'pinyin': 'xiǎo', 'meaning': 'small', 'strokes': 3},
            {'char': '日', 'pinyin': 'rì', 'meaning': 'day, sun', 'strokes': 4},
            {'char': '同', 'pinyin': 'tóng', 'meaning': 'same, with', 'strokes': 6},
            {'char': '现', 'pinyin': 'xiàn', 'meaning': 'present, appear', 'strokes': 11},
            {'char': '长', 'pinyin': 'zhǎng', 'meaning': 'grow, length', 'strokes': 4},
            {'char': '动', 'pinyin': 'dòng', 'meaning': 'move, motion', 'strokes': 6},
            {'char': '点', 'pinyin': 'diǎn', 'meaning': 'dot, o\'clock', 'strokes': 9},
            {'char': '分', 'pinyin': 'fēn', 'meaning': 'minute, divide', 'strokes': 4},
            {'char': '部', 'pinyin': 'bù', 'meaning': 'part, section', 'strokes': 10},
            {'char': '样', 'pinyin': 'yàng', 'meaning': 'manner, like', 'strokes': 10},
            {'char': '情', 'pinyin': 'qíng', 'meaning': 'feeling, emotion', 'strokes': 11},
            {'char': '意', 'pinyin': 'yì', 'meaning': 'meaning, idea', 'strokes': 13},
            {'char': '学', 'pinyin': 'xué', 'meaning': 'study, learn', 'strokes': 8},
            {'char': '重', 'pinyin': 'zhòng', 'meaning': 'heavy, important', 'strokes': 9},
            {'char': '知', 'pinyin': 'zhī', 'meaning': 'know', 'strokes': 8},
            {'char': '等', 'pinyin': 'děng', 'meaning': 'wait, equal', 'strokes': 12},
            {'char': '制', 'pinyin': 'zhì', 'meaning': 'system, make', 'strokes': 8},
        ]
    
    @staticmethod
    def get_embedded_hsk3():
        """Embedded HSK 3 characters (sample of top 150)"""
        hsk2 = HSKCharacterFetcher.get_embedded_hsk2()
        # HSK 3 includes HSK 2 + new characters
        hsk3_new = [
            {'char': '阿', 'pinyin': 'ā', 'meaning': 'prefix, aunt', 'strokes': 7},
            {'char': '挨', 'pinyin': 'āi', 'meaning': 'suffer, endure', 'strokes': 10},
            {'char': '哀', 'pinyin': 'āi', 'meaning': 'sorrow, grieve', 'strokes': 9},
            {'char': '安', 'pinyin': 'ān', 'meaning': 'safe, peace', 'strokes': 6},
            {'char': '案', 'pinyin': 'àn', 'meaning': 'case, table', 'strokes': 10},
            {'char': '暗', 'pinyin': 'àn', 'meaning': 'dark, hidden', 'strokes': 13},
            {'char': '按', 'pinyin': 'àn', 'meaning': 'press, according', 'strokes': 9},
            {'char': '肮', 'pinyin': 'āng', 'meaning': 'dirty, filthy', 'strokes': 8},
            {'char': '凹', 'pinyin': 'āo', 'meaning': 'concave', 'strokes': 5},
            {'char': '凸', 'pinyin': 'tū', 'meaning': 'convex', 'strokes': 5},
            {'char': '敖', 'pinyin': 'áo', 'meaning': 'roam, ramble', 'strokes': 10},
            {'char': '獒', 'pinyin': 'áo', 'meaning': 'mastiff dog', 'strokes': 16},
            {'char': '爸', 'pinyin': 'bà', 'meaning': 'father, dad', 'strokes': 8},
            {'char': '拔', 'pinyin': 'báy', 'meaning': 'pull out', 'strokes': 8},
            {'char': '坝', 'pinyin': 'bà', 'meaning': 'dam, dike', 'strokes': 8},
            {'char': '跋', 'pinyin': 'báy', 'meaning': 'traverse', 'strokes': 12},
            {'char': '巴', 'pinyin': 'bā', 'meaning': 'long for, cling', 'strokes': 4},
            {'char': '百', 'pinyin': 'bǎi', 'meaning': 'hundred', 'strokes': 6},
            {'char': '摆', 'pinyin': 'bǎi', 'meaning': 'swing, sway', 'strokes': 13},
            {'char': '败', 'pinyin': 'bài', 'meaning': 'defeat, fail', 'strokes': 11},
            {'char': '拜', 'pinyin': 'bài', 'meaning': 'pay respect', 'strokes': 9},
            {'char': '班', 'pinyin': 'bān', 'meaning': 'class, group', 'strokes': 10},
            {'char': '斑', 'pinyin': 'bān', 'meaning': 'spotted, variegated', 'strokes': 12},
            {'char': '颁', 'pinyin': 'bān', 'meaning': 'promulgate', 'strokes': 12},
            {'char': '板', 'pinyin': 'bǎn', 'meaning': 'board, plank', 'strokes': 8},
            {'char': '版', 'pinyin': 'bǎn', 'meaning': 'version, edition', 'strokes': 8},
            {'char': '办', 'pinyin': 'bàn', 'meaning': 'handle, manage', 'strokes': 4},
            {'char': '半', 'pinyin': 'bàn', 'meaning': 'half', 'strokes': 5},
            {'char': '伴', 'pinyin': 'bàn', 'meaning': 'companion', 'strokes': 7},
            {'char': '瓣', 'pinyin': 'bàn', 'meaning': 'petal, valve', 'strokes': 19},
        ]
        return hsk2 + hsk3_new
    
    @staticmethod
    def fetch_from_github():
        """Main fetch method with fallbacks"""
        try:
            # Try alternative source
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
                    'meaning': item.get('meanings', [{}])[0].get('meaning', ''),
                    'strokes': item.get('strokes', 0),
                } for item in hsk2_data if item.get('simplified')][:150]
            
            if response3.status_code == 200:
                hsk3_data = response3.json()
                hsk3_chars = [{
                    'char': item.get('simplified', ''),
                    'pinyin': item.get('pinyin', ''),
                    'meaning': item.get('meanings', [{}])[0].get('meaning', ''),
                    'strokes': item.get('strokes', 0),
                } for item in hsk3_data if item.get('simplified')][:150]
            
            if hsk2_chars and hsk3_chars:
                return hsk2_chars, hsk3_chars
        except:
            pass
        
        # Fall back to embedded data
        return (
            HSKCharacterFetcher.get_embedded_hsk2(),
            HSKCharacterFetcher.get_embedded_hsk3()
        )


class HSKPDFGenerator:
    """Generate PDF with proper grids and handwriting practice spaces"""
    
    def __init__(self, title: str, level: int):
        self.title = title
        self.level = level
        self.page_width, self.page_height = A4
        self.margin = 15*mm
        self.cell_size = None  # Will be calculated
        self.grid_cols = None
    
    def generate_pdf_bytes(self, characters: List[Dict], 
                          chars_per_page: int = 9,
                          grid_cols: int = 3) -> bytes:
        """Generate PDF with proper grid layout"""
        self.grid_cols = grid_cols
        grid_rows = chars_per_page // grid_cols
        
        # Calculate cell size
        available_width = self.page_width - (2 * self.margin)
        available_height = self.page_height - (4 * self.margin) - 30*mm  # space for header
        
        cell_width = available_width / grid_cols
        cell_height = available_height / grid_rows
        self.cell_size = min(cell_width, cell_height)
        
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        
        # Cover page
        self._draw_cover(c)
        c.showPage()
        
        # Character pages
        for page_idx in range(0, len(characters), chars_per_page):
            page_chars = characters[page_idx:page_idx + chars_per_page]
            self._draw_character_page(c, page_chars, page_idx, len(characters), grid_cols, grid_rows)
            c.showPage()
        
        c.save()
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
    
    def _draw_cover(self, c):
        """Draw cover page"""
        c.setFont("Helvetica-Bold", 48)
        c.drawCentredString(self.page_width / 2, self.page_height / 2 + 80, 
                           f"HSK {self.level}")
        
        c.setFont("Helvetica", 24)
        c.drawCentredString(self.page_width / 2, self.page_height / 2 + 40,
                           "汉语水平考试")
        
        c.setFont("Helvetica", 18)
        c.drawCentredString(self.page_width / 2, self.page_height / 2 - 20,
                           "Chinese Character Writing Practice")
        
        c.setFont("Helvetica", 12)
        c.drawCentredString(self.page_width / 2, self.page_height / 2 - 80,
                           f"Total Characters: {self.title}")
    
    def _draw_character_page(self, c, characters: List[Dict], 
                            page_idx: int, total_chars: int,
                            grid_cols: int, grid_rows: int):
        """Draw page with character grid"""
        
        # Page header
        c.setFont("Helvetica-Bold", 14)
        c.drawString(self.margin, self.page_height - self.margin - 10,
                    f"Characters {page_idx + 1} - {min(page_idx + len(characters), total_chars)}")
        
        # Draw grid
        y_position = self.page_height - (2.5 * self.margin)
        
        for row_idx in range(grid_rows):
            x_position = self.margin
            
            for col_idx in range(grid_cols):
                char_idx = row_idx * grid_cols + col_idx
                
                if char_idx < len(characters):
                    char_info = characters[char_idx]
                    self._draw_character_cell(c, x_position, y_position, 
                                             char_info, self.cell_size)
                
                x_position += self.cell_size
            
            y_position -= self.cell_size
    
    def _draw_character_cell(self, c, x: float, y: float, 
                            char_info: Dict, cell_size: float):
        """Draw a single character cell with grid lines"""
        
        padding = 5*mm
        content_width = cell_size - (2 * padding)
        content_height = cell_size - (2 * padding)
        
        # Draw border
        c.setLineWidth(0.5)
        c.setStrokeColorRGB(0.7, 0.7, 0.7)
        c.rect(x, y - cell_size, cell_size, cell_size, fill=False)
        
        # Divide cell: top half for character, bottom half for practice grid
        top_height = cell_size * 0.5
        bottom_height = cell_size * 0.5
        
        # ===== TOP: Character display =====
        # Draw character in large font
        char = char_info['char']
        c.setFont("Helvetica-Bold", 72)
        c.setFillColorRGB(0, 0, 0)
        
        # Center character in top half
        char_x = x + cell_size / 2
        char_y = y - padding - 15*mm
        c.drawCentredString(char_x, char_y, char)
        
        # Draw pinyin and meaning below character (smaller)
        pinyin = char_info['pinyin']
        meaning = char_info['meaning'][:15]
        strokes = char_info.get('strokes', 0)
        
        c.setFont("Helvetica", 8)
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.drawCentredString(char_x, char_y - 12, f"{pinyin}")
        c.drawCentredString(char_x, char_y - 18, f"{meaning}")
        c.drawCentredString(char_x, char_y - 24, f"Strokes: {strokes}")
        
        # ===== BOTTOM: Practice grid (4x4 small squares) =====
        grid_start_y = y - top_height
        grid_square_size = (content_width - 2*mm) / 4
        
        c.setLineWidth(0.25)
        c.setStrokeColorRGB(0.85, 0.85, 0.85)
        
        # Draw 4x4 grid
        for row in range(4):
            for col in range(4):
                grid_x = x + padding + (col * grid_square_size)
                grid_y = grid_start_y - padding - (row * grid_square_size)
                
                c.rect(grid_x, grid_y - grid_square_size, 
                      grid_square_size, grid_square_size, fill=False)
        
        # Draw diagonal lines in grid squares for handwriting guide
        c.setLineWidth(0.15)
        c.setStrokeColorRGB(0.92, 0.92, 0.92)
        
        for row in range(4):
            for col in range(4):
                grid_x = x + padding + (col * grid_square_size)
                grid_y = grid_start_y - padding - (row * grid_square_size)
                
                # Diagonal lines for practice
                c.line(grid_x, grid_y, 
                      grid_x + grid_square_size, grid_y - grid_square_size)
                c.line(grid_x + grid_square_size, grid_y,
                      grid_x, grid_y - grid_square_size)


# Main app
@st.cache_data
def load_hsk_data():
    """Cache the data fetching"""
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

    # Generate buttons
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
    st.info("💡 **Suggerimento:** Aumenta i caratteri per pagina per fogli più densi, riduci per meno sforzo visivo.")
    
else:
    st.error("❌ Impossibile scaricare i dati HSK. Usando dati incorporati...")
    st.info("I dati incorporati contengono i caratteri HSK più comuni per la pratica.")
