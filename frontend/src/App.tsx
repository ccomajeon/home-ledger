import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { DashboardPage } from './pages/DashboardPage'
import { NotAuthorizedPage } from './pages/NotAuthorizedPage'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/403" element={<NotAuthorizedPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App
