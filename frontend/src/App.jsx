import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './index.css';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Register from './pages/Register';
import Matches from './pages/Matches';
import Verify from './pages/Verify';
import Contracts from './pages/Contracts';

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Navbar />
        <main className="page-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/register" element={<Register />} />
            <Route path="/matches" element={<Matches />} />
            <Route path="/verify" element={<Verify />} />
            <Route path="/contracts" element={<Contracts />} />
          </Routes>
        </main>

        <footer style={{
          borderTop: '1px solid var(--color-border)',
          padding: '24px',
          textAlign: 'center',
          fontSize: '12px',
          color: 'var(--color-text-dim)',
        }}>
          🇮🇳 MSE Agent Mapping Tool · Built for the MSME TEAM Initiative ·
          ONDC-Ready · DPI-Compliant ·&nbsp;
          <span style={{ color: 'var(--color-saffron)' }}>Powered by Groq Whisper + Gemini AI + Supabase</span>
        </footer>
      </div>
    </BrowserRouter>
  );
}
