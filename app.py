import streamlit as st
import pdfplumber
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

# --- ページ設定 ---
st.set_page_config(page_title="日報サイネージ生成", layout="wide")

st.title("🚀 日報サイネージ生成ツール")

# --- 1. 背景画像とフォントの準備 ---
try:
    base_image = Image.open("base_design.png").convert("RGBA")
    font_path = "NotoSansJP-Regular.ttf" 
    font_main = ImageFont.truetype(font_path, 38)
    font_title = ImageFont.truetype(font_path, 60)
    font_date = ImageFont.truetype(font_path, 45) # 日付用のフォントサイズ
except Exception as e:
    st.error("ファイルが読み込めませんでした。GitHubのファイル名を確認してね。")
    st.stop()

# --- 2. PDF解析ロジック ---
def parse_nippo(file):
    valid_rows = []
    try:
        with pdfplumber.open(file) as pdf:
            table = pdf.pages[0].extract_table()
            if not table: return []
            for row in table:
                room = str(row[0]) if row[0] else ""
                title = str(row[1]) if row[1] else ""
                # メインの作業行（ED-かMA-が含まれる黒文字部分）だけを抽出
                if ("ED-" in room or "MA-" in room) and len(title) > 1:
                    valid_rows.append(row)
        return valid_rows
    except:
        return []

# --- 3. メイン画面のUI ---
# カレンダーで日付を選択
st.subheader("📅 日付を選択")
selected_date = st.date_input("サイネージに表示する日付を選んでね", datetime.now())

# 曜日の日本語変換用
wd_jp = ["月", "火", "水", "木", "金", "土", "日"]
date_str = selected_date.strftime(f"%m月%d日({wd_jp[selected_date.weekday()]})")

uploaded_pdf = st.file_uploader("日報PDFをアップロード", type="pdf")

if uploaded_pdf:
    rows = parse_nippo(uploaded_pdf)
    
    if rows:
        st.write(f"表示形式のプレビュー: **{date_str}**")
        st.subheader("📝 掲載する作業を選択")

        # 全選択・全解除ボタン
        col_btn1, col_btn2, _ = st.columns([1, 1, 5])
        if col_btn1.button("✅ 全選択"):
            for i in range(len(rows)): st.
