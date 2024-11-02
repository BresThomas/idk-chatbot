import React from "react";
import Navbar from "./ui/navbar";
import firebase from "firebase/compat/app";
import Hero12 from "./ui/hero-section";

interface LandingPageProps {
  setUser: React.Dispatch<React.SetStateAction<firebase.User | null>>;
}

const LandingPage: React.FC<LandingPageProps> = ({ setUser }) => {
  return (
    <div className='min-h-screen'>
      <Navbar setUser={setUser} />
      <Hero12 />
      <footer className='bg-[#344D59] text-white py-4'>
        <div className='container mx-auto text-center'>
          <p>&copy; 2023 Your Company. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
