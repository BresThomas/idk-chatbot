import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { sessionState, useChatSession } from "@chainlit/react-client";
import { useRecoilValue } from "recoil";
import { Playground } from "./components/playground";
import { auth } from "./firebase/firebaseConfig";
import firebase from "firebase/compat/app";
import { SidebarProvider } from "./components/ui/sidebar";
import { AppSidebar } from "./components/ui/app-sidebar";
import LandingPage from "./components/Landing-Page";

const userEnv = {}; // Configure userEnv here if necessary

function App() {
  const { connect } = useChatSession();
  const session = useRecoilValue(sessionState);
  const [user, setUser] = useState<firebase.User | null>(null);

  // Connect to the API once the user is connected and the session is ready
  useEffect(() => {
    const connectChatSession = async () => {
      if (!session?.socket.connected && user) {
        try {
          const response = await fetch("http://localhost:80/custom-auth");
          const data = await response.json();
          connect({
            userEnv,
            accessToken: `Bearer ${data.token}`, // Note the space after "Bearer"
          });
        } catch (error) {
          console.error("Error connecting to chat session: ", error);
        }
      }
    };
    
    connectChatSession();
  }, [connect, session, user]);

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
