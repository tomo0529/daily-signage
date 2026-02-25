import streamlit as st
import pdfplumber
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

# --- ページ設定 ---
st.set_page_config(page_title="日報サイネージ生成", layout="wide")

st.title("🚀 日報サイネージ生成ツール")

# --- 1. 背景画像とフォントの準備（読み込めなくても止まらないようにする） ---
font_main = font_title = font_date = ImageFont.load_default()
base_image = Image.new('RGBA', (1920, 1080), (255, 255, 255, 255))

try:
    base_image = Image.open("base_design.png").convert("RGBA")
    font_path = "NotoSansJP-Regular.ttf"
    font_main = ImageFont.truetype(font_path, 38)
    font_title = ImageFont.truetype(font_path, 60)
    font_date = ImageFont.truetype(font_path, 45)
except Exception as e:
    st.warning(f"⚠️ 画像かフォントが読み込めませんでした。GitHubのファイル名を確認してね！: {e}")

# --- 2. カレンダーと日付設定 ---
st.subheader("📅 日付を選択")
selected_date = st.date_input("サイネージに表示する日付", datetime.now())
wd_jp = ["月", "火", "水", "木", "金", "土", "日"]
date_str = selected_date.strftime(f"%m月%d日({wd_jp[selected_date.weekday()]})")

# --- 3. PDF解析（安全に1行ずつチェック） ---
def parse_nippo(file):
    rows = []
    try:
        with pdfplumber.open(file) as pdf:
            table = pdf.pages[0].extract_table()
            if table:
                for row in table:
                    # Noneを空文字に変換
                    r = [str(item) if item else "" for item in row]
                    # 部屋名が入っていて、作品名がある程度長い「黒文字っぽい行」だけを抽出
                    if (("ED-" in r[0]) or ("MA-" in r[0])) and len(r[1]) > 1:
                        rows.append(r)
    except:
        pass
    return rows

uploaded_pdf = st.file_uploader("日報PDFをアップロード", type="pdf")

if uploaded_pdf:
    valid_rows = parse_nippo(uploaded_pdf)
    
    if valid_rows:
        st.write(f"プレビューの日付: **{date_str}**")
        st.subheader("📝 掲載する作業を選択")

        # --- 全選択・全解除ボタン（Session Stateを安全に操作） ---
        col_btn1, col_btn2, _ = st.columns([1, 1, 5])
        if col_btn1.button("✅ 全選択"):
            for i in range(len(valid_rows)): st.session_state[f"check_{i}"] = True
        if col_btn2.button("❌ 全解除"):
            for i in range(len(valid_rows)): st.session_state[f"check_{i}"] = False

        # --- チェックボックスの表示 ---
        selected_rows = []
        cols = st.columns(2)
        for i, row in enumerate(valid_rows):
            key = f"check_{i}"
            if key not in st.session_state: st.session_state[key] = False
            
            # 安全にラベルを作成
            room_name = row[0] if len(row) > 0 else "不明"
            work_name = row[1] if len(row) > 1 else "なし"
            
            if cols[i % 2].checkbox(f"【{room_name}】 {work_name}", key=key):
                selected_rows.append(row)

        # --- 4. 画像生成 ---
        if st.button("🎨 サイネージ画像を生成"):
            if not selected_rows:
                st.error("作業を1つ以上選んでね！")
            else:
                # ✍️ 座標設定（ここで定義すればNameErrorは出ない）
                start_x = 220
                start_y = 380
                line_height = 85
                date_pos = (220, 180) # マップ上の日付の位置
                text_color = (0, 0, 0, 255) # 黒文字
                
                # 描画準備
                txt_layer = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(txt_layer)
                
                # 日付書き込み
                draw.text(date_pos, date_str, font=font_date, fill=text_color)
                
                # タイトル書き込み
                draw.text((start_x, start_y - 140), "TODAY'S SCHEDULE", font=font_title, fill=text_color)
                
                # 各行を安全に書き込み
                for i, row in enumerate(selected_rows):
                    current_y = start_y + (i * line_height)
                    
                    # データの数に関わらずエラーにならないように取得
                    r_room = row[0] if len(row) > 0 else "?"
                    r_title = row[1] if len(row) > 1 else "---"
                    r_staff = row[4] if len(row) > 4 else "---"
                    
                    display_text = f"● [{r_room}] {r_title}　/　{r_staff}"
                    draw.text((start_x, current_y), display_text, font=font_main, fill=text_color)
                
                # 合成と表示
                combined = Image.alpha_composite(base_image, txt_layer)
                final_img = combined.convert("RGB")
                
                st.image(final_img, caption="生成完了！", use_container_width=True)
                
                # ダウンロード準備
                buf = io.BytesIO()
                final_img.save(buf, format="PNG")
                st.download_button("💾 画像をダウンロード", buf.getvalue(), f"signage_{selected_date}.png", "image/png")
