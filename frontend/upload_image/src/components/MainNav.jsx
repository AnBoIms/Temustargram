import { Component } from "react";
import "../index.css";
import "./MainNav.css";
import logoText from "../../public/AnboimsLogo.png";
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

            </div>
            <div className="info">
                안보임스 홈페이지에 오신 것을 환영합니다!<br></br>
                개인정보를 가리고 싶은 이미지를 선택해주세요.
            </div>

        </div>
        <div className="underline"></div>

      </nav>
    );
  }
}

export default MainNav;
