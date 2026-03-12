import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

# ページ設定
st.set_page_config(page_title="PDF解析ツール", layout="centered")

# 画像のデザインに合わせたカスタムCSS
st.markdown("""
    <style>
    /* 全体の背景色 */
    .stApp {
        background-color: #f0f4f8;
    }
    /* メインコンテンツのカード表示 */
    .main .block-container {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-top: 50px;
        margin-bottom: 50px;
    }
    /* タイトルのスタイル */
    h1 {
        color: #3b5998;
        font-size: 24px !important;
        border-bottom: 2px solid #3b5998;
        padding-bottom: 10px;
    }
    /* アップローダーの枠線カスタマイズ */
    [data-testid="stFileUploader"] {
        border: 2px dashed #3b5998;
        border-radius: 10px;
        padding: 20px;
        background-color: #f8fbff;
    }
    /* テーブルヘッダーの青背景再現 */
    thead tr th {
        background-color: #3b5998 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ヘッダー ---
st.title("📄 PDF内部構造 解析ツール")

# --- アップロードエリア (画像の中央配置を再現) ---
uploaded_file = st.file_uploader("ここにファイルをドロップ (PDFのみ)", type="pdf", label_visibility="collapsed")

if uploaded_file is not None:
    # PDFをメモリ上で読み込み
    file_bytes = uploaded_file.read()
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    # --- 基本情報のカード表示 ---
    st.write("### 📋 基本情報")
    col1, col2, col3 = st.columns(3)
    pdf_version = doc.metadata.get("format", "Unknown")
    col1.metric("PDFバージョン", pdf_version)
    col2.metric("総ページ数", f"{len(doc)}")
    col3.metric("サイズ", f"{len(file_bytes) / 1024:.1f} KB")

    # --- 解析結果テーブル (画像の下部テーブルを再現) ---
    st.write("### 🔍 解析データ")
    
    # フォントと画像を統合したデータリストの作成
    tab1, tab2 = st.tabs(["🔤 フォント", "🖼️ 画像解像度"])

    with tab1:
        font_list = []
        for page in doc:
            for f in page.get_fonts():
                font_list.append({
                    "場所/P.": "全ページ", 
                    "抽出されたフォント": f[3], 
                    "状態": "✅ 埋込済" if f[4] != 0 else "❌ 未埋込"
                })
        df_font = pd.DataFrame(font_list).drop_duplicates()
        st.table(df_font)

    with tab2:
        img_list = []
        for page_index in range(len(doc)):
            page = doc[page_index]
            for img in page.get_image_info(hashes=True):
                bbox = img["bbox"]
                width_inch = (bbox[2] - bbox[0]) / 72
                height_inch = (bbox[3] - bbox[1]) / 72
                dpi = round(max(img["width"] / width_inch, img["height"] / height_inch))
                
                img_list.append({
                    "ページ": page_index + 1,
                    "ピクセル": f"{img['width']}x{img['height']}",
                    "判定DPI": dpi,
                    "結果": "OK" if dpi >= 300 else "低解像度"
                })
        
        if img_list:
            df_img = pd.DataFrame(img_list)
            st.dataframe(df_img, use_container_width=True)
        else:
            st.info("画像は見つかりませんでした。")

    doc.close()
else:
    # 未アップロード時のプレースホルダー
    st.write("")
    st.markdown("<p style='text-align: center; color: #888;'>ファイルをドロップしてください</p>", unsafe_allow_html=True)
