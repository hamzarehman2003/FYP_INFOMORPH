// frontend/components/Auth/ProtectedRoute.jsx

"use client";

import { useContext, useEffect } from "react";
import { AuthContext } from "../../context/AuthContext"; // Adjust the path as necessary
import { useRouter } from "next/navigation";
import Header from "../../components/Header"; // Adjust the path as necessary
import { toast } from "react-toastify";

const ProtectedRoute = ({ children }) => {
  const { auth } = useContext(AuthContext);
  const router = useRouter();

  useEffect(() => {
    if (!auth.token) {
      toast.error("You must be logged in to access this page.");
      router.push("/");
    }
  }, [auth.token, router]);

  if (!auth.token) {
    return null; // Optionally, render a loading spinner here
  }

  return (
    <div className="flex flex-col min-h-screen">
      <Header /> {/* Navbar at the top */}
      <main className="flex-1 w-full">
        {children}
      </main>
    </div>
  );
};

export default ProtectedRoute;
