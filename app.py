import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

# ページ設定
st.set_page_config(page_title="PDF解析ツール", layout="centered")

# --- デザイン設定（青いバー、白抜き文字、アイコン白抜き） ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    [data-testid="stFileUploader"] {
        background-color: #1e3a8a !important; 
        border: 2px dashed #3b82f6 !important;
        border-radius: 12px;
        padding: 30px 20px !important;
    }
    [data-testid="stFileUploader"] section {
        background-color: #1e3a8a !important;
        border: none !important;
    }
    [data-testid="stFileUploader"] svg {
        fill: #ffffff !important;
        color: #ffffff !important;
    }
    [data-testid="stFileUploader"] section > div > div > span { display: none !important; }
    [data-testid="stFileUploader"] section > div > div::before {
        content: "ここにPDFをドロップ";
        color: #ffffff !important;
        font-weight: bold !important;
        font-size: 1.2rem !important;
        display: block;
        margin-bottom: 10px;
    }
    [data-testid="stFileUploader"] section > div > small { color: #e2e8f0 !important; }
    [data-testid="stFileUploader"] button {
        background-color: #ffffff !important;
        color: #1e3a8a !important;
        border: none !important;
        font-weight: bold !important;
    }
    h1, h2, h3, p, span, label, td, .stMarkdown { color: #000000 !important; }
    h1 { color: #1e3a8a !important; text-align: center; }
    thead tr th { background-color: #1e3a8a !important; color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("PDF解析ツール")

uploaded_file = st.file_uploader("PDFアップロード", type="pdf", label_visibility="collapsed")

if uploaded_file is not None:
    try:
        file_bytes = uploaded_file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")

        st.write("### 📋 基本情報")
        col1, col2, col3 = st.columns(3)
        col1.metric("バージョン", doc.metadata.get("format", "Unknown"))
        col2.metric("総ページ数", len(doc))
        col3.metric("容量", f"{len(file_bytes) / 1024:.1f} KB")

        st.write("---")

        tab1, tab2 = st.tabs(["🔤 フォント確認", "🖼️ 画像解析"])

        with tab1:
            st.write("#### 使用フォント一覧")
            f_list = [{"フォント名": f[3], "埋め込み": "✅ 済" if f[4] != 0 else "❌ 未"} for page in doc for f in page.get_fonts()]
            if f_list:
                st.table(pd.DataFrame(f_list).drop_duplicates())
            else:
                st.info("フォント情報なし")

        with tab2:
            st.write("#### 画像解像度・カラーモード")
            i_list = []
            for i, page in enumerate(doc):
                for img in page.get_image_info(hashes=True):
                    # 解像度計算
                    b = img["bbox"]
                    wi, hi = (b[2]-b[0])/72, (b[3]-b[1])/72
                    dpi = round(max(img["width"]/wi, img["height"]/hi)) if wi>0 else 0
                    
                    # --- カラーモード判定ロジック ---
                    cs = img.get("colorspace", 0)
                    bpc = img.get("bpc", 8) # bits per component
                    
                    if cs == 4: # DeviceCMYK
                        mode = "CMYK"
                    elif cs == 3: # DeviceRGB
                        mode = "RGB"
                    elif cs == 1: # DeviceGray
                        # 1ビットならモノクロ2階調、それ以外はグレースケール
                        mode = "モノクロ2階調" if bpc == 1 else "グレースケール"
                    else:
                        mode = f"その他({cs})"

                    i_list.append({
                        "ページ": i+1,
                        "DPI": dpi,
                        "モード": mode,
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
