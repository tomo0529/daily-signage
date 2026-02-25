import streamlit as st
import pdfplumber
from PIL import Image, ImageDraw, ImageFont
import io

# --- ページ設定 ---
st.set_page_config(page_title="日報サイネージ生成", layout="wide")

st.title("🚀 日報サイネージ生成ツール")
st.write("PDFを読み取って、サイネージに載せる項目を選ぼう。")

# --- 1. 背景画像とフォントの準備 ---
# エラー防止のために、あらかじめデフォルトを空で定義しておく
font_main = None
font_title = None
base_image = None

try:
    # GitHubにアップした背景とフォントを読み込む
    base_image = Image.open("base_design.png").convert("RGBA")
    
    # 指定されたフォント名に合わせているよ
    font_path = "NotoSansJP-Regular.ttf" 
    font_main = ImageFont.truetype(font_path, 40)
    font_title = ImageFont.truetype(font_path, 65)
except Exception as e:
    st.error(f"ファイルの読み込みに失敗したよ。GitHubに 'base_design.png' と 'NotoSansJP-Regular.ttf' があるか確認してね！")
    st.info(f"エラー詳細: {e}")
    # ファイルがない場合でも動くように標準フォントを代入
    font_main = ImageFont.load_default()
    font_title = ImageFont.load_default()
    if base_image is None:
        base_image = Image.new('RGBA', (1920, 1080), (40, 44, 52, 255))

# --- 2. PDF解析ロジック ---
def parse_nippo(file):
    try:
        with pdfplumber.open(file) as pdf:
            table = pdf.pages[0].extract_table()
            if not table:
                return []
            # 空行を除去して、最低限データが入っている行だけ抽出
            clean_data = [row for row in table if row and any(row)]
            return clean_data[1:] # ヘッダー（1行目）を除いて返す
    except Exception as e:
        st.error(f"PDFの解析でエラーが出たよ: {e}")
        return []

# --- 3. メイン画面のUI ---
uploaded_pdf = st.file_uploader("日報PDFをここにドロップ", type="pdf")

if uploaded_pdf:
    rows = parse_nippo(uploaded_pdf)
    
    if not rows:
        st.warning("PDFから作業データが見つからなかったよ。フォーマットが合っているか確認してみて。")
    else:
        st.subheader("📝 反映させる項目を選択")
        selected_rows = []
        
        # 選択用UIを2列で表示
        cols = st.columns(2)
        for i, row in enumerate(rows):
            # PDFの列構造に合わせてラベルを作成（Room, 作品名, 担当など）
            # インデックスがズレてもエラーにならないように安全に取得
            room = row[0] if len(row) > 0 else "不明"
            title = row[1] if len(row) > 1 else "なし"
            staff = row[4] if len(row) > 4 else "未定"
            
            label = f"【{room}】 {title} （{staff}）"
            if cols[i % 2].checkbox(label, key=f"check_{i}"):
                selected_rows.append(row)

        # --- 4. 画像生成ボタン ---
        if st.button("🎨 サイネージ画像を生成する"):
            if not selected_rows:
                st.error("項目を1つ以上選んでね！")
            else:
                # 編集用の透明レイヤーを作成
                txt_layer = Image.new("RGBA", base_image.size, (255, 255, 255, 0))
                draw = ImageDraw.Draw(txt_layer)
                
                # --- レイアウト設定（ここをいじれば文字位置が変わる！） ---
                start_x
