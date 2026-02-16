from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import textwrap
import os

def load_japanese_font(size):
    """
    Tries to load a standard Japanese font available on Windows.
    """
    # Common Windows Japanese fonts
    font_candidates = [
        # Linux / Streamlit Cloud (Debian)
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
        # Windows
        "meiryo.ttc",       # Meiryo
        "msgothic.ttc",     # MS Gothic
        "yugothb.ttc",      # Yu Gothic Bold
        "YuGothB.ttc",
        "arial.ttf"         # Fallback
    ]
    
    for font_name in font_candidates:
        try:
            return ImageFont.truetype(font_name, size)
        except OSError:
            continue
            
    # Absolute fallback to default if nothing works
    return ImageFont.load_default()

def draw_slide(background_image, title, bullet_points):
    """
    Composes the final slide image with a Split Layout.
    Left 40%: Dark Text Area
    Right 60%: Full Image Area
    """
    target_size = (1920, 1080)
    
    # 1. Create Base Canvas (Dark Background for text area)
    # Using a dark elegant color (e.g., Dark Slate/Charcoal)
    canvas = Image.new('RGB', target_size, (30, 33, 40)) 
    
    # 2. Paste the AI Generated Image on the Right side
    # Resize image to fit height, maintain aspect ratio or crop to width
    # Target area for image: 1152x1080 (60% width)
    img_width = int(target_size[0] * 0.6)
    img_height = target_size[1]
    
    # Resize/Crop background image to fill the right side
    # Calculate aspect ratios
    bg_ratio = background_image.width / background_image.height
    target_ratio = img_width / img_height
    
    if bg_ratio > target_ratio:
        # Image is wider, crop width
        new_height = img_height
        new_width = int(new_height * bg_ratio)
        resized_bg = background_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        left_crop = (new_width - img_width) // 2
        cropped_bg = resized_bg.crop((left_crop, 0, left_crop + img_width, new_height))
    else:
        # Image is taller, crop height
        new_width = img_width
        new_height = int(new_width / bg_ratio)
        resized_bg = background_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        top_crop = (new_height - img_height) // 2
        cropped_bg = resized_bg.crop((0, top_crop, new_width, top_crop + img_height))
    
    # Paste formatted image to the right side
    canvas.paste(cropped_bg, (target_size[0] - img_width, 0))
    
    # 3. Draw Text on the Left Side
    draw = ImageDraw.Draw(canvas)
    
    # Fonts
    # Fonts
    # Adjusted sizes for better visibility
    title_font = load_japanese_font(90)  # Was 70
    body_font = load_japanese_font(60)   # Was 45
    
    # Margins for text area
    text_area_width = target_size[0] - img_width
    margin_x = 80
    current_y = 150
    
    # Draw Title
    # Wrap title if needed
    title_lines = textwrap.wrap(title, width=12) # narrower for left column
    for line in title_lines:
        draw.text((margin_x, current_y), line, font=title_font, fill="white")
        current_y += 90
        
    # Draw Separator
    current_y += 30
    draw.line([(margin_x, current_y), (text_area_width - 50, current_y)], fill="#4da6ff", width=4) # Accent color
    current_y += 60
    
    # Draw Bullet Points
    line_spacing = 70
    
    for point in bullet_points:
        # Wrap text
        wrapped_lines = textwrap.wrap(point, width=18)
        
        for i, line in enumerate(wrapped_lines):
            prefix = "• " if i == 0 else "  "
            draw.text((margin_x, current_y), f"{prefix}{line}", font=body_font, fill="#e0e0e0")
            current_y += line_spacing
        
        current_y += 20 # Extra space between points
            
    return canvas
