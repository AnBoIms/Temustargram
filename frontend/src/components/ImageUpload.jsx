import { useState } from "react";
import { useNavigate } from "react-router-dom";
import MainNav from "./MainNav";
import "./Main.css";

const Logo = () => (
  <svg className="icon" x="0px" y="0px" viewBox="0 0 24 24">
    <path fill="transparent" d="M0,0h24v24H0V0z" />
    <path
      fill="#000"
      d="M20.5,5.2l-1.4-1.7C18.9,3.2,18.5,3,18,3H6C5.5,3,5.1,3.2,4.8,3.5L3.5,5.2C3.2,5.6,3,6,3,6.5V19
        c0,1.1,0.9,2,2,2h14c1.1,0,2-0.9,2-2V6.5C21,6,20.8,5.6,20.5,5.2z M12,17.5L6.5,12H10v-2h4v2h3.5L12,17.5z M5.1,5l0.8-1h12l0.9,1
        H5.1z"
    />
  </svg>
);

const UploadBox = () => {
  const [isActive, setActive] = useState(false);
  const [imagePreview, setImagePreview] = useState("");
  const [responseMessage, setResponseMessage] = useState("");
  const navigate = useNavigate(); // 페이지 이동을 위한 hook

  const handleDragStart = () => setActive(true);
  const handleDragEnd = () => setActive(false);
  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const processFile = (file) => {
    const { size: byteSize, type } = file;

    if (byteSize > 20 * 1024 * 1024) {
      alert("File size must be less than 20MB.");
      return;
    }

    if (type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onloadend = () => setImagePreview(reader.result);
      reader.readAsDataURL(file);
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setActive(false);
  
    const file = event.dataTransfer.files[0];
    if (file) {
      processFile(file);
  
      // <input>과 동기화
      const fileInput = document.querySelector(".file");
      if (fileInput) {
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        fileInput.files = dataTransfer.files;
      }
    }
  };
  

  const handleUpload = ({ target }) => {
    const file = target.files[0];
    if (file) {
      processFile(file);
    }
  };

  const handleSubmit = async () => {
    const fileInput = document.querySelector(".file");
    const file = fileInput?.files[0];

    if (!file) {
      alert("No file selected for upload.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Response JSON:', result); 

        navigate("/Select", {state: {image : result.img, coor: result.objects}}); // 업로드 성공 시 성공 페이지로 이동
        setResponseMessage(`Upload successful: ${result.message}`);
      } else {
        const errorData = await response.json();
        setResponseMessage(`Upload failed: ${errorData.message}`);
      }
    } catch (error) {
      console.error("Error uploading file:", error);
      setResponseMessage("An error occurred while uploading the file.");
    }
  };

  return (
    <div>
      <MainNav />
      <div className="container">
        <div className = "alert">
          <h2>개인정보가 포함 여부를 검사할 사진을 선택해주세요.</h2>
        </div>
        <div>
            <label
                className={`preview${isActive ? " active" : ""}`}
                onDragEnter={handleDragStart}
                onDragOver={handleDragOver}
                onDragLeave={handleDragEnd}
                onDrop={handleDrop}
            >
            <input type="file" className="file" onChange={handleUpload} accept="image/*" />
            {imagePreview ? (
            <div className="image_preview">
                <img
                src={imagePreview}
                alt="Preview"
                style={{ maxWidth: "100%", maxHeight: "300px", objectFit: "contain" }}
                />
            </div>
            ) : (
            <>
                <Logo />
                <p className="preview_msg">클릭 혹은 파일을 이곳에 드롭하세요.</p>
                <p className="preview_desc">파일당 최대 20MB</p>
            </>
            )}
            </label>
        </div>
        <div>
            <button onClick={handleSubmit} className="upload_button">
                이미지 제출
            </button>
        </div>
       
      {responseMessage && <div id="responseMessage">{responseMessage}</div>}
    </div>
    </div>
    
  );
};

export default UploadBox;
