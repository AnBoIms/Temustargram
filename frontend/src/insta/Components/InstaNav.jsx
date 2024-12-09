import { Component } from "react";
import { useState } from 'react';
import "../pages/Common.css";
import "../pages/InstaMain.css";
import logoText from "../Components/Image/logo_text.png";
import upload from "../Components/Image/24uploadIcon.png";
import UploadModal from './Upload';

function MainNav() {
  const [isUploadModalOpen, setUploadModalOpen] = useState(false);

  const handleOpenModal = () => {
    setUploadModalOpen(true);
  };

  const handleCloseModal = () => {
    setUploadModalOpen(false);
  };

  return (
      <nav>
        <div className="topBox">
          <div className="link-left">
            <a href="">
              <img src="https://s3.ap-northeast-2.amazonaws.com/cdn.wecode.co.kr/bearu/logo.png" />
            </a>
            <div className="slash"></div>
            <a className="logo_img" href="">
              <img src={logoText} />
            </a>
          </div>
          <div className="search">
            <input type="search" placeholder="검색" />
          </div>
          <div className="link-right">
          <button className="upload-button" onClick={handleOpenModal}>
                <img
                  className="upload-icon"
                  src={upload}
                />
          </button>
          {isUploadModalOpen && <UploadModal onClose={handleCloseModal} />}

            <a href="">
              <img
                className="search-icon"
                src="https://s3.ap-northeast-2.amazonaws.com/cdn.wecode.co.kr/bearu/explore.png"
              />
            </a>
            <a href="">
              <img
                className="heart-icon"
                src="https://s3.ap-northeast-2.amazonaws.com/cdn.wecode.co.kr/bearu/heart.png"
              />
            </a>
            <a href="">
              <img
                className="mypage-icon"
                src="https://s3.ap-northeast-2.amazonaws.com/cdn.wecode.co.kr/bearu/profile.png"
              />
            </a>
          </div>
        </div>
      </nav>
  );
  
}

export default MainNav;
