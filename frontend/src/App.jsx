import { BrowserRouter as Router } from "react-router-dom";
import AppRoutes from "./Route"; // 분리된 라우트 파일 임포트
import "./App.css";


function App() {
  return (
    <Router>
      <AppRoutes />
    </Router>
  );
}

export default App;
