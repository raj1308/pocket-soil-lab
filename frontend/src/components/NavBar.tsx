import { NavLink } from 'react-router-dom'

const TABS = [
  { to: '/', label: 'Home', icon: '🏠' },
  { to: '/soil', label: 'Soil', icon: '🧪' },
  { to: '/crops', label: 'Crops', icon: '🌾' },
  { to: '/weather', label: 'Weather', icon: '⛅' },
  { to: '/reports', label: 'Reports', icon: '📄' },
]

export function NavBar() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-10 border-t border-soil-100 bg-white">
      <ul className="mx-auto flex max-w-md justify-between px-2">
        {TABS.map((tab) => (
          <li key={tab.to} className="flex-1">
            <NavLink
              to={tab.to}
              className={({ isActive }) =>
                `flex flex-col items-center gap-0.5 py-2 text-xs font-medium ${
                  isActive ? 'text-leaf-600' : 'text-soil-500'
                }`
              }
            >
              <span className="text-lg leading-none">{tab.icon}</span>
              {tab.label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  )
}
