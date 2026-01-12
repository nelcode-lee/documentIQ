import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Chat from './pages/Chat';
import Documents from './pages/Documents';
import Upload from './pages/Upload';
import Generate from './pages/Generate';
import Analytics from './pages/Analytics';

function App() {
  return (
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/chat" replace />} />
          <Route path="chat" element={<Chat />} />
          <Route path="documents" element={<Documents />} />
          <Route path="documents/upload" element={<Upload />} />
          <Route path="generate" element={<Generate />} />
          <Route path="analytics" element={<Analytics />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
