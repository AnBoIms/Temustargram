import { Component } from "react";
import "../pages/Common.css";
import "./InstaMain.css";
import MainNav from "../Components/InstaNav";
import MainFeed from "../Components/MainFeed";

class InstaMain extends Component {
  render() {
    return (
      <>
        <MainNav />
        <MainFeed />
      </>
    );
  }
}

export default InstaMain;
