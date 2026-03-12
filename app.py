import streamlit as st
import fitz  # PyMuPDF
import pandas as pd

# ページ設定：スッキリ見せるため中央寄せのレイアウト
st.set_page_config(page_title="PDF解析ツール", layout="centered")

# 日本の業務ツールらしい「白・薄灰色・濃紺」の配色に固定
st.markdown("""
    <style>
    /* 全体の背景を薄いグレーに */
    .stApp {
        background-color: #f5f7f9 !important;
    }
    
    /* 中央のコンテンツエリアを白いカードに見せる */
    .main .block-container {
        background-color: #ffffff !important;
        color: #333333 !important;
        padding: 50px !important;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-top: 30px;
    }

    /* タイトルや見出しを読みやすい濃紺に */
    h1, h2, h3 {
        color: #1e3a8a !important;
        font-family: "Helvetica Neue", Arial, "Hiragino Kaku Gothic ProN", "Hiragino Sans", Meiryo, sans-serif;
    }

    /* 全ての文字を濃いグレー（黒に近い）で固定 */
    p, span, label, th, td, .stMarkdown {
        color: #333333 !important;
    }

    /* ファイルアップローダーの枠をシンプルに */
    [data-testid="stFileUploader"] {
        border: 2px dashed #cbd5e1 !important;
        background-color: #f8fafc !important;
    }

    /* 表のヘッダーを青背景・白文字に */
    thead tr th {
        background-color: #1e3a8a !important;
        color: #ffffff !important;
    }

    /* メトリック（数字）の装飾 */
    [data-testid="stMetricValue"] {
        color: #1e3a8a !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ロゴ・タイトル ---
st.markdown("<h1 style='text-align: center;'>PDF解析ツール</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b;'>PDFのバージョン、フォント、画像の解像度をチェックします</p>", unsafe_allow_html=True)
st.write("")

# --- ファイル選択 ---
uploaded_file = st.file_uploader("PDFファイルをここにドラッグ＆ドロップしてください", type="pdf", label_visibility="collapsed")

if uploaded_file is not None:
    try:
        file_bytes = uploaded_file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")

        # --- 基本情報エリア ---
        st.write("### 📋 基本情報")
        col1, col2, col3 = st.columns(3)
        
        # 安全なバージョン取得方法
        pdf_version = doc.metadata.get("format", "Unknown")
        
        col1.metric("バージョン", pdf_version)
        col2.metric("総ページ数", f"{len(doc)}")
        col3.metric("サイズ", f"{len(file_bytes) / 1024:.1f} KB")

        st.write("---")

        # --- 詳細解析（タブでスッキリ整理） ---
        tab1, tab2 = st.tabs(["🔤 フォント確認", "🖼️ 画像解像度チェック"])

        with tab1:
            st.write("#### 使用フォント一覧")
            font_list = []
            for page in doc:
                for f in page.get_fonts():
                    font_list.append({
                        "フォント名": f[3], 
                        "埋め込み状態": "✅ 埋込済" if f[4] != 0 else "❌ 未埋込"
                    })
            if font_list:
                df_font = pd.DataFrame(font_list).drop_duplicates()
                st.table(df_font)
            else:
                st.info("テキスト情報が含まれていないPDFです。")

        with tab2:
            st.write("#### 配置画像の状態")
            img_list = []
            for page_index in range(len(doc)):
                page = doc[page_index]
                for img in page.get_image_info(hashes=True):
                    # DPIの計算
                    bbox = img["bbox"]
                    w_inch = (bbox[2] - bbox[0]) / 72
                    h_inch = (bbox[3] - bbox[1]) / 72
                    dpi = round(max(img["width"] / w_inch, img["height"] / h_inch)) if w_inch > 0 else 0
                    
                    img_list.append({
                        "ページ": page_index + 1,
                        "解像度(DPI)": dpi,
                        "カラーモード": img.get("colorspace", "N/A"),
                        "判定": "OK" if dpi >= 300 else "⚠️ 低解像度"
                    })
            
            if img_list:
                df_img = pd.DataFrame(img_list)
                # 読みやすいデータフレーム表示
                st.dataframe(df_img, use_container_width=True)
                st.caption("※DPIが300未満の場合は「⚠️ 低解像度」と表示されます。")
            else:
                st.info("画像が含まれていないPDFです。")
        
        doc.close()

    except Exception as e:
        st.error(f"エラーが発生しました。ファイルを確認してください。")
else:
    # ファイルがない時の案内
    st.markdown("<div style='text-align: center; padding: 100px 0; color: #94a3b8;'>解析するPDFを選択してください</div>", unsafe_allow_html=True)
