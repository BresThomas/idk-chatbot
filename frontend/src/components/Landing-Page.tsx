import React from "react";
import Navbar from "./ui/navbar";
import firebase from "firebase/compat/app";
import Hero12 from "./ui/hero-section";

interface LandingPageProps {
  setUser: React.Dispatch<React.SetStateAction<firebase.User | null>>;
}

const LandingPage: React.FC<LandingPageProps> = ({ setUser }) => {
  return (
    <div className="min-h-screen flex flex-1 flex-col">
      <Navbar setUser={setUser} />
      <Hero12 />
      <footer className="bg-[#000000]/85 text-white py-4 mt-auto">
        <div className="container mx-auto text-center">
          <p>&copy; 2024 I don't know. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
