import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import BrowserChrome from './components/BrowserChrome';
import Home from './pages/Home';
import About from './pages/About';
import Economy from './pages/Economy';

export default function App() {
  return (
    <BrowserRouter>
      <BrowserChrome>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/economy" element={<Economy />} />
          {/* Fallback — redirect unknown paths to home */}
          <Route path="*" element={<Home />} />
        </Routes>
      </BrowserChrome>
    </BrowserRouter>
  );
}
