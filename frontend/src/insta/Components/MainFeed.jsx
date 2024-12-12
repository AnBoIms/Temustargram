import { Component } from "react";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import "../pages/Common.css";
import "../pages/InstaMain.css";
import MainRight from "./MainRight";
import CmtBox from "./CmtBox";

import profileImg from "./Image/firstFeed.jpg";
import dltnwjd22 from "./Image/dltnwjd22.jpg";

import threeDot from "./Image/three-dot.png";
// import feedMain from "./Image/feed1-main.jpg";
import heart from "./Image/heart.png";
import talk from "./Image/talk.png";
import share from "./Image/share.png";
import bookmark from "./Image/bookmark.png";

const MainFeed = ({ location }) => {
  const [error, setError] = useState(null); // 에러 상태
  const [comment, setComment] = useState(""); // input 값
  const [comments, setComments] = useState([]); // 입력된 댓글 배열
  const [imageSrc, setImageSrc] = useState(profileImg); // 기본 이미지를 초기값으로 설정


   // input값 받는 onChange 함수
  const newComment = (e) => {
    setComment(e.target.value);
  };

  // 추가된 input을 배열에 넣는 onClick 함수
  const addComment = () => {
    setComments([...comments, comment]);
    setComment(""); // 입력 후 텍스트를 비워줌
  };

  // map을 return하는 함수
  const cmtUpdate = (arr) => {
    return arr.map((cmt, index) => <CmtBox key={index} data={cmt} />);
  };
  return (
      <section className="main2">
        <article>
          <div className="feed1">
            <div className="feeds-top">
              <header className="feed-info">
                <img className="feed-image" src={dltnwjd22} />
                <a className="feed-id">dltnwjd22</a>
                <div className="feed-menu">
                  <img src={threeDot} />
                </div>
              </header>
              <div className="main-image">
                <a href="">
        
                  <img src={imageSrc} />    

                </a>
              </div>
            </div>
            <div className="feeds-bottom">
              <div className="feeds-bottom1">
                <section className="icon-box">
                  <button type="button">
                    <img src={heart} />
                  </button>
                  <button type="button">
                    <img src={talk} />
                  </button>
                  <button type="button">
                    <img src={share} />
                  </button>
                  <button className="moveIcon" type="button">
                    <img src={bookmark} />
                  </button>
                </section>
                <section className="like">좋아요 33개</section>
                <div className="comment-box">
                  <div>
                    <span className="comment-id">dltnwjd22</span>
                    <span>이사완료!!!</span>
                  </div>
                  <div className="comment-view">댓글 3개 모두 보기</div>
                  <div className="addComment">
                    <div className="comment-list">
                      <span className="comment-id">orhj_0612</span>
                    <span className="comment-text">
                      영욱빌라 아님?? 
                      </span>
                      <img src={heart} />
                    </div>
                    <div className="comment-list">
                      <span className="comment-id">10wook._.0912</span>
                      <span className="comment-text">
                      신분증을 누가 핸드폰 뒤에 들고다녀;; 주민번호 다털림 ㅅㄱ
                    </span>
                      <img src={heart} />
                    </div>
                    <div className="comment-list">
                      <span className="comment-id">bonumstella</span>
                      <span className="comment-text">
                        어딘지 알겠다 바로 갈게~
                      </span>
                      <img src={heart} />
                    </div>

                    {/* 새로운 댓글 추가할 위치 */}
                  {cmtUpdate(comments)}
                </div>
              </div>
              <div className="uploadTime">15분 전</div>
            </div>
            <section className="submit-box">
              <div>
                <input
                  className="submitComment"
                  type="text"
                  placeholder="댓글 달기..."
                  onChange={newComment}
                  value={comment}
                />

                  {/* comment추가 이벤트 */}
                  <button className="submitBtn" onClick={addComment}>
                    게시
                  </button>
                </div>
              </section>
            </div>
          </div>
        </article>
        <MainRight />
      </section>
  );
  
}

export default MainFeed;
