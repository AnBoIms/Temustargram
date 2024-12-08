import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Main from "./pages/InstaMain";

class RoutesComponent extends React.Component {
  render() {
    return (
      <Router>
        <Routes>
          {/* <Route path="/" element={<Login />} /> */}
          <Route path="/" element={<Main />} />
        </Routes>
      </Router>
    );
  }
}

export default RoutesComponent;
