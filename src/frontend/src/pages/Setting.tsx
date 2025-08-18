import Navbar from "../components/Navbar"
import Settingcard from "../components/Settingcard"
import Sidebar from "../components/Sidebar"


const Setting = () => {
  return (
    <>

      <Navbar />
      <div className="flex">
        <Sidebar />
        <Settingcard />
        </div>
      
    </>
  )
}

export default Setting