import streamlit as st
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="E&Endeavor Slide Studio",
    page_icon="🎬",
    layout="wide"
)

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("⚙️ 設定")
    
    # API Key Configuration (Loaded from Secrets/Env)
    # Gemini API Key
    api_key = None
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
    except FileNotFoundError:
        pass
    
    if not api_key and "GEMINI_API_KEY" in os.environ:
        api_key = os.environ["GEMINI_API_KEY"]

    if not api_key:
        st.error("⚠️ システムエラー: APIキーが設定されていません。管理者に連絡してください。")

    # Pexels API Key
    pexels_api_key = None
    try:
        if "PEXELS_API_KEY" in st.secrets:
            pexels_api_key = st.secrets["PEXELS_API_KEY"]
    except FileNotFoundError:
        pass
    
    if not pexels_api_key and "PEXELS_API_KEY" in os.environ:
            pexels_api_key = os.environ["PEXELS_API_KEY"]
    
    st.divider()
    
    # Generation Settings
    font_option = st.selectbox("フォント選択", ["Noto Sans JP", "Hiragino Sans", "IPAGothic"], index=0)
    slide_count = st.number_input("スライド生成枚数", min_value=1, max_value=20, value=5, step=1)
    
    # Voice Selection (Edge TTS)
    voice_map = {
        "女性: 七海 (Nanami) - ニュース/標準": "ja-JP-NanamiNeural",
        "男性: 慶太 (Keita) - ナレーション/解説": "ja-JP-KeitaNeural"
    }
    voice_label = st.selectbox("ナレーター音声", list(voice_map.keys()), index=0)
    selected_voice = voice_map[voice_label]
    
    tone_option = st.selectbox("トーン＆マナー", ["フォーマル (Formal)", "カジュアル (Casual)", "エネルギッシュ (Energetic)"], index=0)

# --- Main Area ---
st.title("🎬 E&Endeavor Slide Studio")
st.markdown("テキストを入力すると、AIが「台本」「スライド」「音声」を自動生成し、動画に仕上げます。")

# Input Area
user_text = st.text_area("講義内容やテーマを入力してください", height=200, placeholder="例：AI技術の建設業界への応用について、初心者向けに解説してください。")

if st.button("構成案を生成 (Phase 1)", type="primary"):
    if not api_key:
        st.error("APIキーを設定してください。")
    elif not user_text:
        st.warning("テキストを入力してください。")
    else:
        # --- Gemini API Logic ---
        try:
            genai.configure(api_key=api_key)
            
            # Using Gemini 2.0 Flash (Retry logic added for 429 errors)
            model = genai.GenerativeModel('gemini-2.0-flash') 
            
            from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
            from google.api_core.exceptions import ResourceExhausted

            @retry(
                retry=retry_if_exception_type(ResourceExhausted),
                wait=wait_exponential(multiplier=2, min=4, max=60),
                stop=stop_after_attempt(5),
                reraise=True
            )
            def generate_with_retry(prompt):
                return model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(response_mime_type="application/json")
                )

            with st.spinner("AIが構成を思考中... (Gemini 2.0 Flash) \n※混雑時は少し時間がかかる場合があります"):
                
                # Prompt Engineering
                system_instruction = f"""
                あなたはプロのプレゼンテーションクリエイターです。
                以下の入力テキストに基づき、ビデオプレゼンテーション用のスライド構成を作成してください。
                
                【設定】
                - スライド枚数: {slide_count}枚程度
                - トーン: {tone_option}
                - 出力形式: JSONのみ (Markdownコードブロックなし)
                
                【JSON構造】
                {{
                  "theme": "プレゼンのテーマ",
                  "slides": [
                    {{
                      "slide_number": 1,
                      "title": "スライドのタイトル",
                      "bullet_points": ["箇条書きテキスト1", "箇条書きテキスト2", ...],
                      "script": "このスライドで読み上げるナレーション原稿 (日本語)",
                      "image_prompt_en": "High quality, photorealistic, cinematic lighting, [このスライドの背景画像を表す英語プロンプト]"
                    }}
                  ]
                }}
                
                【制約】
                - image_prompt_enは、「文字を含まない」「背景として使いやすい」高品質な画像を生成するための英語プロンプトにしてください。
                - scriptは、視聴者に語りかけるような自然な話し言葉にしてください。
                """
                
                try:
                    response = generate_with_retry(f"{system_instruction}\n\n【入力テキスト】\n{user_text}")
                    
                    # Parse JSON
                    result_json = json.loads(response.text)
                    
                    # Store in session state for Phase 2
                    st.session_state['plan'] = result_json
                    
                    st.success("構成案の生成が完了しました！")
                
                except ResourceExhausted:
                    st.error("アクセスが集中しており、生成できませんでした (429 Resource Exhausted)。\nしばらく時間を置いてから再度お試しください。")
                    st.stop()
                except Exception as e:
                    st.error(f"生成中にエラーが発生しました: {e}")
                    st.stop()
                    
        except Exception as e:
            st.error(f"初期化エラーが発生しました: {e}")

# --- Result Display ---
if 'plan' in st.session_state:
    plan = st.session_state['plan']
    
    st.divider()
    st.subheader(f"テーマ: {plan.get('theme', 'No Theme')}")
    
    # Display Slides
    for slide in plan.get('slides', []):
        with st.expander(f"Slide {slide['slide_number']}: {slide['title']}", expanded=True):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**📝 画面上のテキスト**")
                for point in slide['bullet_points']:
                    st.markdown(f"- {point}")
                
                st.markdown("**🗣️ ナレーション台本**")
                st.info(slide['script'])
                
            with col2:
                st.markdown("**🎨 背景画像プロンプト (英語)**")
                st.code(slide['image_prompt_en'], language="text")
    
    st.divider()
    
    # --- Phase 2: Image Generation & Overlay ---
    st.header("🖼️ Phase 2: 画像検索 & スライド合成 (Pexels)")
    
    # Check if we already have generated slides
    if 'generated_slides' not in st.session_state:
        st.session_state['generated_slides'] = {}
        
    if st.button("スライドを一括作成する (Pexels + Pillow)", type="primary"):
        # Import helper modules here to avoid top-level errors if files are missing
        try:
            from image_gen import generate_background_image
            from slide_renderer import draw_slide
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_slides = len(plan.get('slides', []))
            
            for index, slide in enumerate(plan.get('slides', [])):
                slide_num = slide['slide_number']
                
                # Check if already generated to avoid re-cost
                if slide_num in st.session_state['generated_slides']:
                    continue
                
                status_text.text(f"スライド {slide_num}/{total_slides} を生成中... (背景画像生成)")
                
                # 1. Generate Background
                try:
                    # Retry logic already handled inside image_gen or here if needed
                    # We rely on image_gen.py returning a PIL Image or fallback
                    bg_image = generate_background_image(slide['image_prompt_en'])
                    
                    status_text.text(f"スライド {slide_num}/{total_slides} を合成中... (文字入れ)")
                    
                    # 2. Text Overlay
                    final_slide = draw_slide(
                        background_image=bg_image,
                        title=slide['title'],
                        bullet_points=slide['bullet_points']
                    )
                    
                    # Store in session state
                    st.session_state['generated_slides'][slide_num] = final_slide
                    
                except Exception as e:
                    st.error(f"スライド {slide_num} の生成中にエラー: {e}")
                
                # Update progress
                progress_bar.progress((index + 1) / total_slides)
                
            status_text.text("全スライドの生成が完了しました！")
            st.success("画像生成・合成完了！")
            
        except ImportError:
            st.error("モジュールが見つかりません。image_gen.py と slide_renderer.py が存在することを確認してください。")
        except Exception as e:
            st.error(f"予期せぬエラー: {e}")

    # Display Generated Slides
    if st.session_state['generated_slides']:
        st.subheader("📺 生成されたスライドプレビュー")
        
        # Display in a grid
        cols = st.columns(2)
        slides = plan.get('slides', [])
        
        for i, slide in enumerate(slides):
            slide_num = slide['slide_number']
            if slide_num in st.session_state['generated_slides']:
                with cols[i % 2]:
                    st.image(
                        st.session_state['generated_slides'][slide_num], 
                        caption=f"Slide {slide_num}: {slide['title']}",
                        use_container_width=True
                    )
    
    if len(st.session_state['generated_slides']) > 0:
        st.divider()
        st.header("🎥 Phase 3: 動画書き出し (MP4)")
        
        if st.button("動画を生成・ダウンロードする (Python/MoviePy)", type="primary"):
            try:
                from audio_gen import generate_audio
                from video_gen import create_video
                import shutil
                
                # Setup Temp Directory
                temp_dir = "temp_assets"
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                os.makedirs(temp_dir)
                
                progress_bar_video = st.progress(0)
                status_text_video = st.empty()
                
                slides_data = []
                slides = plan.get('slides', [])
                total = len(slides)
                
                for i, slide in enumerate(slides):
                    slide_num = slide['slide_number']
                    status_text_video.text(f"スライド {slide_num}/{total} の素材を準備中... (音声合成)")
                    
                    if slide_num not in st.session_state['generated_slides']:
                        continue
                        
                    # 1. Save Image
                    img = st.session_state['generated_slides'][slide_num]
                    img_path = os.path.join(temp_dir, f"slide_{slide_num}.png")
                    img.save(img_path)
                    
                    # 2. Generate Audio
                    audio_path = os.path.join(temp_dir, f"slide_{slide_num}.mp3")
                    # Use formatted script
                    script = slide['script']
                    if not generate_audio(script, audio_path, voice=selected_voice):
                        st.error(f"音声生成に失敗しました: Slide {slide_num}")
                        st.stop()
                        
                    slides_data.append({
                        "image_path": img_path,
                        "audio_path": audio_path
                    })
                    
                    progress_bar_video.progress((i + 0.5) / total)
                
                status_text_video.text("動画をレンダリング中... (これには数分かかる場合があります)")
                
                # 3. Create Video
                output_video_path = "final_presentation.mp4"
                result_path = create_video(slides_data, output_video_path)
                
                progress_bar_video.progress(1.0)
                
                if result_path and os.path.exists(result_path):
                    status_text_video.text("動画完成！")
                    st.success("動画の生成が完了しました！")
                    
                    # Display Video
                    st.video(result_path)
                    
                    # Download Button
                    with open(result_path, "rb") as file:
                        btn = st.download_button(
                            label="MP4動画をダウンロード",
                            data=file,
                            file_name="presentation.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("動画ファイルの生成に失敗しました。")
                    
            except ImportError as e:
                st.error(f"必要なライブラリが見つかりません: {e}")
            except Exception as e:
                st.error(f"動画生成エラー: {e}")
                import traceback
                st.code(traceback.format_exc())
