import { Routes, Route } from 'react-router-dom'
import { NavBar } from './components/NavBar'
import { Home } from './pages/Home'
import { Weather } from './pages/Weather'
import { Soil } from './pages/Soil'
import { CropAdvisor } from './pages/CropAdvisor'
import { Reports } from './pages/Reports'

export function App() {
  return (
    <div className="min-h-full pb-16">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/soil" element={<Soil />} />
        <Route path="/crops" element={<CropAdvisor />} />
        <Route path="/weather" element={<Weather />} />
        <Route path="/reports" element={<Reports />} />
      </Routes>
      <NavBar />
    </div>
  )
}
