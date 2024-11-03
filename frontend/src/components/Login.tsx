import React, { useEffect } from "react";
import { auth } from "../firebase/firebaseConfig";
import {
  signInWithPopup,
  onAuthStateChanged,
  GithubAuthProvider,
} from "firebase/auth";
import { Dispatch, SetStateAction } from "react";
import firebase from "firebase/compat/app";
import { useNavigate } from "react-router-dom";

interface LoginProps {
  onUserChange: Dispatch<SetStateAction<firebase.User | null>>;
  loginText: string;
}

const Login: React.FC<LoginProps> = ({ onUserChange, loginText }) => {
  const navigate = useNavigate();
  const provider = new GithubAuthProvider(); // Utiliser GitHub comme fournisseur

  const handleLogin = async () => {
    try {
      const result = await signInWithPopup(auth, provider);
      console.log(result.user);
      onUserChange(result.user as firebase.User);
      navigate("/dashboard");
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      onUserChange(user as firebase.User);
      if (user) {
        navigate("/dashboard");
      }
    });

    return () => unsubscribe();
  }, [onUserChange, navigate]);

  return (
    <div className="flex items-center justify-center h-screen">
      <button
        style={{
          background: "linear-gradient(120deg, #5391c1, #876bca)",
          color: "white",
        }}
        className="px-4 py-2 text-white rounded"
        onClick={handleLogin}>
        {loginText}
      </button>
    </div>
  );
};

export default Login;
