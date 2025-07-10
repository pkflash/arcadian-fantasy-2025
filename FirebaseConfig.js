// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyCd_nhVsJQYFRGk63jnfJtW_7hQm5QUxLk",
  authDomain: "norcal-ua-2025.firebaseapp.com",
  projectId: "norcal-ua-2025",
  storageBucket: "norcal-ua-2025.firebasestorage.app",
  messagingSenderId: "539848644882",
  appId: "1:539848644882:web:1c5cd0a48bce34961a3bcb",
  measurementId: "G-QPBM3EJ6SE"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);