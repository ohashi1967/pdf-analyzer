import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

# ページ設定
st.set_page_config(page_title="PDF解析ツール", layout="centered")

# --- ダークモード/ライトモード不問：視認性固定デザイン ---
st.markdown("""
    <style>
    /* 1. 背景を常に白に固定 */
    .stApp {
        background-color: #ffffff !important;
    }

    /* 2. アップロードバー全体を濃い青に固定 */
    [data-testid="stFileUploader"] {
        background-color: #1e3a8a !important; 
        border: 2px dashed #3b82f6 !important;
        border-radius: 12px;
        padding: 30px 20px !important;
    }

    /* 3. バーの中央部分（ドロップエリア）も青に固定し、文字を白抜きに */
    [data-testid="stFileUploader"] section {
        background-color: #1e3a8a !important;
        border: none !important;
    }

    /* 元の英語テキストを消す */
    [data-testid="stFileUploader"] section > div > div > span {
        display: none !important;
    }

    /* 日本語の白抜き文字を挿入（太字でくっきり） */
    [data-testid="stFileUploader"] section > div > div::before {
        content: "ここにファイルをドロップしてください (PDF)";
        color: #ffffff !important;
        font-weight: bold !important;
        font-size: 1.2rem !important;
        display: block;
        margin-bottom: 10px;
    }

    /* 補助テキスト（容量制限など）も白く */
    [data-testid="stFileUploader"] section > div > small {
        color: #e2e8f0 !important;
        font-weight: normal !important;
    }

    /* 4. ボタンを白背景・青文字で固定 */
    [data-testid="stFileUploader"] button {
        background-color: #ffffff !important;
        color: #1e3a8a !important;
        border: none !important;
        font-weight: bold !important;
    }

    /* 5. 結果エリアの文字を常に「黒」に固定（白飛び防止） */
    h1, h2, h3, p, span, label, td, .stMarkdown {
        color: #000000 !important;
    }

    /* タイトルデザイン */
    h1 {
        color: #1e3a8a !important;
        text-align: center;
        margin-bottom: 30px !important;
    }

    /* 表のスタイル */
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
                        "ページ": i+1,
                        "DPI": dpi,
                        "モード": img.get("colorspace", "N/A"),
                        "判定": "OK" if dpi>=300 else "⚠️ 低"
                    })
            if i_list:
                st.dataframe(pd.DataFrame(i_list), use_container_width=True)
            else:
                st.info("画像はありません")
        doc.close()

    except Exception:
        st.error("エラーが発生しました。")
else:
    st.markdown("<p style='text-align: center; font-weight: bold; color: #1e3a8a; padding: 40px;'>上の青い枠にPDFをドロップしてください</p>", unsafe_allow_html=True)
