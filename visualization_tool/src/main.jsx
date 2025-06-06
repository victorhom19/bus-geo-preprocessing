import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { useGeographic } from 'ol/proj';

// Using EPSG 4326 (lon, lat) coordinate system
useGeographic();

createRoot(document.getElementById('root')).render(
    <App />
)
