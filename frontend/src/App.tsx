import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Header } from './components/layout/Header'
import { Sidebar } from './components/layout/Sidebar'
import { ChatPage } from './components/chat/ChatPage'
import { DocumentManager } from './components/documents/DocumentManager'
import { GraphExplorer } from './components/graph/GraphExplorer'

function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-surface text-text overflow-hidden">
        <Sidebar />
        <div className="flex-1 flex flex-col h-full overflow-hidden relative">
          <Header />
          <main className="flex-1 overflow-auto relative">
            <Routes>
              <Route path="/" element={<Navigate to="/chat" replace />} />
              <Route path="/chat" element={<ChatPage />} />
              <Route path="/documents" element={<DocumentManager />} />
              <Route path="/graph" element={<GraphExplorer />} />
              {/* Other routes will go here in later phases */}
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App
