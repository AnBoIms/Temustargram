import { useState } from 'react';
import "./Main.css";

const ImageUpload = () => {
    const [file, setFile] = useState(null);
    const [responseMessage, setResponseMessage] = useState('');
    const [imagePreview, setImagePreview] = useState(''); // 이미지 프리뷰 상태 추가


    const handleFileChange = (event) => {
        const selectedFile = event.target.files[0];
        setFile(selectedFile);

        // 이미지 파일이 선택되었을 경우 미리보기 설정
        if (selectedFile) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setImagePreview(reader.result); // 파일 읽기 완료 후 이미지 URL을 상태에 저장
            };
            reader.readAsDataURL(selectedFile); // 파일을 Data URL로 읽음
        }    
    };
    
    const handleSubmit = async (event) => {
        event.preventDefault(); // 폼 제출 기본 동작 방지

        if (!file) {
            setResponseMessage('Please select a file before uploading.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

    
        const response = await fetch('http://localhost:5000/upload', {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            const result = await response.json();
            console.log('Response JSON:', result);
            setResponseMessage(`Message: ${result.message}, Success: ${result.isSuccess}`);
        } else {
            const errorData = await response.json();
            console.log('Error JSON:', errorData);
            setResponseMessage(`Error: ${errorData.message}`);
        }
      
    };

    return (
        <div className ="container">
            <h1>Image Upload</h1>
            <form onSubmit={handleSubmit}>
                <input
                    type="file"
                    onChange={handleFileChange}
                    accept="image/*"
                    required
                />
                <div>
                    <button type="submit">Upload Image</button>

                </div>
            </form>

            
            {imagePreview && (
                <div>
                    <h3>Image Preview:</h3>
                    <img src={imagePreview} alt="Image Preview" style={{ maxWidth: '100%', maxHeight: '300px', objectFit: 'contain' }} />
                </div>
            )}
            
            {responseMessage && <div id="responseMessage">{responseMessage}</div>}
            
        </div>
    );
};

export default ImageUpload;
