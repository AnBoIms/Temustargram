import { useState } from 'react';

const ImageUpload = () => {
    const [file, setFile] = useState(null);
    const [responseMessage, setResponseMessage] = useState('');


    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
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
        <div>
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
            {responseMessage && <div id="responseMessage">{responseMessage}</div>}
            
        </div>
    );
};

export default ImageUpload;
