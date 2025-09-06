

import DynamicDashboard from '../components/DynamicDashboard'
import Navbar from '../components/Navbar'
import Sidebar from '../components/Sidebar'


const Dashboard = () => {
  return (
    <>

      <Navbar />
      <div className="flex">
        <Sidebar />
        <DynamicDashboard />
        </div>
      
    </>
  )
}

export default Dashboard


