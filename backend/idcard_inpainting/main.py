from idcard_processor import ocr_result, process_ocr_results, process_bounding_box
import cv2

# 이미지 및 텍스처 경로 설정
image_path = 'Temustargram/backend/idcard_inpainting/crop_image/cropimage.png'
textures = {
    "name": 'Temustargram/backend/idcard_inpainting/text_image/name.png',
    "resident_id": 'Temustargram/backend/idcard_inpainting/text_image/number.png',
    "address": 'Temustargram/backend/idcard_inpainting/text_image/address.png'
}
output_image_path = "Temustargram/backend/idcard_inpainting/output_image/idcard_inpainting_image.png"

# OCR 실행
ocr_results = ocr_result(image_path)
processed_results = process_ocr_results(ocr_results)

# 원본 이미지 로드
image = cv2.imread(image_path)

# 각 카테고리에 대해 이미지 합성
for category, bounding_box_data in processed_results.items():
    if bounding_box_data and isinstance(bounding_box_data, list):
        for bounding_box, _ in bounding_box_data:
            texture_path = textures.get(category)
            if texture_path:
                image = process_bounding_box(image, texture_path, bounding_box)

# 결과 이미지 저장
cv2.imwrite(output_image_path, image)
print(f"결과 이미지 저장 완료: {output_image_path}")
