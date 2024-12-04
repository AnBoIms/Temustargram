import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom"; // useNavigate 추가
import "./Main.css";

const Select = () => {
  const location = useLocation();
  const navigate = useNavigate(); // navigate 훅 사용
  const canvasRef = useRef(null);
  const [imageSrc, setImageSrc] = useState(""); // 이미지 URL
  const [objects, setObjects] = useState([]); // 객체 데이터
  const [error, setError] = useState(""); // 에러 메시지
  const [highlightedObjectId, setHighlightedObjectId] = useState(null); // 강조된 객체 ID 저장

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

  useEffect(() => {
    if (!imageSrc || !canvasRef.current) return; // `null` 상태에서 작업 방지

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    if (imageSrc && objects.length > 0) {
      const img = new Image();

      img.onload = () => {
        // 캔버스 크기를 이미지 크기에 맞춤
        canvas.width = img.width;
        canvas.height = img.height;

        // 이미지 그리기
        ctx.drawImage(img, 0, 0);

        // 다각형 그리기
        objects.forEach((obj) => {
          const { polygon, id } = obj;

          ctx.beginPath();
          polygon.forEach(([x, y], index) => {
            if (index === 0) {
              ctx.moveTo(x, y); // 시작점 설정
            } else {
              ctx.lineTo(x, y); // 라인 그리기
            }
          });
          ctx.closePath();

          // 선택된 객체는 반투명한 색으로 채우기
          if (id === highlightedObjectId) {
            ctx.fillStyle = "rgba(255, 0, 0, 0.3)"; // 빨간색, 50% 투명도
            ctx.fill(); // 다각형 색 채우기
          } else {
            ctx.strokeStyle = "red"; // 기본 테두리 색상
            ctx.lineWidth = 10;
            ctx.stroke();
          }
        });
      };

      img.src = imageSrc;
    }

    const handleCanvasClick = (event) => {
      if (objects.length === 0) return;

      // 클릭 좌표 계산
      const rect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / rect.width; // X축 스케일 비율
      const scaleY = canvas.height / rect.height; // Y축 스케일 비율
      const x = (event.clientX - rect.left) * scaleX;
      const y = (event.clientY - rect.top) * scaleY;

      // 클릭한 다각형 확인
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

        // 클릭 위치가 다각형 내부인지 확인
        if (ctx.isPointInPath(x, y)) {
          setHighlightedObjectId(id); // 클릭된 객체의 ID를 상태에 저장
          return; // 첫 번째 매칭 다각형만 처리
        }
      }
    };

    // 클릭 이벤트 리스너 추가
    canvas.addEventListener("click", handleCanvasClick);

    // 클린업 함수로 이벤트 리스너 제거
    return () => {
      canvas.removeEventListener("click", handleCanvasClick);
    };
  }, [imageSrc, objects, highlightedObjectId]);

  const handleGoBack = () => {
    navigate("/"); // "/" 경로로 이동
  };

  const handleGoOutput = () => {
    navigate("/Output"); // "/" 경로로 이동
  };

  return (
    <div>
      {error && <div style={{ color: "red", marginTop: "10px" }}>{error}</div>}
      <div className="container_row">
        <div>
          <div className="alert_col">
            <h2>사진에 표시된 객체들 중<br />가리고 싶은 대상을 선택해주세요.</h2>
          </div>
          <div className="center">
            <button className="upload_button" onClick={handleGoBack}>
              이전 페이지로
            </button>
            <button className="upload_button" onClick={handleGoOutput}>
              선택 완료
            </button>
          </div>
        </div>
        
        {imageSrc ? (
          <canvas ref={canvasRef} className="select_preview" />
        ) : (
          <div>Loading image...</div>
        )}
      </div>
    </div>
  );
};

export default Select;
