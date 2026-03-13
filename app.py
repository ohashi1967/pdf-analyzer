import streamlit as st

# ページ設定（これは最初に行う必要があります）
st.set_page_config(page_title="PDF解析ツール", layout="centered")

# --- デザイン設定（青いバー、白抜き文字、スクロール枠） ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; }
    [data-testid="stFileUploader"] {
        background-color: #1e3a8a !important; 
        border: 2px dashed #3b82f6 !important;
        border-radius: 12px;
        padding: 30px 20px !important;
    }
    [data-testid="stFileUploader"] section { background-color: #1e3a8a !important; border: none !important; }
    [data-testid="stFileUploader"] svg { fill: #ffffff !important; color: #ffffff !important; }
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
    h1, h2, h3, h4, p, span, label, td, .stMarkdown { color: #000000 !important; }
    h1, h3 { color: #1e3a8a !important; }
    h1 { text-align: center; margin-bottom: 30px !important; }
    .section-box { margin-top: 30px; padding-top: 20px; border-top: 2px solid #f0f2f6; }
    thead tr th { background-color: #1e3a8a !important; color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("PDF解析ツール")

uploaded_file = st.file_uploader("PDFアップロード", type="pdf", label_visibility="collapsed")

if uploaded_file is not None:
    # --- 遅延インポート（解析が始まってから重いライブラリを読み込む） ---
    import fitz  # PyMuPDF
    import pandas as pd

    try:
        file_bytes = uploaded_file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")

        # --- 基本情報 ---
        st.write("### 📋 基本情報")
        col1, col2, col3 = st.columns(3)
        col1.metric("バージョン", doc.metadata.get("format", "Unknown"))
        col2.metric("総ページ数", len(doc))
        col3.metric("容量", f"{len(file_bytes) / 1024:.1f} KB")

        # --- 1. ページサイズ確認 (mm) ---
        st.markdown("<div class='section-box'></div>", unsafe_allow_html=True)
        st.write("### 📐 ページサイズ確認 (mm)")
        p_sizes = []
        for i in range(len(doc)):
            page = doc[i]
            # 各ボックス（MediaBox, CropBox, TrimBox, ArtBox, BleedBox）
            def get_mm(rect):
                if rect:
                    return f"{rect.width * 25.4 / 72:.1f} x {rect.height * 25.4 / 72:.1f}"
                return "未設定"

            p_sizes.append({
                "P.": i + 1,
                "メディア(用紙)": get_mm(page.mediabox),
                "トリム(仕上がり)": get_mm(page.trimbox) if page.trimbox else get_mm(page.cropbox),
                "アート(内容)": get_mm(page.artbox),
                "ブリード(塗り足し)": get_mm(page.bleedbox)
            })
        st.dataframe(pd.DataFrame(p_sizes), use_container_width=True, height=200)

        # --- 2. 画像解析 ---
        st.markdown("<div class='section-box'></div>", unsafe_allow_html=True)
        st.write("### 🖼️ 画像解析")
        i_list = []
        for i, page in enumerate(doc):
            img_info_list = page.get_image_info(hashes=True)
            for img in img_info_list:
                cs = img.get("colorspace", 0)
                bpc = img.get("bpc", 8)
                if cs == 4: mode = "CMYK"
                elif cs == 3: mode = "RGB"
                elif cs == 1: mode = "モノクロ2階調" if bpc == 1 else "グレースケール"
                else: mode = f"不明({cs})"
                
                b = img["bbox"]
                wi, hi = (b[2]-b[0])/72, (b[3]-b[1])/72
                px_w, px_h = img["width"], img["height"]
                dpi = round(max(px_w/wi, px_h/hi)) if wi>0 else 0

                i_list.append({
                    "P.": i+1, "DPI": dpi, "モード": mode, "サイズ(px)": f"{px_w}x{px_h}"
                })
        if i_list:
            st.dataframe(pd.DataFrame(i_list), use_container_width=True, height=300)
        else:
            st.info("画像オブジェクトは見つかりませんでした。")

        # --- 3. フォント確認 ---
        st.markdown("<div class='section-box'></div>", unsafe_allow_html=True)
        st.write("### 🔤 フォント確認")
        f_list = [{"フォント名": f[3], "埋め込み": "✅ 済" if f[4] != 0 else "❌ 未"} for page in doc for f in page.get_fonts()]
        if f_list:
            st.dataframe(pd.DataFrame(f_list).drop_duplicates().reset_index(drop=True), use_container_width=True, height=300)
        else:
            st.info("フォント情報は見つかりませんでした。")

        doc.close()
    except Exception as e:
        st.error(f"解析中に問題が発生しました。")
else:
    st.markdown("<p style='text-align: center; font-weight: bold; color: #1e3a8a; padding: 40px;'>上の青い枠にPDFをドロップしてください</p>", unsafe_allow_html=True)
