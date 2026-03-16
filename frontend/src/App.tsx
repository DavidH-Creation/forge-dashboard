import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
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
        <Link to="/" className="app-nav__brand">
          Forge
        </Link>
        <div className="app-nav__links">
          <Link to="/">Overview</Link>
          <Link to="/pipeline">Pipeline</Link>
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
