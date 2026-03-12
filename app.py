import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

# ページ設定
st.set_page_config(page_title="PDF解析ツール", layout="centered")

# --- アイコン・文字を全て白抜き、文言を「ここにPDFをドロップ」に変更 ---
st.markdown("""
    <style>
    /* 全体の背景を白に固定 */
    .stApp {
        background-color: #ffffff !important;
    }

    /* 1. アップロードバー全体：濃い青 */
    [data-testid="stFileUploader"] {
        background-color: #1e3a8a !important; 
        border: 2px dashed #3b82f6 !important;
        border-radius: 12px;
        padding: 30px 20px !important;
    }

    /* 2. ドロップエリア中央：濃い青 */
    [data-testid="stFileUploader"] section {
        background-color: #1e3a8a !important;
        border: none !important;
    }

    /* 3. 雲のマーク（アイコン）を白抜きに */
    [data-testid="stFileUploader"] svg {
        fill: #ffffff !important;
        color: #ffffff !important;
    }

    /* 元の英語テキストを非表示 */
    [data-testid="stFileUploader"] section > div > div > span {
        display: none !important;
    }

    /* 指定の日本語文言を挿入（白抜き・太字） */
    [data-testid="stFileUploader"] section > div > div::before {
        content: "ここにPDFをドロップ";
        color: #ffffff !important;
        font-weight: bold !important;
        font-size: 1.2rem !important;
        display: block;
        margin-bottom: 10px;
    }

    /* 補助テキストも白 */
    [data-testid="stFileUploader"] section > div > small {
        color: #e2e8f0 !important;
    }

    /* 4. ボタン：白背景・青文字 */
    [data-testid="stFileUploader"] button {
        background-color: #ffffff !important;
        color: #1e3a8a !important;
        border: none !important;
        font-weight: bold !important;
    }

    /* 5. 結果エリア：常に黒文字 */
    h1, h2, h3, p, span, label, td, .stMarkdown {
        color: #000000 !important;
    }

    /* タイトル */
    h1 {
        color: #1e3a8a !important;
        text-align: center;
    }

    /* テーブルヘッダー */
    thead tr th {
        background-color: #1e3a8a !important;
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 画面構成 ---
st.title("PDF解析ツール")

uploaded_file = st.file_uploader(
    "PDFアップロード", 
    type="pdf", 
    label_visibility="collapsed"
)

if uploaded_file is not None:
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
                st.info("フォント情報なし")

        with tab2:
            st.write("#### 画像解像度チェック")
            i_list = []
            for i, page in enumerate(doc):
                for img in page.get_image_info(hashes=True):
                    b = img["bbox"]
                    wi, hi = (b[2]-b[0])/72, (b[3]-b[1])/72
                    dpi = round(max(img["width"]/wi, img["height"]/hi)) if wi>0 else 0
                    i_list.append({
                        "ページ": i+1,
                        "DPI": dpi,
                        "判定": "OK" if dpi>=300 else "⚠️ 低"
                    })
            if i_list:
                st.dataframe(pd.DataFrame(i_list), use_container_width=True)
            else:
                st.info("画像なし")
        doc.close()

    except Exception:
        st.error("エラーが発生しました。")
else:
    st.markdown("<p style='text-align: center; font-weight: bold; color: #1e3a8a; padding: 40px;'>上の青い枠にPDFをドロップしてください</p>", unsafe_allow_html=True)
