import { Component } from "react";
import "../pages/Common.css";
import "../pages/InstaMain.css";

import heart from "./Image/heart.png";

class CmtBox extends Component {
  render() {
    return (
      <div className="comment-list" key={this.props.data}>
        <span className="comment-id">_sunghae__</span>
        <span className="comment-text">{this.props.data}</span>
        <img src={heart} />
      </div>
    );
  }
}

export default CmtBox;
