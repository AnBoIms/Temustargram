import os
from PIL import Image, ImageDraw, ImageFont

# # 폴더 경로 설정
# input_folder = "static/text_regions"  # PNG 파일이 있는 폴더 경로
# output_folder = "labels/"  # 처리된 이미지를 저장할 폴더 경로

# # 출력 폴더가 없으면 생성
# os.makedirs(output_folder, exist_ok=True)

# # 글꼴 파일 경로 설정
# font_path = "hangil.ttf"  # 자신의 시스템에 맞는 경로로 변경

# 회색 배경 생성 및 한글 텍스트 추가 함수
def create_gray_image_with_text(size, output_path, text, font_path):
    gray_image = Image.new("RGB", size, (128, 128, 128))  # RGB 값 (128, 128, 128)은 회색
    
    # 이미지에 글씨 그리기
    draw = ImageDraw.Draw(gray_image)
    try:
        font_size = min(size[0], size[1]) // 1  # 폰트 크기 설정
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

# 원본 파일 저장 함수
def save_original_image(img, output_path):
    img.save(output_path)

# 폴더 내 모든 PNG 파일을 처리하는 함수
def process_all_images(input_folder, output_folder, text, font_path):
    os.makedirs(output_folder, exist_ok=True)
    
    # 원본 이름과 처리된 이름을 매핑하는 딕셔너리
    file_mapping = {}
    
    # 원본 파일 읽기 및 매핑 저장
    all_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".png")]
    all_files.sort()  # 파일 이름 정렬
    for idx, file_name in enumerate(all_files, start=1):
        original_name, ext = os.path.splitext(file_name)
        file_mapping[idx] = original_name  # 딕셔너리에 매핑 저장

        # 이미지 열기
        input_path = os.path.join(input_folder, file_name)
        with Image.open(input_path) as img:
            size = img.size

            # 원본 파일 저장
            original_output_path = os.path.join(output_folder, f"{idx}_i_s{ext}")
            save_original_image(img, original_output_path)

            # 회색 배경 이미지 생성 및 저장
            gray_output_path = os.path.join(output_folder, f"{idx}_i_t{ext}")
            create_gray_image_with_text(size, gray_output_path, text, font_path)

    # 결과 매핑 출력
    # print("파일 이름 매핑:")
    # for new_idx, original_name in file_mapping.items():
    #     print(f"{new_idx}: {original_name}")

    print(f"모든 작업이 완료되었습니다. 파일들이 '{output_folder}' 폴더에 저장되었습니다.")
    return file_mapping

# # 메인 함수 실행
# if __name__ == "__main__":
#     process_all_images(input_folder, output_folder, "안보임스")
