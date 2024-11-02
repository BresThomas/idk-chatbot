import { useState } from 'react';
import { signInWithPopup } from 'firebase/auth';
import { auth, githubProvider } from '../firebase/firebaseConfig';

export const useLogin = () => {
  const [error, setError] = useState<string | null>(null);
  const [isPending, setIsPending] = useState(false);

  const login = async () => {
    setError(null);
    setIsPending(true);

    try {
      const res = await signInWithPopup(auth, githubProvider);
      if (!res) {
        throw new Error('Could not complete signup');
      }
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unknown error occurred');
      }
      console.error('Login error:', err);
    } finally {
      setIsPending(false);
    }
  };

  return { login, error, isPending };
};