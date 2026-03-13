import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

# ページ設定
st.set_page_config(page_title="PDF解析ツール", layout="centered")

# --- デザイン設定（青いバー、白抜き文字、アイコン、固定レイアウト） ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    
    /* アップロードバーのデザイン */
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

    /* 文字色と見出しの固定 */
    h1, h2, h3, h4, p, span, label, td, .stMarkdown { color: #000000 !important; }
    h1, h3 { color: #1e3a8a !important; }
    h1 { text-align: center; margin-bottom: 30px !important; }
    
    /* セクションの区切り */
    .section-box {
        margin-top: 40px;
        padding: 20px;
        border-top: 2px solid #f0f2f6;
    }

    /* テーブルヘッダー */
    thead tr th { background-color: #1e3a8a !important; color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("PDF解析ツール")

uploaded_file = st.file_uploader("PDFアップロード", type="pdf", label_visibility="collapsed")

if uploaded_file is not None:
    try:
        file_bytes = uploaded_file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")

        # --- 基本情報 ---
        st.write("### 📋 基本情報")
        col1, col2, col3 = st.columns(3)
        col1.metric("バージョン", doc.metadata.get("format", "Unknown"))
        col2.metric("総ページ数", len(doc))
        col3.metric("容量", f"{len(file_bytes) / 1024:.1f} KB")

        # --- 上段：画像解析 ---
        st.markdown("<div class='section-box'></div>", unsafe_allow_html=True)
        st.write("### 🖼️ 画像解析")
        i_list = []
        for i, page in enumerate(doc):
            images = page.get_images(full=True)
            for img_info in images:
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                
                # カラーモード判定
                cs = base_image.get("colorspace", 0)
                bpc = base_image.get("bpc", 8)
                if cs == 4: mode = "CMYK"
                elif cs == 3: mode = "RGB"
                elif cs == 1: mode = "モノクロ2階調" if bpc == 1 else "グレースケール"
                else: mode = f"その他({cs})"

                # 圧縮形式
                ext = base_image.get("ext", "").upper()
                if ext == "JPEG": compress = "JPEG"
                elif ext == "PNG": compress = "ZIP"
                else: compress = ext

                # サイズとDPI
                px_w = base_image["width"]
                px_h = base_image["height"]
                
                for detailed_info in page.get_image_info():
                    if detailed_info.get("xref") == xref:
                        b = detailed_info["bbox"]
                        wi, hi = (b[2]-b[0])/72, (b[3]-b[1])/72
                        dpi = round(max(px_w/wi, px_h/hi)) if wi>0 else 0
                        
                        i_list.append({
                            "P.": i+1,
                            "DPI": dpi,
                            "モード": mode,
                            "形式": compress,
                            "サイズ(px)": f"{px_w}x{px_h}"
                        })
                        break

        if i_list:
            st.dataframe(pd.DataFrame(i_list), use_container_width=True)
        else:
            st.info("画像は見つかりませんでした。")

        # --- 下段：フォント確認 ---
        st.markdown("<div class='section-box'></div>", unsafe_allow_html=True)
        st.write("### 🔤 フォント確認")
        f_list = []
        for page in doc:
            for f in page.get_fonts():
                f_list.append({
                    "フォント名": f[3], 
                    "埋め込み": "✅ 済" if f[4] != 0 else "❌ 未"
                })
        
        if f_list:
            df_fonts = pd.DataFrame(f_list).drop_duplicates().reset_index(drop=True)
            st.table(df_fonts)
        else:
            st.info("フォント情報は見つかりませんでした。")

        doc.close()
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
else:
    st.markdown("<p style='text-align: center; font-weight: bold; color: #1e3a8a; padding: 40px;'>上の青い枠にPDFをドロップしてください</p>", unsafe_allow_html=True)
