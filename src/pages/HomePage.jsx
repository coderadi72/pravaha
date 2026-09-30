import "../styles/global.css";

import Navbar from "../components/layout/Navbar";
import Hero from "../components/home/Hero";
import Features from "../components/home/Features";
import Analytics from "../components/home/Analytics";
import HowItWorks from "../components/home/HowItWorks";
import Intelligence from "../components/home/Intelligence";
import KnowledgeBase from "../components/home/KnowledgeBase";
import FinalCTA from "../components/home/FinalCTA";
import Footer from "../components/layout/Footer";

function HomePage() {
  return (
    <div className="app">
      <Navbar />

      <main>
        <Hero />
        <Features />
        <Analytics />
        <HowItWorks />
        <Intelligence />
        <KnowledgeBase />
        <FinalCTA />
      </main>

      <Footer />
    </div>
  );
}

export default HomePage;