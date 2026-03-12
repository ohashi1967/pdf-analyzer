import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

# ページ設定
st.set_page_config(page_title="PDF解析ツール", layout="centered")

# 502エラーを防ぐため、CSSの記述を最も安全な形式に修正
st.markdown("""
    <style>
    /* 全体の背景 */
    .stApp {
        background-color: #f0f4f8 !important;
    }
    
    /* 中央のカード（白背景・濃い文字を強制） */
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        color: #333333 !important;
    }

    .main .block-container {
        background-color: #ffffff !important;
        color: #333333 !important;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-top: 50px;
        margin-bottom: 50px;
    }

    /* 文字色を黒〜濃いグレーに固定 */
    h1, h2, h3, p, span, label {
        color: #1a3a6d !important;
    }

    /* メトリック（数字）の色 */
    [data-testid="stMetricValue"] {
        color: #1a3a6d !important;
    }
    [data-testid="stMetricLabel"] {
        color: #555555 !important;
    }

    /* テーブルのスタイル */
    thead tr th {
        background-color: #1a3a6d !important;
        color: #ffffff !important;
    }
    
    /* アップローダー */
    [data-testid="stFileUploader"] {
        border: 2px dashed #1a3a6d !important;
        border-radius: 10px;
        background-color: #f8fbff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- メイン画面 ---
st.title("📄 PDF内部構造 解析ツール")

uploaded_file = st.file_uploader("PDFファイルをアップロード", type="pdf", label_visibility="collapsed")

if uploaded_file is not None:
    try:
        file_bytes = uploaded_file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")

        st.write("### 📋 基本情報")
        col1, col2, col3 = st.columns(3)
        
        # 以前のエラー原因(pdf_get_version)を回避した安全な取得方法
        pdf_version = doc.metadata.get("format", "Unknown")
        
        col1.metric("バージョン", pdf_version)
        col2.metric("総ページ数", f"{len(doc)}")
        col3.metric("サイズ", f"{len(file_bytes) / 1024:.1f} KB")

        st.write("---")

        tab1, tab2 = st.tabs(["🔤 フォント", "🖼️ 画像解像度"])

        with tab1:
            font_list = []
            for page in doc:
                for f in page.get_fonts():
                    font_list.append({
                        "フォント名": f[3], 
                        "埋め込み": "✅ 埋込済" if f[4] != 0 else "❌ 未埋込"
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
                        "DPI": dpi,
                        "モード": img.get("colorspace", "N/A"),
                        "判定": "OK" if dpi >= 300 else "⚠️ 低"
                    })
            
            if img_list:
                st.dataframe(pd.DataFrame(img_list), use_container_width=True)
            else:
                st.info("画像は見つかりませんでした。")
        
        doc.close()

    except Exception as e:
        st.error(f"解析中にエラーが発生しました: {e}")
else:
    st.markdown("<div style='text-align: center; padding: 50px; color: #666;'>ファイルをドロップしてください</div>", unsafe_allow_html=True)
