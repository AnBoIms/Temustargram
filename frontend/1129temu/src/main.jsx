// import React from "react";
import ReactDOM from "react-dom/client";  // react-dom/client로 import
import "./index.css";
import Routes from "./Route";

// createRoot를 사용하여 렌더링
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<Routes />);
