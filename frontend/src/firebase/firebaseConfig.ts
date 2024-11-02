// firebaseConfig.js
import { initializeApp } from 'firebase/app';
import { getAuth, GithubAuthProvider } from 'firebase/auth';

const firebaseConfig = {
    apiKey: "AIzaSyCOvPctaZQNBbFD1BQvM0Bwmsd5wqxd0yY",
    authDomain: "idk-chat-bd017.firebaseapp.com",
    projectId: "idk-chat-bd017",
    storageBucket: "idk-chat-bd017.firebasestorage.app",
    messagingSenderId: "63946407621",
    appId: "1:63946407621:web:65dfbff78cb9eddcf5faac"
  };

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GithubAuthProvider();

export { auth, provider };
