import { Component } from "react";
import "../index.css";
import "./MainNav.css";
import logoText from "../assets/AnboimsLogo.png";
import InstaLogo from "../assets/instagramLogo.png";
import chatgptLogo from "../assets/chatgptLogo.png";
import { useNavigate } from "react-router-dom";


// import upload from "../Components/Image/24uploadIcon.png";

const MainNav = () => {
  const navigate = useNavigate(); // navigate 훅 사용

  const handleGoToInsta = () => {
    navigate("/insta");
  };
  const handleGoToGpt = () => {
    navigate("/gpt");
  };


  return (
      <div>
        <div className="topBox">
            <div className="link-logo">
                <a href="">
                    <img src={logoText} />
                </a>
                <div className="line"></div>
                <div className="info">
                  당신의 사진을 안전하게~<br></br>
                  안전보호 이미지 안보임스
                </div>
            </div>
            <div className = "link-right"> 
              <button onClick={handleGoToInsta}>
                <a href="">
                    <img 
                      className="upload_icon"
                      src={InstaLogo} />
                </a>
              </button>
              <button className="share_button" onClick={handleGoToGpt}>    
                <a href="">
                    <img                 
                    className="upload_icon"
                     src={chatgptLogo} />
                </a>
              </button>
                
            </div>

        </div>
        <div className="underline"></div>

      </div>
  );
  
};

export default MainNav;
