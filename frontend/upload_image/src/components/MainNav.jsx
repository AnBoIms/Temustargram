import { Component } from "react";
import "../index.css";
import "./MainNav.css";
import logoText from "../assets/AnboimsLogo.png";
import InstaLogo from "../assets/instagramLogo.png";
import chatgptLogo from "../assets/chatgptLogo.png";


// import upload from "../Components/Image/24uploadIcon.png";

class MainNav extends Component {
  render() {
    return (
      <nav>
        <div className="topBox">
            <div className="link-left">
                <a href="">
                    <img src={logoText} />
                </a>
                <div className="slash"></div>
                <div className="info">
                  당신의 사진을 안전하게~<br></br>
                  안전보호 이미지 안보임스
                </div>
            </div>
            <div className = "link-right"> 
                <a href="">
                    <img 
                      className="upload_icon"
                      src={InstaLogo} />
                </a>
                <a href="">
                    <img                 
                    className="upload_icon"
                     src={chatgptLogo} />
                </a>
            </div>

        </div>
        <div className="underline"></div>

      </nav>
    );
  }
}

export default MainNav;
