from idcard_processor import ocr_result, process_ocr_results, process_bounding_box, apply_blur
import cv2

# 이미지 및 텍스처 경로 설정
image_path = '/home/hyejin/test_ocr/inpainting_final/crop_image/cropimage2.png'
textures = {
    "name": '/home/hyejin/test_ocr/inpainting_final/text_image/name.png',
    "resident_id": '/home/hyejin/test_ocr/inpainting_final/text_image/number.png',
    "address": '/home/hyejin/test_ocr/inpainting_final/text_image/address.png'
}
output_image_path = "/home/hyejin/test_ocr/inpainting_final/output_image/idcard_inpainting_image2.png"

# OCR 실행
ocr_results = ocr_result(image_path)
processed_results = process_ocr_results(ocr_results)

# 각 카테고리에 대해 이미지 합성
image = cv2.imread(image_path)
if not processed_results["name"] or not processed_results["resident_id"] or not processed_results["address"]:
    apply_blur(image, output_image_path)
    print(f"블러 처리된 이미지가 저장되었습니다: {output_image_path}")
else:
    for category, bounding_box_data in processed_results.items():
        if bounding_box_data and isinstance(bounding_box_data, list):
            for bounding_box, _ in bounding_box_data:
                texture_path = textures.get(category)
                if texture_path:
                    image = process_bounding_box(image, texture_path, bounding_box)

    # 결과 이미지 저장
    cv2.imwrite(output_image_path, image)
    print(f"결과 이미지 저장 완료: {output_image_path}")
