// src/components/Login.tsx
import React, { useEffect } from 'react';
import { auth, provider } from '../firebase/firebaseConfig';
import { signInWithPopup, onAuthStateChanged } from 'firebase/auth';
import { Dispatch, SetStateAction } from 'react';
import firebase from 'firebase/compat/app';

interface LoginProps {
    onUserChange: Dispatch<SetStateAction<firebase.User | null>>;
  }

const Login: React.FC<LoginProps> = ({ onUserChange }) => {
    const handleLogin = async () => {
        try {
            const result = await signInWithPopup(auth, provider);
            console.log(result.user);
            onUserChange(result.user as firebase.User); // Appel de la fonction de mise à jour de l'utilisateur
        } catch (error) {
            console.error(error);
        }
    };

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, (user) => {
            onUserChange(user as firebase.User); // Mettez à jour l'état de l'utilisateur lors des changements
        });

        return () => unsubscribe(); // Nettoyer l'abonnement à la déconnexion
    }, [onUserChange]);

    return (
        <div className="flex items-center justify-center h-screen">
            <button
                className="px-4 py-2 text-white bg-blue-600 rounded"
                onClick={handleLogin}>
                Login with GitHub
            </button>
        </div>
    );
};

export default Login;
