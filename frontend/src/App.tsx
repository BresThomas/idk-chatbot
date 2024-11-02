import React, { useContext, useEffect, useState } from "react";
import { useLogin } from "./hooks/useLogin";
import { AuthContext } from "./contexts/AuthContext";
import ProfileCard from "./components/ProfileCard";

const App: React.FC = () => {
  const { login, isPending, error } = useLogin();
  const { user, authIsReady } = useContext(AuthContext);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simuler un chargement initial
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  if (isLoading || !authIsReady) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <h1 className="text-2xl font-bold">Préparation de l&apos;authentification, veuillez patienter...</h1>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      {user ? (
        <ProfileCard user={user} />
      ) : (
        <div className="text-center">
          {error && <p className="text-red-500 mb-4">{error}</p>}
          <button 
            className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded transition duration-200"
            onClick={login}
            disabled={isPending}
          >
            {isPending ? "Chargement..." : "Se connecter avec GitHub"}
          </button>
        </div>
      )}
    </div>
  );
};

export default App;