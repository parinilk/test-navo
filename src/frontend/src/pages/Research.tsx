
import { useLocation } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Navbarcredit from "../components/Navbarcredit";
import Researchcard1 from "../components/Researchcard1";
import Researchcard2 from "../components/Researchcard2";

const Research = () => {
  const location = useLocation();

  return (
    <>
      <Navbarcredit />
      <div className="flex">
        <Sidebar />
        {location.pathname === "/researchcard2" ? <Researchcard2 /> : <Researchcard1 />}
      </div>
    </>
  );
};

export default Research;
