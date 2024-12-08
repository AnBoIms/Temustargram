import os
from PIL import Image, ImageDraw, ImageFont

# 회색 배경 생성 및 한글 텍스트 추가 함수
def create_gray_image_with_text(size, output_path, text, font_path):
    gray_image = Image.new("RGB", size, (128, 128, 128)) 
    
    draw = ImageDraw.Draw(gray_image)
    try:
        font_size = min(size[0], size[1]) // 1 
        while font_size > 0:
            font = ImageFont.truetype(font_path, font_size)
            text_width, text_height = draw.textsize(text, font=font)
            if text_width <= size[0] * 0.9 and text_height <= size[1] * 0.9:
                break
            font_size -= 1
        if font_size > 0:
            text_position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
            draw.text(text_position, text, fill="black", font=font)
    except IOError:
        print("글꼴 파일을 찾을 수 없습니다. 경로를 확인하세요.")
        return

    gray_image.save(output_path)

def save_original_image(img, output_path):
    img.save(output_path)

def process_all_images(input_folder, output_folder, text, font_path):
    os.makedirs(output_folder, exist_ok=True)
    
    file_mapping = {}
    
    all_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".png")]
    all_files.sort() 
    for idx, file_name in enumerate(all_files, start=1):
        original_name, ext = os.path.splitext(file_name)
        file_mapping[idx] = original_name 

        input_path = os.path.join(input_folder, file_name)
        with Image.open(input_path) as img:
            size = img.size

            original_output_path = os.path.join(output_folder, f"{idx}_i_s{ext}")
            save_original_image(img, original_output_path)

            gray_output_path = os.path.join(output_folder, f"{idx}_i_t{ext}")
            create_gray_image_with_text(size, gray_output_path, text, font_path)

    print(f"모든 작업이 완료되었습니다. 파일들이 '{output_folder}' 폴더에 저장되었습니다.")
    return file_mapping

