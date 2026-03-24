import { Routes, Route, Link } from 'react-router-dom';
import './index.css';
import Dashboard from './pages/Dashboard';
import Projects from './pages/Projects';
import Notes from './pages/Notes';
import Images from './pages/Images';

function App() {
  return (
    <div className="min-h-screen bg-gray-900 text-white flex">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-800 p-4">
        <h2 className="text-xl font-bold mb-4">Navigation</h2>
        <nav>
          <ul>
            <li className="mb-2">
              <Link to="/" className="block p-2 rounded hover:bg-gray-700">Dashboard</Link>
            </li>
            <li className="mb-2">
              <Link to="/projects" className="block p-2 rounded hover:bg-gray-700">Projects</Link>
            </li>
            <li className="mb-2">
              <Link to="/notes" className="block p-2 rounded hover:bg-gray-700">Notes</Link>
            </li>
            <li className="mb-2">
              <Link to="/images" className="block p-2 rounded hover:bg-gray-700">Images</Link>
            </li>
          </ul>
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-4">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/notes" element={<Notes />} />
          <Route path="/images" element={<Images />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
