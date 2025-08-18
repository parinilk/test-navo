
import Navbarcredit from "../components/Navbarcredit"
import Saveddata from "../components/Saveddata"
import Sidebar from "../components/Sidebar"


const Saved = () => {
  return (
    <>

      <Navbarcredit />
      <div className="flex">
        <Sidebar />
        <Saveddata />
      </div>

    </>
  )
}

export default Saved
