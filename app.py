import streamlit as st
import pdfplumber
from PIL import Image, ImageDraw, ImageFont
import io

# --- ページ設定 ---
st.set_page_config(page_title="日報サイネージ生成", layout="wide")

st.title("🚀 日報サイネージ生成ツール")

# --- 1. 背景画像とフォントの準備 ---
font_main = None
font_title = None
base_image = None

try:
    base_image = Image.open("base_design.png").convert("RGBA")
    font_path = "NotoSansJP-Regular.ttf" 
    font_main = ImageFont.truetype(font_path, 40)
    font_title = ImageFont.truetype(font_path, 65)
except Exception as e:
    st.error(f"ファイルの読み込みに失敗したよ。GitHubのファイル名を確認してね！")
    font_main = ImageFont.load_default()
    font_title = ImageFont.load_default()
    if base_image is None:
        base_image = Image.new('RGBA', (1920, 1080), (40, 44, 52, 255))

# --- 2. PDF解析ロジック ---
def parse_nippo(file):
    try:
        with pdfplumber.open(file) as pdf:
            table = pdf.pages[0].extract_table()
            if not table: return []
            clean_data = [row for row in table if row and any(row)]
            return clean_data[1:]
    except:
        return []

# --- 3. メイン画面のUI ---
uploaded_pdf = st.file_uploader("日報PDFをここにドロップ", type="pdf")

if uploaded_pdf:
    rows = parse_nippo(uploaded_pdf)
    
    if rows:
        st.subheader("📝 反映させる項目を選択")
        selected_rows = []
        cols = st.columns(2)
        for i, row in enumerate(rows):
            room = row[0] if len(row) > 0 else "不明"
            title = row[1] if len(row) > 1 else "なし"
            label = f"【{room}】 {title}"
            if cols[i % 2].checkbox(label, key=f"check_{i}"):
                selected_rows.append(row)

        # --- 4. 画像生成ボタン ---
        if st.button("🎨 サイネージ画像を生成する"):
            if not selected_rows:
                st.error("項目を1つ以上選んでね！")
            else:
                # ✍️ ここで座標を定義（絶対にエラーが出ないようにボタンの直後に置いたよ！）
                start_x = 220
                start_y = 380
                line_height = 90
                
                # 編集用の透明レイヤーを作成
                txt_layer = Image.new("RGBA", base_image.size, (255, 255, 255, 0))
                draw = ImageDraw.Draw(txt_layer)
                
                # タイトル（TODAY'S SCHEDULE）
                draw.text((start_x, start_y - 140), "TODAY'S SCHEDULE", font=font_title, fill=(255, 255, 255, 255))
                
                # 選択項目の書き込み
                for i, row in enumerate(selected_rows):
                    current_y = start_y + (i * line_height)
                    room = row[0] if len(row) > 0 else "?"
                    title = row[1] if len(row) > 1 else "---"
                    staff = row[4] if len(row) > 4 else "---"
                    
                    display_text = f"● [{room}]  {title}　/　{staff}"
                    draw.text((start_x, current_y), display_text, font=font_main, fill=(255, 255, 255, 255))
                
                # 合成
                combined = Image.alpha_composite(base_image, txt_layer)
                final_img = combined.convert("RGB")
                
                st.image(final_img, caption="生成完了！", use_container_width=True)
                
                buf = io.BytesIO()
