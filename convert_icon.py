from PIL import Image
import os

source_path = "C:/Users/makist_code_04/.gemini/antigravity/brain/207bc033-8544-4d76-99b5-908bc28446ef/typing_service_icon_1770979429014.png"
temp_png_path = "frontend/public/icons/real_icon.png"

try:
    img = Image.open(source_path)
    img.save(temp_png_path, "PNG")
    print(f"Successfully converted {source_path} to {temp_png_path}")
except Exception as e:
    print(f"Error converting image: {e}")
