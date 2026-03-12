import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

# ページ設定（指定サイトのようなワイドレイアウト）
st.set_page_config(page_title="PDF解析ツール", layout="wide")

# カスタムCSSでデザインを調整
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_stdio=True)

# --- サイドバー設定 ---
with st.sidebar:
    st.title("⚙️ 設定・操作")
    st.write("PDFをアップロードして解析を開始します。")
    
    # ファイルアップローダーをサイドバーに配置
    uploaded_file = st.file_uploader("PDFファイルをドロップ", type="pdf")
    
    st.divider()
    st.info("""
    **解析項目:**
    - PDFバージョン
    - フォント埋め込み状況
    - 画像解像度 (DPI)
    - カラーモード
    """)

# --- メインエリア ---
st.title("📄 PDF内部構造エンジン")

if uploaded_file is not None:
    # PDFをメモリ上で開く
    file_bytes = uploaded_file.read()
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    # --- 基本情報の表示 (横並びのカード形式) ---
    st.subheader("基本情報")
    col1, col2, col3 = st.columns(3)
    # 前回の修正を適用：metadataからバージョン取得
    pdf_version = doc.metadata.get("format", "Unknown")
    col1.metric("PDFバージョン", pdf_version)
    col2.metric("総ページ数", len(doc))
    col3.metric("サイズ", f"{len(file_bytes) / 1024:.1f} KB")

    # タブを使って情報を整理（サイドバーのあるサイトでよく使われる形式）
    tab1, tab2 = st.tabs(["🔤 フォント解析", "🖼️ 画像解析"])

    with tab1:
        all_fonts = []
        for page in doc:
            for f in page.get_fonts():
                font_info = {"フォント名": f[3], "埋め込み": "✅ 埋込済" if f[4] != 0 else "❌ 未埋込"}
                if font_info not in all_fonts:
                    all_fonts.append(font_info)
        
        if all_fonts:
            st.table(pd.DataFrame(all_fonts))
        else:
            st.info("フォント情報が見つかりませんでした。")

    with tab2:
        img_data = []
        for page_index in range(len(doc)):
            page = doc[page_index]
            for img in page.get_image_info(hashes=True):
                bbox = img["bbox"]
                width_inch = (bbox[2] - bbox[0]) / 72
                height_inch = (bbox[3] - bbox[1]) / 72
                
                dpi_w = img["width"] / width_inch if width_inch > 0 else 0
                dpi_h = img["height"] / height_inch if height_inch > 0 else 0
                
                img_data.append({
                    "ページ": page_index + 1,
                    "幅(px)": img["width"],
                    "高さ(px)": img["height"],
                    "解像度(DPI)": round(max(dpi_w, dpi_h)),
                    "カラーモード": img.get("colorspace", "N/A")
                })

        if img_data:
            df_img = pd.DataFrame(img_data)
            # 300dpi未満を赤くハイライト
            st.dataframe(
                df_img.style.highlight_between(left=0, right=299, subset=["解像度(DPI)"], color="#ff4b4b44"),
                use_container_width=True
            )
            st.caption("※解像度(DPI)が300未満の行をハイライトしています。")
        else:
            st.info("画像が含まれていません。")

    doc.close()
else:
    # ファイルがアップロードされていない時の表示
    st.warning("左側のサイドバーからPDFファイルをアップロードしてください。")
