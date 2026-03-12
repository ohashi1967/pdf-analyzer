import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

# ページ設定：中央寄せ
st.set_page_config(page_title="PDF解析ツール", layout="centered")

# --- 徹底的に「明るさ」と「視認性」を重視したスタイル ---
st.markdown("""
    <style>
    /* 1. 背景を真っ白に固定 */
    .stApp {
        background-color: #ffffff !important;
    }
    
    /* 2. すべての文字を「真っ黒」に固定（読めない問題を解決） */
    h1, h2, h3, h4, p, span, label, th, td, div {
        color: #000000 !important;
    }

    /* 3. コンテンツエリアの枠組み */
    .main .block-container {
        background-color: #ffffff !important;
        padding: 30px !important;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        margin-top: 20px;
    }

    /* 4. タイトル：明るい青 */
    h1 {
        color: #0047ab !important;
        text-align: center;
        border-bottom: 2px solid #0047ab;
        padding-bottom: 10px;
    }

    /* 5. ファイルアップローダー：明るい水色 */
    [data-testid="stFileUploader"] {
        border: 2px dashed #0047ab !important;
        background-color: #f0f8ff !important;
    }

    /* 6. 表のヘッダー：濃い青に白文字 */
    thead tr th {
        background-color: #0047ab !important;
        color: #ffffff !important;
    }

    /* 7. 基本情報の数字：青色で強調 */
    [data-testid="stMetricValue"] {
        color: #0047ab !important;
        font-weight: bold !important;
    }
    
    /* 8. タブの選択色 */
    button[aria-selected="true"] {
        background-color: #0047ab !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 画面レイアウト ---
st.title("PDF解析ツール")

# アップロード部分
uploaded_file = st.file_uploader("PDFファイルをアップロードしてください", type="pdf", label_visibility="collapsed")

if uploaded_file is not None:
    try:
        file_bytes = uploaded_file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")

        # --- 基本情報 ---
        st.write("### 📋 基本情報")
        c1, c2, c3 = st.columns(3)
        ver = doc.metadata.get("format", "Unknown")
        c1.metric("バージョン", ver)
        c2.metric("ページ数", len(doc))
        c3.metric("容量", f"{len(file_bytes) / 1024:.1f} KB")

        st.write("---")

        # --- 詳細解析 ---
        t1, t2 = st.tabs(["🔤 フォント", "🖼️ 画像解像度"])

        with t1:
            st.write("#### 使用フォント")
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
                        "DPI": dpi,
                        "カラー": img.get("colorspace", "N/A"),
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
    st.markdown("<div style='text-align: center; padding: 50px; color: #555;'>PDFをドロップすると解析が始まります</div>", unsafe_allow_html=True)
