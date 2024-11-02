// src/App.tsx
import React, { useEffect, useState } from 'react';
import { sessionState, useChatSession } from "@chainlit/react-client";
import { useRecoilValue } from "recoil";
import Login from './components/Login';
import { Playground } from "./components/playground";
import { auth } from './firebase/firebaseConfig';
import firebase from 'firebase/compat/app'; // Assurez-vous que cela correspond à votre configuration


const userEnv = {};

function App() {
    const { connect } = useChatSession();
    const session = useRecoilValue(sessionState);
    const [user, setUser] = useState<firebase.User | null>(null); // État pour stocker l'utilisateur

    useEffect(() => {
        if (session?.socket.connected) {
            return;
        }

        if (user) {
            fetch("http://localhost:80/custom-auth")
                .then((res) => res.json())
                .then((data) => {
                    connect({
                        userEnv,
                        accessToken: `Bearer: ${data.token}`,
                    });
                });
        }
    }, [connect, session, user]);

    const handleLogout = async () => {
        try {
            await auth.signOut(); // Déconnexion de Firebase
            setUser(null); // Réinitialiser l'état utilisateur
        } catch (error) {
            console.error('Error signing out: ', error);
        }
    };

    return (
        <>
            <div>
                {!user ? (
                    <Login onUserChange={setUser} />
                ) : (
                    <Playground onLogout={handleLogout} />
                )}
            </div>
        </>
    );
}

export default App;