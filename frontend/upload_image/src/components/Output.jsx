import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom"; // useNavigate 추가
import "./Main.css";
import { useRef } from "react";
// import { useNavigate } from "react-router-dom";
import MainNav from "./MainNav";


import tempImg from "../assets/tempIMG.jpg";
import InstaLogo from "../assets/instagramLogo.png";
import chatgptLogo from "../assets/chatgptLogo.png";
import downloadLogo from "../assets/downloadLogo.png";

const Output = () => {
    const imgRef = useRef(null);
    const navigate = useNavigate(); // navigate 훅 사용


    const location = useLocation();
    const [imageSrc, setImageSrc] = useState(null); // 이미지를 저장할 상태
    const [error, setError] = useState(null); // 에러 상태
  
    useEffect(() => {
      // location.state로 전달된 데이터 확인
      if (location.state && location.state.result) {
        const base64Image = location.state.result;

        if (!base64Image.startsWith("data:image/")) {
          setImageSrc(`data:image/png;base64,${base64Image}`);
        } else {
          setImageSrc(base64Image);
        }      } else {
        setError("이미지가 전달되지 않았습니다.");
      }
    }, [location.state]);


    const handleDownload = () => {
        // Get the image URL and create a link
        if (!imgRef.current) {
            console.error("Image not loaded or imgRef is null!");
            return;
        }

        const imgURL = imgRef.current.src;
        const link = document.createElement("a");
        link.href = imgURL;
        link.download = "downloaded_image.jpg"; // Set the file name
        link.click();
    };

    const handleGoToInsta = () => {
        navigate("/insta");
    };
    const handleGoToGpt = () => {
        navigate("/gpt");
    };

    return (
        <div>
            <MainNav />

            <div className="container">
                <div className = "alert">
                    <h1>개인정보 안보임스!</h1>

                </div>
                <div className = "preview">
                    {/* // 다음 img태그 주석하고 밑의 주석 풀기 */}
                    {/* <img className="img" ref={imgRef} src={tempImg} alt="Preview" /> */}
                    {imageSrc ? (
                        <div>
                        <img
                            ref={imgRef}
                            src={imageSrc}
                        />
                        </div>
                    ) : (
                        <div className="loader"></div>
                    )}
                </div>
        
                
                <div>
                    <button className="share_button"  onClick={handleGoToInsta}>
                        <a href="">
                            <img 
                            className="share_icon"
                            src={InstaLogo} />
                        </a>
                    </button>
                    <button className="share_button" onClick={handleGoToGpt}>
                    
                        <a href="">
                            <img                 
                            className="share_icon"
                            src={chatgptLogo} />
                        </a>
                    </button>
                    <button className="share_button" onClick={handleDownload}>
                        <img
                            className="share_icon"
                            src={downloadLogo}
                            alt="Download"
                        />
                    </button>
                </div>
        
            </div>
        </div>
        
    )
};

export default Output;
