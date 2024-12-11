import { Routes, Route } from "react-router-dom";
import ImageUpload from "./components/ImageUpload";
import Select from "./components/Select";
import Output from "./components/Output";
import InstaMain from "./insta/pages/InstaMain"; // insta 관련 컴포넌트 임포트
import GptMain from "./gpt/src/GptMain"; // insta 관련 컴포넌트 임포트
import OutputPage from "./insta/Components/OutputPage";

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<ImageUpload />} />
      <Route path="/select" element={<Select />} />
      <Route path="/output" element={<Output />} />
      <Route path="/instaMain" element={<InstaMain />} /> {/* insta 메인 경로 추가 */}
      <Route path="/instaOutput" element={<OutputPage />} /> {/* insta 메인 경로 추가 */}
    </Routes>
  );
};

export default AppRoutes;
