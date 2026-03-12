import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

st.set_page_config(page_title="PDF Insider", layout="wide")

st.title("📄 PDF内部構造エンジン (Analyzer)")
st.write("PDFをドロップして、バージョン、フォント、画像の解像度を解析します。")

# ファイルアップローダー
uploaded_file = st.file_uploader("PDFファイルをアップロードしてください", type="pdf")

if uploaded_file is not None:
    # PDFをメモリ上で開く
    file_bytes = uploaded_file.read()
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    # --- 基本情報の表示 ---
    st.subheader("基本情報")
    col1, col2, col3 = st.columns(3)
    col1.metric("PDFバージョン", doc.metadata.get("format", "Unknown"))
    col2.metric("総ページ数", len(doc))
    col3.metric("ファイルサイズ", f"{len(file_bytes) / 1024:.1f} KB")

    # --- フォント解析 ---
    st.subheader("使用フォント")
    all_fonts = []
    for page in doc:
        for f in page.get_fonts():
            # f[3]はフォント名, f[4]は埋め込みフラグ(0以外なら埋め込み)
            font_info = {"Name": f[3], "Embedded": "✅" if f[4] != 0 else "❌"}
            if font_info not in all_fonts:
                all_fonts.append(font_info)
    
    if all_fonts:
        st.table(pd.DataFrame(all_fonts))
    else:
        st.info("フォント情報が見つかりませんでした。")

    # --- 画像解析 (解像度・カラーモード) ---
    st.subheader("画像解析 (DPI & Colorspace)")
    img_data = []
    
    for page_index in range(len(doc)):
        page = doc[page_index]
        # ページ内の画像配置情報を取得
        image_info = page.get_image_info(hashes=True)
        
        for img in image_info:
            # DPI計算: 画素数 / (配置サイズ / 72)
            # PDFの基本単位は1/72インチ
            bbox = img["bbox"]
            width_inch = (bbox[2] - bbox[0]) / 72
            height_inch = (bbox[3] - bbox[1]) / 72
            
            dpi_w = img["width"] / width_inch if width_inch > 0 else 0
            dpi_h = img["height"] / height_inch if height_inch > 0 else 0
            
            img_data.append({
                "Page": page_index + 1,
                "Width(px)": img["width"],
                "Height(px)": img["height"],
                "DPI (Max)": round(max(dpi_w, dpi_h)),
                "Colorspace": img.get("colorspace", "N/A"),
                "BPC (Bit)": img.get("bpc", 8)
            })

    if img_data:
        df_img = pd.DataFrame(img_data)
        # 低解像度（300dpi未満）にハイライトを入れる例
        st.dataframe(df_img.style.highlight_between(left=0, right=299, subset=["DPI (Max)"], color="#ff4b4b44"))
        st.caption("※DPIが300未満の行を赤くハイライトしています。")
    else:
        st.info("このPDFには画像が含まれていません。")

    doc.close()
