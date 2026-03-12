import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

# ページ設定
st.set_page_config(page_title="PDF解析ツール", layout="centered")

# --- 「脱・黒」！明るい青と白の視認性重視デザイン ---
st.markdown("""
    <style>
    /* 背景を完全に白に固定（ダークモードを無効化） */
    .stApp {
        background-color: #ffffff !important;
    }
    
    /* 1. 上のバー（ファイルアップローダー）のデザインを青基調に */
    [data-testid="stFileUploader"] {
        border: 2px dashed #007bff !important; /* 青い点線 */
        background-color: #f0f7ff !important; /* 薄い水色 */
        border-radius: 10px;
    }
    /* アップローダー内の「Drag and drop」などの文字を濃い青に */
    [data-testid="stFileUploader"] section div {
        color: #004085 !important;
    }
    [data-testid="stFileUploader"] button {
        background-color: #007bff !important;
        color: white !important;
        border: none;
    }

    /* 2. 下の文字が入っているボックス（カード）を明るく */
    .main .block-container {
        background-color: #ffffff !important;
        padding: 40px !important;
        border: 1px solid #dee2e6;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    /* 3. すべての文字を「濃い紺色」に固定（黒より読みやすく） */
    h1, h2, h3, h4, p, span, label, th, td, div {
        color: #1a3044 !important;
    }

    /* タイトル：爽やかな青 */
    h1 {
        color: #007bff !important;
        text-align: center;
        border-bottom: 2px solid #007bff;
        padding-bottom: 10px;
        margin-bottom: 30px !important;
    }

    /* 表のヘッダー：明るい青に白文字 */
    thead tr th {
        background-color: #007bff !important;
        color: #ffffff !important;
    }

    /* メトリック（数字部分） */
    [data-testid="stMetricValue"] {
        color: #007bff !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 画面レイアウト ---
st.title("PDF解析ツール")

# 1. ファイルアップローダー（ここが青いボックスになります）
uploaded_file = st.file_uploader("PDFファイルをここにドラッグ＆ドロップしてください", type="pdf", label_visibility="collapsed")

if uploaded_file is not None:
    try:
        file_bytes = uploaded_file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")

        # 2. 解析結果表示エリア
        st.write("### 📋 基本情報")
        c1, c2, c3 = st.columns(3)
        ver = doc.metadata.get("format", "Unknown")
        c1.metric("バージョン", ver)
        c2.metric("総ページ数", f"{len(doc)}")
        c3.metric("サイズ", f"{len(file_bytes) / 1024:.1f} KB")

        st.write("---")

        t1, t2 = st.tabs(["🔤 フォント", "🖼️ 画像解像度"])

        with t1:
            st.write("#### 使用フォント")
            f_list = []
            for page in doc:
                for f in page.get_fonts():
                    f_list.append({
                        "フォント名": f[3], 
                        "埋め込み状態": "✅ 埋込済" if f[4] != 0 else "❌ 未埋込"
                    })
            if f_list:
                st.table(pd.DataFrame(f_list).drop_duplicates())
            else:
                st.info("フォント情報なし")

        with t2:
            st.write("#### 画像解析")
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
                st.info("画像なし")
        doc.close()
    except Exception:
        st.error("解析エラーが発生しました。")
else:
    st.markdown("<div style='text-align: center; padding: 50px; color: #007bff;'>PDFを選択すると解析を開始します</div>", unsafe_allow_html=True)
