import { Component } from "react";
import "../pages/Common.css";
import "../pages/Main.css";
import MainRight from "./MainRight";
import CmtBox from "./CmtBox";

import profileImg from "./Image/feed1-profile.jpg";
import threeDot from "./Image/three-dot.png";
import feedMain from "./Image/feed1-main.jpg";
import heart from "./Image/heart.png";
import talk from "./Image/talk.png";
import share from "./Image/share.png";
import bookmark from "./Image/bookmark.png";

class MainFeed extends Component {
  constructor(props) {
    super(props);

    this.state = {
      comment: "", //input창
      comments: [] //입력된 댓글을 포함하고있는 배열
    };
  }

  //input값 받는 onChange 함수
  newComment = e => {
    this.setState({
      comment: e.target.value
    });
  };

  //추가된 input을 배열에 넣는 onClick 함수
  // comment:"" 하는 이유는 클릭 후 인풋안에 있던 텍스트를 없애기 위해서
  addComment = e => {
    this.setState({
      comments: this.state.comments.concat(this.state.comment),
      comment: ""
    });
  };

  //map을 return하는 함수
  //매개변수 꼭 설정(arr) -> 함수를 실행할 때 받는 배열인 인자에 map를 쓰기 때문에
  //cmt = this.state.comments이고 이 값을 CmtBox의 props로 전달
  cmtUpdate = arr => {
    return arr.map(cmt => <CmtBox data={cmt} />);
  };

  render() {
    return (
      <section className="main2">
        <article>
          <div className="feed1">
            <div className="feeds-top">
              <header className="feed-info">
                <img className="feed-image" src={profileImg} />
                <a className="feed-id">5rozy_</a>
                <div className="feed-menu">
                  <img src={threeDot} />
                </div>
              </header>
              <div className="main-image">
                <a href="">
                  <img src={feedMain} />
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
                <section className="like">좋아요 1,063개</section>
                <div className="comment-box">
                  <div>
                    <span className="comment-id">5rozy_</span>
                    <span>언니잠싀만!!!!!! 냄새맛집이라고</span>
                  </div>
                  <div className="comment-view">댓글 2개 모두 보기</div>
                  <div className="addComment">
                    <div className="comment-list">
                      <span className="comment-id">br0thersilver</span>
                      <span className="comment-text">멍!!멍멍!!</span>
                      <img src={heart} />
                    </div>
                    <div className="comment-list">
                      <span className="comment-id">jiy00000n</span>
                      <span className="comment-text">
                        아 로지 사랑스로왕,,🧡🧡
                      </span>
                      <img src={heart} />
                    </div>

                    {/* 새로운 댓글 추가할 위치 */}
                    {/* this.state.comments를 인자로 받음 */}
                    {this.cmtUpdate(this.state.comments)}
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
                    onChange={this.newComment}
                    value={this.state.comment}
                  />

                  {/* comment추가 이벤트 */}
                  <button className="submitBtn" onClick={this.addComment}>
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
}

export default MainFeed;
