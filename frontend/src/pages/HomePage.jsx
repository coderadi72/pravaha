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
import AuthModal from "../components/auth/AuthModal.jsx";
import { useState } from "react";

function HomePage({ onAuthenticated }) {
  const [authPortal, setAuthPortal] = useState(null);
  const [signup, setSignup] = useState(false);
  const openAuth = (portal = "management") => { setSignup(false); setAuthPortal(portal); };
  const openSignup = () => { setSignup(true); setAuthPortal("management"); };
  return (
    <div className="app">
      <Navbar onOpenAuth={openAuth} onOpenSignup={openSignup} />

      <main>
        <Hero onDemoStart={() => openAuth("management")} />
        <Features />
        <Analytics />
        <HowItWorks />
        <Intelligence />
        <KnowledgeBase />
        <FinalCTA onDemoStart={() => openAuth("management")} />
      </main>

      <Footer onOpenAuth={openAuth} />
      <AuthModal isOpen={Boolean(authPortal)} role={authPortal} signup={signup} onOpenSignin={() => setSignup(false)} onClose={() => { setAuthPortal(null); setSignup(false); }} onAuthenticated={onAuthenticated} />
    </div>
  );
}

export default HomePage;
