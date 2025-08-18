import Navbar from "../components/Navbar"
import Sidebar from "../components/Sidebar"
import Supportcard from "../components/Supportcard"


const Support = () => {
  return (
     <>

      <Navbar />
      <div className="flex">
        <Sidebar />
        <Supportcard />
        </div>
      
    </>
  )
}

export default Support