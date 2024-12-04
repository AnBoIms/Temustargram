import ImageUpload from './components/ImageUpload';
import MainNav from './components/MainNav';
import './App.css';
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Select from './components/Select'; 
import Output from './components/Output'; 


function App() {
  return (
    <Router>
      <MainNav />
      <Routes>
        <Route path="/" element={<ImageUpload />} />
        <Route path="/select" element={<Select />} /> {/* 업로드 성공 후 리디렉션할 경로 */}
        <Route path="/output" element={<Output />} /> {/* 업로드 성공 후 리디렉션할 경로 */}

      </Routes>
    </Router>
  );
}

export default App;
