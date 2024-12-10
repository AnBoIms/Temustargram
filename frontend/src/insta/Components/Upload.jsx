import "../pages/Upload.css";
import { useState, useEffect, useRef } from "react";
import {useLocation, useNavigate } from "react-router-dom";
import tempImg from "./Image/temp2.jpg";

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

function UploadModal({ onClose }) {
  const [isActive, setActive] = useState(false);
  const [imagePreview, setImagePreview] = useState("");
  const [responseMessage, setResponseMessage] = useState("");
  const [isUploaded, setIsUploaded] = useState(true);  // 업로드 완료 상태 관리

  const [objects, setObjects] = useState([]); // 객체 데이터 추가
  const [selectedObjectIds, setSelectedObjectIds] = useState([]); // 선택된 객체 ID 배열
  const canvasRef = useRef(null);
  const location = useLocation(); // location 객체를 사용하여 상태 데이터 접근
  const [error, setError] = useState(""); // 에러 메시지
  const [isLoading, setIsLoading] = useState(false); // 로딩 상태 추가
  const [serverMessage, setServerMessage] = useState(""); // 서버 응답 메시지

  const handleDragStart = () => setActive(true);
  const handleDragEnd = () => setActive(false);
  const handleDragOver = (event) => {
    event.preventDefault();
  };

  useEffect(() => {
  //   if (location.state && location.state.image && location.state.coor) {
  //     const base64Image = location.state.image;

  //     // base64 형식의 이미지 처리
  //     if (!base64Image.startsWith("data:image/")) {
  //       setImagePreview(`data:image/png;base64,${base64Image}`);
  //     } else {
  //       setImagePreview(base64Image);
  //     }

  //     setObjects(location.state.coor); // 전달된 객체 데이터 설정
  //     setResponseMessage(""); // 초기화
  //   } else {
  //     setResponseMessage("이미지 데이터가 전달되지 않았습니다/.");
  //   }
  // }, [location.state]);
  //------------------------------- 위아래로 주석 풀기/채우기
    setImagePreview(tempImg);
    setObjects([
      // 임시 객체 데이터 추가
      {
        id: 1,
        polygon: [
          [50, 50],
          [500, 50],
          [500, 500],
          [50, 500],
        ],
        // type: "id_card"
        type: "sign"
      },
    ]);
    setError("이미지 데이터가 전달되지 않았습니다.");
  }, []);
  // -----------------------------------

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

  const handleUpload = ({ target }) => {
    const file = target.files[0];
    if (file) {
      processFile(file);
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

        setIsUploaded(true);
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
  useEffect(() => {
    if (!imagePreview || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    const img = new Image();
    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);

      // 객체를 그리기
      objects.forEach((obj) => {
        const { polygon, id, type } = obj;

        ctx.beginPath();
        polygon.forEach(([x, y], index) => {
          if (index === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        });
        ctx.closePath();

        if (selectedObjectIds.includes(id)) {
          ctx.fillStyle = type === "id_card" ? "rgba(255, 0, 0, 0.3)" : "rgba(255, 255, 0, 0.3)";
          ctx.fill();
        } else {
          ctx.strokeStyle = type === "id_card" ? "red" : "yellow";
          ctx.lineWidth = 7;
          ctx.stroke();
        }
      });
    };
    img.src = imagePreview;
  }, [imagePreview, objects, selectedObjectIds]);

  const handleCanvasClick = (event) => {
    if (objects.length === 0) return;

    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const x = (event.clientX - rect.left) * scaleX;
    const y = (event.clientY - rect.top) * scaleY;

    objects.forEach((obj) => {
      const { id, polygon } = obj;
      const ctx = canvas.getContext("2d");
      ctx.beginPath();
      polygon.forEach(([px, py], index) => {
        if (index === 0) {
          ctx.moveTo(px, py);
        } else {
          ctx.lineTo(px, py);
        }
      });
      ctx.closePath();

      if (ctx.isPointInPath(x, y)) {
        setSelectedObjectIds((prev) =>
          prev.includes(id) ? prev.filter((objId) => objId !== id) : [...prev, id]
        );
      }
    });
  };

  const handleSendToServer = async (onClose) => {
    if (selectedObjectIds.length === 0) {
      setError("선택된 객체가 없습니다. 먼저 객체를 선택해주세요.");
      return;
    }

    setIsLoading(true); // 로딩 시작

    try {
      const response = await fetch("http://localhost:5000/load_result", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ selected_ids: selectedObjectIds }),
      });

      const data = await response.json();

      if (response.ok) {
        setServerMessage(data.message); // 서버의 성공 메시지 표시
        onClose(); // 서버 응답이 성공하면 onClose 호출

        // navigate("/Output", { state: { result: data.result } }); // Output 페이지로 결과 전달
      } else {
        setError(`서버 오류: ${data.message}`);
      }
    } catch (error) {
      setError("서버 요청에 실패했습니다. 네트워크 상태를 확인해주세요.");
    } finally {
      setIsLoading(false); // 로딩 종료
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="instacontainer">
          {isUploaded ? (  // isUploaded가 true일 때 InstaSelect 내용 표시
            <div>
              {isLoading && (
                <div className="lock-loading">
                  <div className="lock">
                    <div className="lock-body"></div>
                    <div className="lock-shackle"></div>
                  </div>
                  <h3>잠시만 기다려주세요...</h3>
                </div>
              )}
              <div>
                <h3>개인정보를 가진 객체가 검출되었어요!</h3>
                <div>
                  <h3>사진에 표시된<br />객체들 중<br />가리고 싶은 대상을<br />선택해주세요.</h3>
                  <div className="selectImg">
                    <canvas ref={canvasRef} className="select_preview" onClick={handleCanvasClick} />
                  </div>
                </div>
                <div>
                  <p>{responseMessage}</p>
                </div>
                <div>
                  <button onClick={() => handleSendToServer(onClose)}>Upload</button>
                </div>
              </div>
            </div>

          ) : (  // 이 괄호는 위의 조건문을 닫고, else 부분을 시작하는 괄호입니다.
              <div>
                <div className="alert">
                  <h2>개인정보가 포함 여부를 검사할 사진을 선택해주세요.</h2>
                </div>
                <div>
                  <label
                    className={`instaPreview${isActive ? " active" : ""}`}
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
              </div>
          )}  {/* 여기에서 조건문 끝 */}
          
          {responseMessage && <div id="responseMessage">{responseMessage}</div>}
        </div>
        <button onClick={onClose}>닫기</button>
      </div>
    </div>
  );
}

export default UploadModal;
