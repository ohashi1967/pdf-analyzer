import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

# ページ設定
st.set_page_config(page_title="PDF解析ツール", layout="centered")

# --- 視認性を極限まで高めたスタイル設定 ---
st.markdown("""
    <style>
    /* 全体の背景を白に固定 */
    .stApp {
        background-color: #ffffff !important;
    }
    
    /* 1. アップロードエリア（バー）を濃い青に固定 */
    [data-testid="stFileUploader"] {
        background-color: #1e3a8a !important; /* 濃い青 */
        border: 2px dashed #3b82f6 !important;
        border-radius: 10px;
        padding: 20px;
    }

    /* 2. アップロードエリア内の文字を「白・太字」に強制 */
    [data-testid="stFileUploader"] section div {
        color: #ffffff !important;
        font-weight: bold !important;
    }
    /* 「Browse files」ボタンの文字色 */
    [data-testid="stFileUploader"] button {
        color: #1e3a8a !important;
        background-color: #ffffff !important;
        font-weight: bold !important;
    }

    /* 3. 解析結果エリアの文字を黒に固定 */
    .main .block-container {
        color: #000000 !important;
    }
    h1, h2, h3, p, span, label, td {
        color: #000000 !important;
    }

    /* タイトルとヘッダー */
    h1 {
        color: #1e3a8a !important;
        text-align: center;
    }
    thead tr th {
        background-color: #1e3a8a !important;
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 画面構成 ---
st.title("PDF解析ツール")

# 日本語メッセージを直接指定
uploaded_file = st.file_uploader(
    "ここにファイルをドロップ（PDF）", 
    type="pdf", 
    label_visibility="collapsed"
)

# アップロード前後の日本語案内
if uploaded_file is None:
    st.markdown("<p style='text-align: center; font-weight: bold; padding: 20px;'>PDFを選択またはドロップしてください</p>", unsafe_allow_html=True)
else:
    try:
        file_bytes = uploaded_file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")

        st.write("### 📋 基本情報")
        col1, col2, col3 = st.columns(3)
        ver = doc.metadata.get("format", "Unknown")
        
        col1.metric("バージョン", ver)
        col2.metric("総ページ数", len(doc))
        col3.metric("容量", f"{len(file_bytes) / 1024:.1f} KB")

        st.write("---")

        tab1, tab2 = st.tabs(["🔤 フォント確認", "🖼️ 画像解析"])

        with tab1:
            st.write("#### 使用フォント一覧")
            f_list = []
            for page in doc:
                for f in page.get_fonts():
                    f_list.append({
                        "フォント名": f[3], 
                        "埋め込み": "✅ 済" if f[4] != 0 else "❌ 未"
                    })
            if f_list:
                st.table(pd.DataFrame(f_list).drop_duplicates())
            else:
                st.info("フォント情報はありません")

        with tab2:
            st.write("#### 画像解像度チェック")
            i_list = []
            for i, page in enumerate(doc):
                for img in page.get_image_info(hashes=True):
                    b = img["bbox"]
                    wi, hi = (b[2]-b[0])/72, (b[3]-b[1])/72
                    dpi = round(max(img["width"]/wi, img["height"]/hi)) if wi>0 else 0
                    i_list.append({
                        "P.": i+1,
                        "解像度(DPI)": dpi,
                        "モード": img.get("colorspace", "N/A"),
                        "判定": "OK" if dpi>=300 else "⚠️ 低"
                    })
            if i_list:
                st.dataframe(pd.DataFrame(i_list), use_container_width=True)
            else:
                st.info("画像はありません")
        doc.close()

    except Exception:
        st.error("解析エラーが発生しました。")
