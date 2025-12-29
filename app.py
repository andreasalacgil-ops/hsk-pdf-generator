"""
HSK PDF Generator - Streamlit Web App
Interfaccia web interattiva per generare i PDF
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
    @staticmethod
    def fetch_from_github():
        """Fetch HSK lists from GitHub"""
        try:
            hsk2_url = "https://raw.githubusercontent.com/jiangwenhan/hsk-words/master/data/hsk2.json"
            hsk3_url = "https://raw.githubusercontent.com/jiangwenhan/hsk-words/master/data/hsk3.json"
            
            response2 = requests.get(hsk2_url, timeout=10)
            response3 = requests.get(hsk3_url, timeout=10)
            
            hsk2_chars = []
            hsk3_chars = []
            
            if response2.status_code == 200:
                hsk2_data = response2.json()
                hsk2_chars = [{
                    'char': item.get('word', ''),
                    'pinyin': item.get('pinyin', ''),
                    'meaning': item.get('meaning', ''),
                    'strokes': item.get('strokes', 0),
                    'level': 2
                } for item in hsk2_data if item.get('word')]
            
            if response3.status_code == 200:
                hsk3_data = response3.json()
                hsk3_chars = [{
                    'char': item.get('word', ''),
                    'pinyin': item.get('pinyin', ''),
                    'meaning': item.get('meaning', ''),
                    'strokes': item.get('strokes', 0),
                    'level': 3
                } for item in hsk3_data if item.get('word')]
            
            return hsk2_chars, hsk3_chars
            
        except Exception as e:
            st.error(f"❌ Errore nel download: {e}")
            return [], []


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
        meaning = char_info['meaning'][:20]
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

st.header("📥 Scaricamento dati...")
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
    st.error("❌ Impossibile scaricare i dati HSK. Controlla la connessione internet.")
