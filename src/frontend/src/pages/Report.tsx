
import { useLocation } from "react-router-dom"
import Navbarcredit from "../components/Navbarcredit"
import Reportcard from "../components/Reportcard"
import Sidebar from "../components/Sidebar"
import Reportcardmain from "../components/Reportcardmain"


const Report = () => {
  const location = useLocation();
  return (
    <>
  
      <Navbarcredit />
      <div className="flex">
        <Sidebar />
        
        {location.pathname === "/report" ? <Reportcardmain/> : <Reportcard />}
        </div>
      
    </>
  )
}

export default Report