import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { useWebSocket } from './hooks/useWebSocket';
import { Overview } from './pages/Overview';
import { PipelineFlow } from './pages/PipelineFlow';
import { ComponentDetail } from './pages/ComponentDetail';
import { RunDetail } from './pages/RunDetail';
import './App.css';

function AppShell() {
  useWebSocket();

  return (
    <div className="app-shell">
      <nav className="app-nav">
        <NavLink to="/" className="app-nav__brand" end>
          Forge
        </NavLink>
        <div className="app-nav__links">
          <NavLink to="/" end className={({ isActive }) => isActive ? 'app-nav__link app-nav__link--active' : 'app-nav__link'}>
            Overview
          </NavLink>
          <NavLink to="/pipeline" className={({ isActive }) => isActive ? 'app-nav__link app-nav__link--active' : 'app-nav__link'}>
            Pipeline
          </NavLink>
        </div>
      </nav>
      <main className="app-main">
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/pipeline" element={<PipelineFlow />} />
          <Route path="/components/:name" element={<ComponentDetail />} />
          <Route path="/components/:name/runs/:id" element={<RunDetail />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppShell />
    </BrowserRouter>
  );
}

export default App;
