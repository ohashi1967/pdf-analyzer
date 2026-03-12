import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

# ページ設定
st.set_page_config(page_title="PDF解析ツール", layout="centered")

# --- ダークモードでも強制的に色を固定するスタイル設定 ---
st.markdown("""
    <style>
    /* 1. 全体の背景を落ち着いた薄いグレーに固定 */
    .stApp {
        background-color: #f4f7f9 !important;
    }
    
    /* 2. メインコンテンツの白いボックス（文字は常に黒） */
    .main .block-container {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        padding: 40px !important;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-top: 30px;
    }

    /* 3. 上のバー（ファイルアップローダー）を濃い青に固定 */
    [data-testid="stFileUploader"] {
        background-color: #1e3a8a !important; /* 濃い青 */
        border: 2px dashed #3b82f6 !important;
        border-radius: 10px;
        padding: 20px;
    }
    /* バーの中の文字を「白」に固定 */
    [data-testid="stFileUploader"] section div, 
    [data-testid="stFileUploader"] label, 
    [data-testid="stFileUploader"] small {
        color: #ffffff !important;
    }
    /* アップロードボタンの調整 */
    [data-testid="stFileUploader"] button {
        background-color: #ffffff !important;
        color: #1e3a8a !important;
        border: none !important;
    }

    /* 4. タイトルや見出し */
    h1 {
        color: #1e3a8a !important;
        text-align: center;
        font-weight: bold;
        border-bottom: 2px solid #1e3a8a;
        padding-bottom: 10px;
    }

    /* 5. 表のヘッダー（濃い青に白文字） */
    thead tr th {
        background-color: #1e3a8a !important;
        color: #ffffff !important;
    }
    
    /* 6. 解析結果の文字色を「黒」に固定 */
    p, span, td, div.stMarkdown {
        color: #1a1a1a !important;
    }

    /* メトリック（基本情報）の数字 */
    [data-testid="stMetricValue"] {
        color: #1e3a8a !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 画面構成 ---
st.title("PDF解析ツール")

# 濃い青色のバー（アップローダー）
uploaded_file = st.file_uploader("PDFファイルをここにドラッグ＆ドロップしてください", type="pdf", label_visibility="collapsed")

if uploaded_file is not None:
    try:
        file_bytes = uploaded_file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")

        st.write("### 📋 基本情報")
        col1, col2, col3 = st.columns(3)
        ver = doc.metadata.get("format", "Unknown")
        
        col1.metric("バージョン", ver)
        col2.metric("総ページ数", f"{len(doc)}")
        col3.metric("サイズ", f"{len(file_bytes) / 1024:.1f} KB")

        st.write("---")

        tab1, tab2 = st.tabs(["🔤 フォント", "🖼️ 画像解像度"])

        with tab1:
            st.write("#### 使用フォント一覧")
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
                st.info("フォント情報は見つかりませんでした。")

        with tab2:
            st.write("#### 画像解析結果")
            i_list = []
            for i, page in enumerate(doc):
                for img in page.get_image_info(hashes=True):
                    b = img["bbox"]
                    wi, hi = (b[2]-b[0])/72, (b[3]-b[1])/72
                    dpi = round(max(img["width"]/wi, img["height"]/hi)) if wi>0 else 0
                    i_list.append({
                        "ページ": i+1,
                        "解像度(DPI)": dpi,
                        "カラーモード": img.get("colorspace", "N/A"),
                        "判定": "OK" if dpi>=300 else "⚠️ 低解像度"
                    })
            if i_list:
                st.dataframe(pd.DataFrame(i_list), use_container_width=True)
            else:
                st.info("画像は見つかりませんでした。")
        doc.close()

    except Exception:
        st.error("解析中にエラーが発生しました。")
else:
    st.markdown("<div style='text-align: center; padding: 60px; color: #1e3a8a; font-weight: bold;'>PDFを選択してください</div>", unsafe_allow_html=True)
