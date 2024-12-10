import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "./Main.css";
import MainNav from "./MainNav";
import tempImg from "../assets/temp2.jpg";
// src\assets\temp2.jpg
// src\components\Select.jsx


const Select = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const canvasRef = useRef(null);
  const [imageSrc, setImageSrc] = useState(""); // 이미지 URL
  const [objects, setObjects] = useState([]); // 객체 데이터
  const [error, setError] = useState(""); // 에러 메시지
  const [selectedObjectIds, setSelectedObjectIds] = useState([]); // 선택된 객체 ID 배열
  const [serverMessage, setServerMessage] = useState(""); // 서버 응답 메시지
  const [isLoading, setIsLoading] = useState(false); // 로딩 상태 추가

  useEffect(() => {
    if (location.state && location.state.image && location.state.coor) {
      const base64Image = location.state.image;

      if (!base64Image.startsWith("data:image/")) {
        setImageSrc(`data:image/png;base64,${base64Image}`);
      } else {
        setImageSrc(base64Image);
      }

      setObjects(location.state.coor); // 전달된 객체 데이터 설정
      setError(""); // 에러 초기화
    } else {
      setError("이미지 데이터가 전달되지 않았습니다.");
    }
  }, [location.state]);
  //------------------------------- 위아래로 주석 풀기/채우기
  //   setImageSrc(tempImg);
  //   setObjects([
  //     // 임시 객체 데이터 추가
  //     {
  //       id: 1,
  //       polygon: [
  //         [50, 50],
  //         [500, 50],
  //         [500, 500],
  //         [50, 500],
  //       ],
  //       type: "id_card"
  //       // type: "sign"
  //     },
  //   ]);
  //   setError("");
  // }, []);
  // -----------------------------------


  useEffect(() => {
    if (!imageSrc || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    if (imageSrc && objects.length > 0) {
      const img = new Image();

      img.onload = () => {
        canvas.width = img.width;
        canvas.height = img.height;

        ctx.drawImage(img, 0, 0);

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
            if(type == "id_card"){
              ctx.fillStyle = "rgba(255, 0, 0, 0.3)";
            }
            else if(type == "sign"){
              ctx.fillStyle = "rgba(255, 255, 0, 0.3)";
            }
            ctx.fill();
          } else {
            if(type == "id_card"){
              ctx.strokeStyle = "red";
            }
            else if(type == "sign"){
              ctx.strokeStyle = "yellow";
            }
            ctx.lineWidth = 7;
            ctx.stroke();
          }
        });
      };

      img.src = imageSrc;
    }

    const handleCanvasClick = (event) => {
      if (objects.length === 0) return;

      const rect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / rect.width;
      const scaleY = canvas.height / rect.height;
      const x = (event.clientX - rect.left) * scaleX;
      const y = (event.clientY - rect.top) * scaleY;

      for (const obj of objects) {
        const { id, polygon } = obj;

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
          ); // 선택 해제 또는 추가
          return;
        }
      }
    };

    canvas.addEventListener("click", handleCanvasClick);

    return () => {
      canvas.removeEventListener("click", handleCanvasClick);
    };
  }, [imageSrc, objects, selectedObjectIds]);

  const handleGoBack = () => {
    navigate("/");
  };

  const handleSendToServer = async () => {
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
        navigate("/Output", { state: { result: data.result } }); // Output 페이지로 결과 전달
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
    <div>
      <MainNav />

      {error && <div style={{ color: "red", marginTop: "10px" }}>{error}</div>}
      {serverMessage && <div style={{ color: "green", marginTop: "10px" }}>{serverMessage}</div>}
      {isLoading && (
        <div className="lock-loading">
          <div className="lock">
            <div className="lock-body"></div>
            <div className="lock-shackle"></div>
          </div>
          <h3>잠시만 기다려주세요...</h3>
        </div>
      )}
      <div className="container_row" style={{ display: isLoading ? "none" : "flex" }}>
     
        <div className="box">
          <div className="alert_col">
            <h3>사진에 표시된<br />객체들 중<br />가리고 싶은 대상을<br />선택해주세요.</h3>
          </div>
          <div >
            <div className="align-center">
              <button className="upload_button" onClick={handleGoBack}>
                이전 페이지로
              </button>
              <button className="upload_button" onClick={handleSendToServer}>
                선택 완료
              </button>
            </div>
          </div>
          
        </div>
        <div className="selectImg">
          {imageSrc ? (
            <canvas ref={canvasRef} className="select_preview" />
          ) : (
            <div className="loader"></div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Select;
