import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

import Dashboard from './pages/Dashboard';
import Research from './pages/Research';
import Report from './pages/Report';
import Saved from './pages/Saved';
import Setting from './pages/Setting';
import Support from './pages/Support';
import ResearchResults from './pages/ResearchResults';
import Login from './pages/Login';
import Signup from './pages/Signup';
import ProtectedRoute from './components/ProtectedRoute';
import SessionDebugger from './components/SessionDebugger';
import { AuthProvider } from './contexts/AuthContext';



function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="flex">
          <main className="flex-1 h-screen overflow-auto">
            <Routes>
              <Route path="/" element={<Navigate to="/login" />} />
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="/dashboard" element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } />
              <Route path="/research" element={
                <ProtectedRoute>
                  <Research />
                </ProtectedRoute>
              } />
              <Route path="/researchcard2" element={
                <ProtectedRoute>
                  <Research />
                </ProtectedRoute>
              } />
              <Route path="/research-results" element={
                <ProtectedRoute>
                  <ResearchResults />
                </ProtectedRoute>
              } />
              <Route path="/report" element={
                <ProtectedRoute>
                  <Report />
                </ProtectedRoute>
              } />
              <Route path="/reportcard" element={
                <ProtectedRoute>
                  <Report />
                </ProtectedRoute>
              } />
              <Route path="/saved" element={
                <ProtectedRoute>
                  <Saved />
                </ProtectedRoute>
              } />
              <Route path="/support" element={
                <ProtectedRoute>
                  <Support />
                </ProtectedRoute>
              } />
              <Route path="/setting" element={
                <ProtectedRoute>
                  <Setting />
                </ProtectedRoute>
              } />
            </Routes>
          </main>
          {/* Session Debugger - only show in development */}
          {import.meta.env.DEV && <SessionDebugger />}
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
