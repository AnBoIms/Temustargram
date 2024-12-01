import { Component } from "react";
import "../pages/Common.css";
import "../pages/Main.css";

import profileImg from "./Image/feed1-profile.jpg";


class MainRight extends Component {
  render() {
    return (
      <div className="main-right">
        <div className="user-info">
          <div>
            <img
              className="user-info-img"
              src={profileImg}
            />
          </div>
          <div className="user-info-text">
            <div className="user-info1">_sunghae__</div>
            <div className="user-info2">성혜</div>
          </div>
        </div>
        <div className="main-right-box">
          <div className="story-box">
            <div className="small-box">
              <span className="storytext">스토리</span>
              <span className="everything">모두 보기</span>
            </div>
            <div className="story-list">
              <div className="story-detail">
                <img src={profileImg} />
                <div className="story-info">
                  <div className="story-id">minitmute_official</div>
                  <div className="story-time">1시간 전</div>
                </div>
              </div>
              <div className="story-detail">
                <img src={profileImg} />
                <div className="story-info">
                  <div className="story-id">so__yoni</div>
                  <div className="story-time">2시간 전</div>
                </div>
              </div>
              <div className="story-detail">
                <img src={profileImg} />
                <div className="story-info">
                  <div className="story-id">it.smemario</div>
                  <div className="story-time">2시간 전</div>
                </div>
              </div>
              <div className="story-detail">
                <img src={profileImg} />
                <div className="story-info">
                  <div className="story-id">__onakahet__</div>
                  <div className="story-time">3시간 전</div>
                </div>
              </div>
              <div className="story-detail">
                <img src={profileImg} />
                <div className="story-info">
                  <div className="story-id">changmo_</div>
                  <div className="story-time">4시간 전</div>
                </div>
              </div>
            </div>
          </div>
          <div className="recommend-box">
            <div className="small-box">
              <span className="storytext">회원님을 위한 추천</span>
              <span className="everything">모두 보기</span>
            </div>
            <div className="recommend-list">
              <div className="story-detail">
                <img src={profileImg} />
                <div className="story-info">
                  <div className="story-id">2toyoung</div>
                  <div className="story-friend">회원님을 팔로우합니다</div>
                </div>
                <div className="follow">팔로우</div>
              </div>
              <div className="story-detail">
                <img src={profileImg} />
                <div className="story-info">
                  <div className="story-id">ron_sae</div>
                  <div className="story-friend">회원님을 팔로우합니다</div>
                </div>
                <div className="follow">팔로우</div>
              </div>
              <div className="story-detail">
                <img src={profileImg} />
                <div className="story-info">
                  <div className="story-id">sangtorii</div>
                  <div className="story-friend">회원님을 팔로우합니다</div>
                </div>
                <div className="follow">팔로우</div>
              </div>
            </div>
          </div>
          <div className="last-text">
            <div>
              Instagram 정보 · 도움말 · 홍보 센터 · API · 채용 정보 ·
              개인정보처리방침 · 약관 · 디렉터리 · 프로필 · 해시태그 · 언어
            </div>
            <div className="last">ⓒ 2020 INSTAGRAM</div>
          </div>
        </div>
      </div>
    );
  }
}

export default MainRight;
