import React from 'react';
import { User } from 'firebase/auth';
import { useLogout } from '../hooks/useLogout';

interface ProfileCardProps {
  user: User;
}

const ProfileCard: React.FC<ProfileCardProps> = ({ user }) => {
  const { logout, isPending } = useLogout();

  return (
    <div className="bg-white shadow-md rounded-lg p-6 max-w-sm mx-auto mt-10">
      <img src={user.photoURL || '/placeholder.svg?height=100&width=100'} alt="Profile" className="w-24 h-24 rounded-full mx-auto mb-4" />
      <h2 className="text-2xl font-bold text-center mb-2">{user.displayName}</h2>
      <p className="text-gray-600 text-center mb-4">{user.email}</p>
      <button 
        onClick={logout} 
        className="w-full bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600 transition duration-200"
        disabled={isPending}
      >
        {isPending ? 'Déconnexion...' : 'Se déconnecter'}
      </button>
    </div>
  );
};

export default ProfileCard;