import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import { Overview } from './pages/Overview'
import { ResearchAnalytics } from './pages/ResearchAnalytics'
import { NetworkExplorer } from './pages/NetworkExplorer'
import { CommunityAnalysis } from './pages/CommunityAnalysis'
import { ThresholdSensitivity } from './pages/ThresholdSensitivity'
import { PeerDiscussion } from './pages/PeerDiscussion'
import { AcademicInsights } from './pages/AcademicInsights'
import { ExploreElectives } from './pages/ExploreElectives'
import { ElectiveDetail } from './pages/ElectiveDetail'
import { ElectiveFinder } from './pages/ElectiveFinder'
import { CompareElectives } from './pages/CompareElectives'
import { MyPlanner } from './pages/MyPlanner'
import { LearningMaterials } from './pages/LearningMaterials'
import { About } from './pages/About'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Overview />} />
          <Route path="/analytics" element={<ResearchAnalytics />} />
          <Route path="/network" element={<NetworkExplorer />} />
          <Route path="/communities" element={<CommunityAnalysis />} />
          <Route path="/threshold" element={<ThresholdSensitivity />} />
          <Route path="/peer-discussion" element={<PeerDiscussion />} />
          <Route path="/academic" element={<AcademicInsights />} />
          <Route path="/electives" element={<ExploreElectives />} />
          <Route path="/electives/:id" element={<ElectiveDetail />} />
          <Route path="/finder" element={<ElectiveFinder />} />
          <Route path="/compare" element={<CompareElectives />} />
          <Route path="/planner" element={<MyPlanner />} />
          <Route path="/materials" element={<LearningMaterials />} />
          <Route path="/about" element={<About />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
