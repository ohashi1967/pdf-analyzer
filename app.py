import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

# ページ設定
st.set_page_config(page_title="PDF解析ツール", layout="centered")

# 強制的に「白背景・濃い文字」にするための修正CSS
st.markdown("""
    <style>
    /* 全体の背景（薄いグレー） */
    .stApp {
        background-color: #f0f4f8 !important;
    }
    
    /* 中央のカード（白背景・濃い文字を強制） */
    .main .block-container {
        background-color: #ffffff !important;
        color: #333333 !important; /* 濃いグレーの文字 */
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-top: 50px;
        margin-bottom: 50px;
    }

    /* タイトル（濃い青） */
    h1, h2, h3 {
        color: #1a3a6d !important;
    }

    /* 各種テキストの色の固定 */
    p, span, label, .stMarkdown {
        color: #333333 !important;
    }

    /* アップローダーの枠 */
    [data-testid="stFileUploader"] {
        border: 2px dashed #1a3a6d !important;
        border-radius: 10px;
        background-color: #f8fbff !important;
    }

    /* テーブルのヘッダー */
    thead tr th {
        background-color: #1a3a6d !important;
        color: #ffffff !important;
    }

    /* メトリック（数字）のラベルと値 */
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
        color: #333333 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ヘッダー ---
st.title("📄 PDF内部構造 解析ツール")

# --- アップロードエリア ---
uploaded_file = st.file_uploader("PDFファイルをアップロード", type="pdf", label_visibility="collapsed")

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    st.write("### 📋 基本情報")
    col1, col2, col3 = st.columns(3)
    pdf_version = doc.metadata.get("format", "Unknown")
    
    with col1:
        st.metric("PDFバージョン", pdf_version)
    with col2:
        st.metric("総ページ数", f"{len(doc)}")
    with col3:
        st.metric("サイズ", f"{len(file_bytes) / 1024:.1f} KB")

    st.write("---")

    tab1, tab2 = st.tabs(["🔤 フォント", "🖼️ 画像解像度"])

    with tab1:
        font_list = []
        for page in doc:
            for f in page.get_fonts():
                font_list.append({
                    "抽出されたフォント": f[3], 
                    "状態": "✅ 埋込済" if f[4] != 0 else "❌ 未埋込"
                })
        if font_list:
            df_font = pd.DataFrame(font_list).drop_duplicates()
            st.table(df_font)
        else:
            st.info("フォント情報はありません。")

    with tab2:
        img_list = []
        for page_index in range(len(doc)):
            page = doc[page_index]
            for img in page.get_image_info(hashes=True):
                bbox = img["bbox"]
                w_inch = (bbox[2] - bbox[0]) / 72
                h_inch = (bbox[3] - bbox[1]) / 72
                dpi = round(max(img["width"] / w_inch, img["height"] / h_inch)) if w_inch > 0 else 0
                
                img_list.append({
                    "P.": page_index + 1,
                    "解像度(DPI)": dpi,
                    "モード": img.get("colorspace", "N/A"),
                    "判定": "OK" if dpi >= 300 else "⚠️ 低"
                })
        
        if img_list:
            st.dataframe(pd.DataFrame(img_list), use_container_width=True)
        else:
            st.info("画像は見つかりませんでした。")

    doc.close()
else:
    st.markdown("<div style='text-align: center; padding: 50px; color: #666;'>ファイルをドロップしてください</div>", unsafe_allow_html=True)
