import streamlit as st
import pdfplumber
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="日報サイネージくん", layout="centered")

st.title("📟 日報サイネージ生成ツール")
st.info("PDFを読み取って、サイネージに載せたい項目をポチポチ選んでね。")

# --- ファイル読み込み ---
try:
    base_image = Image.open("base_design.png")
except:
    base_image = Image.new('RGB', (1920, 1080), color=(40, 44, 52))

# --- PDF解析 ---
uploaded_file = st.file_uploader("日報PDFをアップロード", type="pdf")

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        # 1ページ目の表を抽出
        table = pdf.pages[0].extract_table()
        if table:
            # データの整形（空行を除外）
            data = [row for row in table if any(row)]
            header = data[0]
            rows = data[1:]
        else:
            st.error("PDFから表が見つからなかったよ…！")
            st.stop()

    st.subheader("📝 どの作業を画像に載せる？")
    selected_rows = []
    
    # 選択画面をチェックボックスで作成
    for i, row in enumerate(rows):
        # 「Room - 作品名 - 技術者」をラベルにする
        label = f"【{row[0]}】 {row[1]} （{row[4]}）"
        if st.checkbox(label, key=f"row_{i}"):
            selected_rows.append(row)

    # --- 画像生成 ---
    if st.button("🚀 画像を生成する"):
        if not selected_rows:
            st.warning("項目を選んでね！")
        else:
            canvas = base_image.copy()
            draw = ImageDraw.Draw(canvas)
            
            # フォント設定（同じフォルダに font.ttf を置いてね）
            try:
                font = ImageFont.truetype("font.ttf", 45)
                title_font = ImageFont.truetype("font.ttf", 60)
            except:
                font = ImageFont.load_default()
                st.warning("指定のフォントが見つからないからデフォルトで書くね。")

            # 文字を書く位置の指定（座標は自分の画像に合わせて調整して！）
            x, y = 150, 350
            draw.text((150, 250), "本日の作業スケジュール", font=title_font, fill=(255, 255, 255))
            
            for row in selected_rows:
                # [部屋] 作品名 / 担当者
                text = f"[{row[0]}]  {row[1]}   /   {row[4]}"
                draw.text((x, y), text, font=font, fill=(255, 255, 255))
                y += 90 # 行間
            
            # プレビュー表示
            st.image(canvas, use_container_width=True)
            
            # ダウンロード
            buf = io.BytesIO()
            canvas.save(buf, format="PNG")
            st.download_button("画像を保存する", buf.getvalue(), "signage.png", "image/png")