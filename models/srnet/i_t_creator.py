import os
from PIL import Image, ImageDraw, ImageFont

# 폴더 경로 설정
input_folder = "models/srnet/static/cropped"  # PNG 파일이 있는 폴더 경로
output_folder = "models/srnet/custom_feed/labels/"  # 회색 배경 이미지를 저장할 폴더 경로

# 출력 폴더가 없으면 생성
os.makedirs(output_folder, exist_ok=True)

# 글꼴 파일 경로 설정 (예: 나눔고딕 글꼴)
font_path = "models/srnet/hangil.ttf"  # 자신의 시스템에 맞는 경로로 변경

# 회색 배경 생성 및 한글 텍스트 추가 함수
def create_gray_image_with_text(size, output_path, text):
    gray_image = Image.new("RGB", size, (128, 128, 128))  # RGB 값 (128, 128, 128)은 회색
    
    # 이미지에 글씨 그리기
    draw = ImageDraw.Draw(gray_image)
    try:
        # 폰트 크기를 동적으로 조정하기 위해 초기 폰트 크기 설정
        font_size = min(size[0], size[1]) // 1  # 이미지 크기 대비 1/10 정도로 초기 크기 설정

        # 폰트 크기가 0 이하가 되지 않도록 확인하면서 설정
        while font_size > 0:
            font = ImageFont.truetype(font_path, font_size)
            text_width, text_height = draw.textsize(text, font=font)

            # 텍스트 크기가 이미지 크기의 90% 이내라면 반복 종료
            if text_width <= size[0] * 0.9 and text_height <= size[1] * 0.9:
                break

            # 폰트 크기 감소
            font_size -= 1

        # 폰트 크기가 0보다 크면 텍스트를 그림
        if font_size > 0:
            text_position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
            draw.text(text_position, text, fill="black", font=font)

    except IOError:
        print("글꼴 파일을 찾을 수 없습니다. 경로를 확인하세요.")
        return

    gray_image.save(output_path)
    # print(f"회색 배경 이미지가 '{output_path}'에 저장되었습니다.")

# 폴더 내 모든 PNG 파일을 처리하는 함수
def process_all_images(input_folder, output_folder, text):
    # 출력 폴더가 없으면 생성
    os.makedirs(output_folder, exist_ok=True)
    
    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith(".png"):  # 대소문자 구분 없이 PNG 파일 확인
            input_path = os.path.join(input_folder, file_name)

            # 이미지 열기
            with Image.open(input_path) as img:
                size = img.size  # (width, height)

                # 원본 파일 저장
                base_name, ext = os.path.splitext(file_name)
                modified_name = f"{base_name}_i_s{ext}"
                original_output_path = os.path.join(output_folder, modified_name)

                if not os.path.exists(original_output_path):
                    img.save(original_output_path)
                    # print(f"원본 이미지 저장 완료: {original_output_path}")

                # 회색 배경 이미지 생성 및 한글 텍스트 추가
                gray_name = f"{base_name}_i_t{ext}"
                gray_output_path = os.path.join(output_folder, gray_name)
                create_gray_image_with_text(size, gray_output_path, text)

    # print(f"모든 작업이 완료되었습니다. 파일들이 '{output_folder}' 폴더에 저장되었습니다.")

# 메인 함수 실행
if __name__ == "__main__":
    process_all_images(input_folder, output_folder, "안보임스")
