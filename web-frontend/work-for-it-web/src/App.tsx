import './App.css'
import NavBar from './components/NavBar'
import { Route, Routes } from 'react-router-dom'

function SectionPage({ title }: { title: string }) {
  return (
    <main>
      <h1>{title}</h1>
    </main>
  )
}

function App() {
  return (
    <div className='nav-header'>
      <NavBar />
      <Routes>
        <Route path='/product-section' element={<SectionPage title='Product' />} />
        <Route path='/how-it-works-section' element={<SectionPage title='How it Works' />} />
        <Route path='/privacy-section' element={<SectionPage title='Privacy' />} />
      </Routes>
    </div>  
  )
}

export default App
