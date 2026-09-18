import './App.css'
import NavBar from './components/NavBar'
import { Route, Routes } from 'react-router-dom'
import HowItWorksSection from './sections/HowItWorksSection'
import PrivacySection from './sections/Privacy'
import ProductSection from './sections/ProductSection'
import Human from './assets/human'

function App() {
  return (
    <div>
      <header className='site-header'>
        <h1 className='site-title'>Work For It</h1>
      </header>

      <NavBar />

      <div className='human-stage'>
        <h2 className='human-stage-title'>Point your camera. Perform.</h2>
        <Human />
      </div>
      
      <Routes>
        <Route path='/' element={<ProductSection />} />
        <Route path='/how-it-works-section' element={<HowItWorksSection />} />
        <Route path='/privacy-section' element={<PrivacySection />} />
      </Routes>
    </div>  
  )
}

export default App
