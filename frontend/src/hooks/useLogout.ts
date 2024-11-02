import { useState } from 'react';
import { signOut } from 'firebase/auth';
import { auth } from '../firebase/firebaseConfig';

export const useLogout = () => {
  const [error, setError] = useState<string | null>(null);
  const [isPending, setIsPending] = useState(false);

  const logout = async () => {
    setError(null);
    setIsPending(true);

    try {
      await signOut(auth);
      setIsPending(false);
    } catch (err) {
      if (err instanceof Error) {
        console.log(err.message);
        setError(err.message);
      } else {
        console.log(String(err));
        setError(String(err));
      }
      setIsPending(false);
    }
  };

  return { logout, error, isPending };
};