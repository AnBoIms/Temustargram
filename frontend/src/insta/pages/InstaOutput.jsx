import { Component } from "react";
import "../pages/Common.css";
import "./InstaMain.css";
import MainNav from "../Components/InstaNav";
import OutputFeed from "../Components/OutputPage";

class InstaOutput extends Component {
  render() {
    return (
      <>
        <MainNav />
        <OutputFeed />
      </>
    );
  }
}

export default InstaOutput;
