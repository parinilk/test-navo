

import Draftcard from '../components/Draftcard'
import Navbar from '../components/Navbar'
import Sidebar from '../components/Sidebar'


const Dashboard = () => {
  return (
    <>

      <Navbar />
      <div className="flex">
        <Sidebar />
        <Draftcard />
        </div>
      
    </>
  )
}

export default Dashboard


