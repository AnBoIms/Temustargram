import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom"; // useNavigate 추가
import "./Main.css";
import MainNav from "./MainNav";


import tempImg from "../assets/temp2.jpg";
import InstaLogo from "../assets/instagramLogo.png";
import chatgptLogo from "../assets/chatgptLogo.png";
import downloadLogo from "../assets/downloadLogo.png";

const Output = () => {
    const imgRef = useRef(null);
    const navigate = useNavigate(); // navigate 훅 사용
   
    const [selectedObjectIds, setSelectedObjectIds] = useState([]); // 선택된 객체 ID 배열
    const location = useLocation();


    const [imageSrc, setImageSrc] = useState(null); // 이미지를 저장할 상태
    const [error, setError] = useState(null); // 에러 상태
  
    useEffect(() => {
      location.state
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
    // -----------------------------------
    //     setImageSrc(tempImg);
        
    //     setError("");
    // }, []);
  //---------------------------

    const handleDownload = () => {
        // Get the image URL and create a link
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
                <div className = "text_output">
                    <h1>개인정보 안보임스!</h1>
                </div>
                <div className = "result">
                    {imageSrc ? (
                        <div className = "result_img">
                            <img
                                src={imageSrc}
                            />
                        </div>
                    ) : (
                        <div className="loader"></div>
                    )}
                </div>
        
                
                <div className = "buttons">
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
