import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';


import Dashboard from './pages/Dashboard';
import Research from './pages/Research';
import Report from './pages/Report';
import Saved from './pages/Saved';
import Setting from './pages/Setting';
import Support from './pages/Support';
import ResearchResults from './pages/ResearchResults';



function App() {
  return (
    <Router>
      <div className="flex">
        <main className="flex-1 h-screen overflow-auto">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/research" element={<Research />} />
            <Route path="/researchcard2" element={<Research />} />
            <Route path="/research-results" element={<ResearchResults />} />
            <Route path="/report" element={<Report />} />
            <Route path="/reportcard" element={<Report />} />
            <Route path="/saved" element={<Saved />} />
            <Route path="/support" element={<Support />} />
            <Route path="/setting" element={<Setting />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
