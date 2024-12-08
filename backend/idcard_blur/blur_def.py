def apply_blur(image_path, output_path, blur_intensity=45):
    blurred_image = cv2.GaussianBlur(image_path, (blur_intensity, blur_intensity), 0)

    cv2.imwrite(output_path, blurred_image)