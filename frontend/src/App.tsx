import { Routes, Route } from 'react-router-dom'
import { NavBar } from './components/NavBar'
import { Home } from './pages/Home'
import { Weather } from './pages/Weather'
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
        <Route path="/weather" element={<Weather />} />
        <Route
          path="/reports"
          element={<PlaceholderPage title="Reports" phase="Phase 8" />}
        />
      </Routes>
      <NavBar />
    </div>
  )
}
