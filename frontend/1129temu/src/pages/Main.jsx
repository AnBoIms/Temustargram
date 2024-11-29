import { Component } from "react";
import "../pages/Common.css";
import "./Main.css";
import MainNav from "../Components/MainNav";
import MainFeed from "../Components/MainFeed";

class Main extends Component {
  render() {
    return (
      <>
        <MainNav />
        <MainFeed />
      </>
    );
  }
}

export default Main;
