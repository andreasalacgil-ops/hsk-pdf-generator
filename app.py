"""
HSK PDF Generator - Streamlit Web App (Fixed)
Interfaccia web interattiva per generare i PDF
Con dati HSK embedded + fallback sources
"""

import streamlit as st
import requests
import json
from typing import List, Dict
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io

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
    chars_per_page = st.slider("Caratteri per pagina", 6, 20, 12)
    grid_cols = st.slider("Colonne nella griglia", 2, 4, 3)

class HSKCharacterFetcher:
    """Fetch HSK character data with multiple fallbacks"""
    
    @staticmethod
    def get_embedded_hsk2():
        """Embedded HSK 2 characters (official 300 most common)"""
        return [
            {'char': '爱', 'pinyin': 'ài', 'meaning': 'love, like', 'strokes': 10, 'level': 2},
            {'char': '八', 'pinyin': 'bā', 'meaning': 'eight', 'strokes': 2, 'level': 2},
            {'char': '白', 'pinyin': 'bái', 'meaning': 'white', 'strokes': 5, 'level': 2},
            {'char': '班', 'pinyin': 'bān', 'meaning': 'class', 'strokes': 10, 'level': 2},
            {'char': '半', 'pinyin': 'bàn', 'meaning': 'half', 'strokes': 5, 'level': 2},
            {'char': '办', 'pinyin': 'bàn', 'meaning': 'handle, manage', 'strokes': 4, 'level': 2},
            {'char': '帮', 'pinyin': 'bāng', 'meaning': 'help, gang', 'strokes': 9, 'level': 2},
            {'char': '包', 'pinyin': 'bāo', 'meaning': 'wrap, bag', 'strokes': 5, 'level': 2},
            {'char': '被', 'pinyin': 'bèi', 'meaning': 'by (passive), quilt', 'strokes': 10, 'level': 2},
            {'char': '北', 'pinyin': 'běi', 'meaning': 'north', 'strokes': 5, 'level': 2},
            {'char': '本', 'pinyin': 'běn', 'meaning': 'root, base, origin', 'strokes': 5, 'level': 2},
            {'char': '比', 'pinyin': 'bǐ', 'meaning': 'compare, than', 'strokes': 4, 'level': 2},
            {'char': '笔', 'pinyin': 'bǐ', 'meaning': 'pen, brush', 'strokes': 10, 'level': 2},
            {'char': '必', 'pinyin': 'bì', 'meaning': 'must, necessary', 'strokes': 5, 'level': 2},
            {'char': '边', 'pinyin': 'biān', 'meaning': 'side, edge, border', 'strokes': 5, 'level': 2},
            {'char': '别', 'pinyin': 'bié', 'meaning': 'other, do not', 'strokes': 7, 'level': 2},
            {'char': '病', 'pinyin': 'bìng', 'meaning': 'illness, disease', 'strokes': 10, 'level': 2},
            {'char': '不', 'pinyin': 'bù', 'meaning': 'not, no', 'strokes': 4, 'level': 1},
            {'char': '布', 'pinyin': 'bù', 'meaning': 'cloth, fabric', 'strokes': 5, 'level': 2},
            {'char': '部', 'pinyin': 'bù', 'meaning': 'part, section', 'strokes': 10, 'level': 2},
            {'char': '才', 'pinyin': 'cái', 'meaning': 'talent, only then', 'strokes': 3, 'level': 2},
            {'char': '餐', 'pinyin': 'cān', 'meaning': 'meal, food', 'strokes': 12, 'level': 2},
            {'char': '参', 'pinyin': 'cānshù', 'meaning': 'ginseng, participate', 'strokes': 8, 'level': 2},
            {'char': '蚕', 'pinyin': 'cán', 'meaning': 'silkworm', 'strokes': 10, 'level': 2},
            {'char': '层', 'pinyin': 'céng', 'meaning': 'layer, stratum', 'strokes': 9, 'level': 2},
            {'char': '差', 'pinyin': 'chā', 'meaning': 'differ, lack, poor', 'strokes': 10, 'level': 2},
            {'char': '长', 'pinyin': 'cháng', 'meaning': 'long, length', 'strokes': 4, 'level': 1},
            {'char': '常', 'pinyin': 'cháng', 'meaning': 'often, usually', 'strokes': 11, 'level': 2},
            {'char': '场', 'pinyin': 'chǎng', 'meaning': 'field, place', 'strokes': 6, 'level': 2},
            {'char': '唱', 'pinyin': 'chàng', 'meaning': 'sing, song', 'strokes': 10, 'level': 2},
            # ... Add more up to 300 for complete HSK 2
        ]
    
    @staticmethod
    def get_embedded_hsk3():
        """Embedded HSK 3 characters (official 600 - selected sample)"""
        return [
            {'char': '阿', 'pinyin': 'ā', 'meaning': 'prefix, aunt', 'strokes': 7, 'level': 3},
            {'char': '挨', 'pinyin': 'āi', 'meaning': 'suffer, endure', 'strokes': 10, 'level': 3},
            {'char': '哀', 'pinyin': 'āi', 'meaning': 'sorrow, grieve', 'strokes': 9, 'level': 3},
            {'char': '安', 'pinyin': 'ān', 'meaning': 'safe, peace', 'strokes': 6, 'level': 3},
            {'char': '案', 'pinyin': 'àn', 'meaning': 'case, table', 'strokes': 10, 'level': 3},
            {'char': '暗', 'pinyin': 'àn', 'meaning': 'dark, hidden', 'strokes': 13, 'level': 3},
            {'char': '按', 'pinyin': 'àn', 'meaning': 'press, according to', 'strokes': 9, 'level': 3},
            {'char': '肮', 'pinyin': 'āng', 'meaning': 'dirty, filthy', 'strokes': 8, 'level': 3},
            {'char': '凹', 'pinyin': 'āo', 'meaning': 'concave, sunken', 'strokes': 5, 'level': 3},
            {'char': '凸', 'pinyin': 'tū', 'meaning': 'convex, protruding', 'strokes': 5, 'level': 3},
            {'char': '敖', 'pinyin': 'áo', 'meaning': 'roam, ramble', 'strokes': 10, 'level': 3},
            {'char': '八', 'pinyin': 'bā', 'meaning': 'eight', 'strokes': 2, 'level': 3},
            {'char': '巴', 'pinyin': 'bā', 'meaning': 'long for, cling to', 'strokes': 4, 'level': 3},
            {'char': '拔', 'pinyin': 'báy', 'meaning': 'pull out, uproot', 'strokes': 8, 'level': 3},
            {'char': '把', 'pinyin': 'bǎ', 'meaning': 'grasp, hold', 'strokes': 7, 'level': 3},
            {'char': '坝', 'pinyin': 'bà', 'meaning': 'dam, dike', 'strokes': 8, 'level': 3},
            {'char': '跋', 'pinyin': 'báy', 'meaning': 'traverse, move', 'strokes': 12, 'level': 3},
            {'char': '白', 'pinyin': 'bái', 'meaning': 'white', 'strokes': 5, 'level': 3},
            {'char': '百', 'pinyin': 'bǎi', 'meaning': 'hundred', 'strokes': 6, 'level': 3},
            {'char': '摆', 'pinyin': 'bǎi', 'meaning': 'swing, sway', 'strokes': 13, 'level': 3},
            # ... Add more up to 600 for complete HSK 3
        ]
    
    @staticmethod
    def fetch_from_alternative_sources():
        """Try to fetch from alternative GitHub sources"""
        try:
            # Source 1: drkameleon/complete-hsk-vocabulary
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
                    'level': 2
                } for item in hsk2_data if item.get('simplified')][:300]
            
            if response3.status_code == 200:
                hsk3_data = response3.json()
                hsk3_chars = [{
                    'char': item.get('simplified', ''),
                    'pinyin': item.get('pinyin', ''),
                    'meaning': item.get('meanings', [{}])[0].get('meaning', ''),
                    'strokes': item.get('strokes', 0),
                    'level': 3
                } for item in hsk3_data if item.get('simplified')][:300]
            
            return hsk2_chars, hsk3_chars
            
        except Exception as e:
            return [], []
    
    @staticmethod
    def fetch_from_github():
        """Main fetch method with fallbacks"""
        # Try alternative source first
        hsk2_chars, hsk3_chars = HSKCharacterFetcher.fetch_from_alternative_sources()
        
        if hsk2_chars and hsk3_chars:
            return hsk2_chars, hsk3_chars
        
        # Fall back to embedded data
        return (
            HSKCharacterFetcher.get_embedded_hsk2(),
            HSKCharacterFetcher.get_embedded_hsk3()
        )


class HSKWorksheetGenerator:
    def __init__(self, title: str, level: int):
        self.title = title
        self.level = level
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='TitleStyle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=1
        ))
    
    def _create_character_cell(self, char_info: Dict) -> str:
        char = char_info['char']
        pinyin = char_info['pinyin']
        meaning = char_info['meaning'][:20] if char_info['meaning'] else 'N/A'
        strokes = char_info.get('strokes', 0)
        
        cell_text = f"""
<font size="32" color="#000000"><b>{char}</b></font><br/>
<font size="9" color="#666666">{pinyin}</font><br/>
<font size="8" color="#999999">{meaning}...</font><br/>
<font size="7" color="#cccccc">tratti: {strokes}</font>
"""
        return cell_text
    
    def create_character_grid(self, characters: List[Dict], 
                            chars_per_page: int = 12,
                            grid_cols: int = 3) -> Table:
        grid_rows = chars_per_page // grid_cols
        table_data = []
        
        for i in range(grid_rows):
            row = []
            for j in range(grid_cols):
                char_idx = i * grid_cols + j
                if char_idx < len(characters):
                    char_info = characters[char_idx]
                    cell_content = self._create_character_cell(char_info)
                    row.append(cell_content)
                else:
                    row.append('')
            table_data.append(row)
        
        table = Table(table_data, colWidths=[5.5*cm]*grid_cols)
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BORDER', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('ROWHEIGHTS', (0, 0), (-1, -1), 4*cm),
        ]))
        
        return table
    
    def generate_pdf_bytes(self, characters: List[Dict], 
                          chars_per_page: int = 12,
                          grid_cols: int = 3) -> bytes:
        """Generate PDF and return as bytes"""
        pdf_buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )
        
        story = []
        
        # Cover page
        spacer = Spacer(1, 3*cm)
        story.append(spacer)
        title = Paragraph(self.title, self.styles['TitleStyle'])
        story.append(title)
        subtitle = Paragraph(
            f"汉语水平考试 HSK {self.level}<br/>Chinese Character Writing Practice",
            self.styles['Normal']
        )
        story.append(subtitle)
        story.append(PageBreak())
        
        # Character pages
        for page_idx in range(0, len(characters), chars_per_page):
            page_chars = characters[page_idx:page_idx + chars_per_page]
            
            header = Paragraph(
                f"Characters {page_idx + 1} - {min(page_idx + chars_per_page, len(characters))}",
                self.styles['Normal']
            )
            story.append(header)
            story.append(Spacer(1, 0.3*cm))
            
            grid = self.create_character_grid(page_chars, chars_per_page=chars_per_page, grid_cols=grid_cols)
            story.append(grid)
            story.append(PageBreak())
        
        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()


# Main app - Load data with caching
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
                gen2 = HSKWorksheetGenerator("HSK 2 Writing Practice", 2)
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
                gen3 = HSKWorksheetGenerator("HSK 3 Writing Practice", 3)
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
    st.error("❌ Impossibile scaricare i dati HSK. Usando dati di fallback...")
    st.info("I dati incorporati contengono i caratteri HSK più comuni. Per la lista completa, riprova tra pochi secondi.")
