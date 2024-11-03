import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { sessionState, useChatSession } from "@chainlit/react-client";
import { useRecoilValue } from "recoil";
import { Playground } from "./components/playground";
import { auth } from "@/firebase/firebaseConfig";
import firebase from "firebase/compat/app";
import { SidebarProvider } from "./components/ui/sidebar";
import { AppSidebar } from "./components/ui/app-sidebar";
import LandingPage from "./components/Landing-Page";

const userEnv = {}; // Configure userEnv here if necessary

function App() {
  const [user, setUser] = useState<firebase.User | null>(null);

  const { connect } = useChatSession();
  const session = useRecoilValue(sessionState);
  useEffect(() => {
    if (session?.socket.connected) {
      return;
    }
    fetch("http://localhost:80/custom-auth")
      .then((res) => {
        return res.json();
      })
      .then((data) => {
        connect({
          userEnv,
          accessToken: `Bearer: ${data.token}`,
        });
      });
  }, [connect]);

  // Handle logout
  const handleLogout = async () => {
    try {
      await auth.signOut();
      setUser(null);
    } catch (error) {
      console.error("Error during logout: ", error);
    }
  };

  return (
    <Router>
      <Routes>
        {/* Home page */}
        <Route path="/" element={<LandingPage setUser={setUser} />} />

        {/* Protected route: dashboard */}
        <Route
          path="/dashboard"
          element={
            user ? (
              <SidebarProvider>
                <AppSidebar onLogout={handleLogout} />
                <main className="w-screen">
                  <Playground />
                </main>
              </SidebarProvider>
            ) : (
              <Navigate to="/" replace />
            )
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
