import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

# ページ設定：ワイドレイアウトでカレンダー確認ツールのような広さを確保
st.set_page_config(page_title="PDF解析ツール", layout="wide")

# カスタムCSS：背景色やカードのデザインを調整
st.markdown("""
    <style>
    /* メイン背景色の変更 */
    .stApp {
        background-color: #f8f9fa;
    }
    /* メトリック（数字表示）のカードデザイン */
    [data-testid="stMetricValue"] {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }
    /* サイドバーのスタイル */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #ddd;
    }
    </style>
    """, unsafe_allow_html=True)

# --- サイドバー (操作パネル) ---
with st.sidebar:
    st.title("⚙️ ツール操作")
    st.write("PDFをここにドロップして解析を開始します。")
    
    # ファイルアップローダー
    uploaded_file = st.file_uploader("PDFファイルをアップロード", type="pdf")
    
    st.divider()
    st.markdown("""
    ### 📝 解析内容
    - **PDFバージョン**の確認
    - **フォント埋め込み**の有無
    - **画像解像度(DPI)**の計算
    - **カラーモード**の抽出
    """)
    
    st.caption("v1.0.0 | Produced by Your Engine")

# --- メインコンテンツエリア ---
st.title("📄 PDF内部構造エンジン (Analyzer)")

if uploaded_file is not None:
    # PDFをメモリ上で読み込み
    file_bytes = uploaded_file.read()
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    # --- ステータス概要 (3カラム表示) ---
    st.subheader("基本プロパティ")
    col1, col2, col3 = st.columns(3)
    
    # バージョン情報の取得 (PyMuPDFの仕様変更に対応)
    pdf_version = doc.metadata.get("format", "Unknown")
    
    col1.metric("PDFバージョン", pdf_version)
    col2.metric("総ページ数", f"{len(doc)} ページ")
    col3.metric("ファイル容量", f"{len(file_bytes) / 1024:.1f} KB")

    st.divider()

    # --- 詳細解析タブ ---
    tab1, tab2 = st.tabs(["🔤 フォント・埋め込み確認", "🖼️ 画像・解像度/カラーモード"])

    with tab1:
        st.write("### 使用フォント一覧")
        all_fonts = []
        for page in doc:
            for f in page.get_fonts():
                # f[3]はフォント名, f[4]は埋め込みフラグ
                font_info = {
                    "フォント名": f[3], 
                    "埋め込み状態": "✅ 埋込済" if f[4] != 0 else "❌ 未埋込"
                }
                if font_info not in all_fonts:
                    all_fonts.append(font_info)
        
        if all_fonts:
            st.table(pd.DataFrame(all_fonts))
        else:
            st.info("このPDFにはテキスト（フォント情報）が含まれていません。")

    with tab2:
        st.write("### 配置画像詳細")
        img_data = []
        for page_index in range(len(doc)):
            page = doc[page_index]
            image_info = page.get_image_info(hashes=True)
            
            for img in image_info:
                # 座標(bbox)から配置インチサイズを計算
                bbox = img["bbox"]
                width_inch = (bbox[2] - bbox[0]) / 72
                height_inch = (bbox[3] - bbox[1]) / 72
                
                # DPIの算出 (画素数 / インチ)
                dpi_w = img["width"] / width_inch if width_inch > 0 else 0
                dpi_h = img["height"] / height_inch if height_inch > 0 else 0
                
                img_data.append({
                    "ページ": page_index + 1,
                    "幅(px)": img["width"],
                    "高さ(px)": img["height"],
                    "実効解像度(DPI)": round(max(dpi_w, dpi_h)),
                    "カラーモード": img.get("colorspace", "N/A"),
                    "BPC": img.get("bpc", 8)
                })

        if img_data:
            df_img = pd.DataFrame(img_data)
            # 300dpi未満をハイライト表示
            st.dataframe(
                df_img.style.highlight_between(left=0, right=299, subset=["実効解像度(DPI)"], color="#ff4b4b44"),
                use_container_width=True
            )
            st.info("💡 **DPIが300未満**の画像は赤くハイライトされています。印刷用途ではご注意ください。")
        else:
            st.info("このPDFには画像が含まれていません。")

    doc.close()
else:
    # 未アップロード時の案内
    st.info("👈 左側のサイドバーにPDFファイルをドラッグ＆ドロップしてください。")
    st.markdown("""
    ---
    ### 使い方
    1. 左のメニューからPDFを選択
    2. 自動的に解析が始まります
    3. 各タブで詳細な技術情報を確認できます
    """)
