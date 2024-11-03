// src/pages/SettingsPage.tsx
import React, { useEffect, useState } from "react";
import { auth } from "@/firebase/firebaseConfig"; // Assurez-vous d'importer votre configuration Firebase

const SettingsPage = () => {
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const user = auth.currentUser;

  useEffect(() => {
    if (user) {
      // Récupérez le nom d'affichage et l'email de l'utilisateur
      setDisplayName(user.displayName || "Nom non défini");
      setEmail(user.email || "Email non défini");
    }
  }, [user]);

  return (
    <div className="max-w-md mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Settings</h1>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Display Name
          </label>
          <p className="mt-1 block w-full border border-gray-300 rounded-md p-2 bg-gray-100">
            {displayName}
          </p>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Email
          </label>
          <p className="mt-1 block w-full border border-gray-300 rounded-md p-2 bg-gray-100">
            {email}
          </p>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
