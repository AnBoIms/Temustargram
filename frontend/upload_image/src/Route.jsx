import { Routes, Route } from "react-router-dom";
import ImageUpload from "./components/ImageUpload";
import Select from "./components/Select";
import Output from "./components/Output";
import InstaMain from "./insta/pages/InstaMain"; // insta 관련 컴포넌트 임포트

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<ImageUpload />} />
      <Route path="/select" element={<Select />} />
      <Route path="/output" element={<Output />} />
      <Route path="/insta" element={<InstaMain />} /> {/* insta 메인 경로 추가 */}
    </Routes>
  );
};

export default AppRoutes;
