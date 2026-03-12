import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

# ページ設定
st.set_page_config(page_title="PDF解析ツール", layout="centered")

# --- 明るく、読みやすい青を基調としたデザイン設定 ---
st.markdown("""
    <style>
    /* 全体の背景：清潔感のある非常に薄いグレー */
    .stApp {
        background-color: #fcfdfe !important;
    }
    
    /* 中央の白カード：文字色を「超濃いグレー」で固定 */
    .main .block-container {
        background-color: #ffffff !important;
        color: #1a1a1a !important; /* ほぼ黒 */
        padding: 40px !important;
        border-radius: 12px;
        box-shadow: 0 4px 25px rgba(0,0,0,0.05);
        margin-top: 40px;
    }

    /* タイトル：明るく力強い青 */
    h1 {
        color: #0056b3 !important;
        font-weight: 800 !important;
        text-align: center;
        border-bottom: 3px solid #0056b3;
        padding-bottom: 15px;
        margin-bottom: 30px !important;
    }

    /* 各種テキストの見やすさを確保 */
    h2, h3, p, span, label, div {
        color: #2c3e50 !important; /* 濃い紺色に近いグレー */
    }

    /* ファイルアップローダー：明るい水色の枠 */
    [data-testid="stFileUploader"] {
        border: 2px dashed #007bff !important;
        background-color: #f0f7ff !important;
        border-radius: 10px;
    }

    /* メトリック（基本情報）の数字を強調 */
    [data-testid="stMetricValue"] {
        color: #0056b3 !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #555555 !important;
        font-size: 1rem !important;
    }

    /* 表のヘッダー：見本のような綺麗な青 */
    thead tr th {
        background-color: #0056b3 !important;
        color: #ffffff !important;
        font-weight: bold !important;
    }
    
    /* 表のセル文字もはっきりと */
    tbody td {
        color: #1a1a1a !important;
    }

    /* タブのスタイル */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f8f9fa;
        border-radius: 5px 5px 0 0;
        padding: 10px 20px;
        color: #555555;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0056b3 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 画面構成 ---
st.title("PDF解析ツール")

# アップロードエリア
uploaded_file = st.file_uploader("ファイルをここにドロップしてください", type="pdf", label_visibility="collapsed")

if uploaded_file is not None:
    try:
        file_bytes = uploaded_file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")

        # 基本情報カード
        st.markdown("### 📋 基本情報")
        col1, col2, col3 = st.columns(3)
        
        pdf_version = doc.metadata.get("format", "Unknown")
        
        col1.metric("バージョン", pdf_version)
        col2.metric("総ページ数", len(doc))
        col3.metric("サイズ", f"{len(file_bytes) / 1024:.1f} KB")

        st.markdown("<br>", unsafe_allow_html=True)

        # タブ切り替え
        tab1, tab2 = st.tabs(["🔤 フォント", "🖼️ 画像解像度"])

        with tab1:
            st.markdown("#### 使用フォント一覧")
            font_list = []
            for page in doc:
                for f in page.get_fonts():
                    font_list.append({
                        "フォント名": f[3], 
                        "埋め込み状態": "✅ 埋込済" if f[4] != 0 else "❌ 未埋込"
                    })
            if font_list:
                df_font = pd.DataFrame(font_list).drop_duplicates()
                st.table(df_font)
            else:
                st.info("フォント情報は検出されませんでした。")

        with tab2:
            st.markdown("#### 配置画像の状態")
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
                        "判定": "OK" if dpi >= 300 else "⚠️ 低解像度"
                    })
            
            if img_list:
                st.dataframe(pd.DataFrame(img_list), use_container_width=True)
            else:
                st.info("画像は検出されませんでした。")
        
        doc.close()

    except Exception as e:
        st.error("エラーが発生しました。ファイルの形式を確認してください。")
else:
    # 待機中の表示
    st.markdown("<div style='text-align: center; padding: 60px; color: #7f8c8d; font-size: 1.1em;'>PDFをアップロードすると解析を開始します</div>", unsafe_allow_html=True)
