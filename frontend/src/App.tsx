import { Routes, Route } from 'react-router-dom'
import { NavBar } from './components/NavBar'
import { Home } from './pages/Home'
import { PlaceholderPage } from './pages/PlaceholderPage'

export function App() {
  return (
    <div className="min-h-full pb-16">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route
          path="/soil"
          element={<PlaceholderPage title="Soil Analysis" phase="Phase 3" />}
        />
        <Route
          path="/crops"
          element={<PlaceholderPage title="Crop Advisor" phase="Phase 4" />}
        />
        <Route
          path="/weather"
          element={<PlaceholderPage title="Weather" phase="Phase 2" />}
        />
        <Route
          path="/reports"
          element={<PlaceholderPage title="Reports" phase="Phase 8" />}
        />
      </Routes>
      <NavBar />
    </div>
  )
}
