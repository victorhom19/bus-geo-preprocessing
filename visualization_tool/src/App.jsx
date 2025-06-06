import './App.css'
import InfoPanel from './components/InfoPanel'
import MapContainer from './components/MapContainer'
import Toolbar from './components/Toolbar'

function App() {
    
    return (
        <div className='ContentWrapper'>
            <Toolbar/>
            <div className='HorizontalWrapper'>
                <MapContainer/>
                <InfoPanel/>
            </div>
        </div>
    )
}

export default App
