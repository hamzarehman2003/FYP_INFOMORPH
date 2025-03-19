// frontend/src/context/AuthContext.jsx

"use client";

import React, { createContext, useState, useEffect } from "react";
import api from "../../src/app/api"; // Import the configured Axios instance

// Create the context
export const AuthContext = createContext();

// Create the provider component
export const AuthProvider = ({ children }) => {
  const [auth, setAuth] = useState({
    token: null,
    email: null,
  });

  useEffect(() => {
    // Check for token and email in localStorage on mount
    const token = localStorage.getItem("token");
    const email = localStorage.getItem("email");
    if (token && email) {
      setAuth({ token, email });
      api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    }
  }, []);

  const login = async (email, password) => {
    try {
      const params = new URLSearchParams();
      params.append('username', email);
      params.append('password', password);

      const response = await api.post("/token", params, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      const { access_token } = response.data;
      setAuth({ token: access_token, email });
      localStorage.setItem("token", access_token);
      localStorage.setItem("email", email);
      api.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
      return { success: true };
    } catch (error) {
      console.error("Login error:", error.response?.data?.detail || error.message);
      return { success: false, message: error.response?.data?.detail || "Login failed" };
    }
  };

  const signup = async (email, password) => {
    try {
      const response = await api.post("/signup", {
        email,
        password,
      });

      const { access_token } = response.data;
      setAuth({ token: access_token, email });
      localStorage.setItem("token", access_token);
      localStorage.setItem("email", email);
      api.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
      return { success: true };
    } catch (error) {
      console.error("Signup error:", error.response?.data?.detail || error.message);
      return { success: false, message: error.response?.data?.detail || "Signup failed" };
    }
  };

  const logout = () => {
    setAuth({ token: null, email: null });
    localStorage.removeItem("token");
    localStorage.removeItem("email");
    delete api.defaults.headers.common["Authorization"];
    // Optionally, navigate to login page or homepage
  };

  return (
    <AuthContext.Provider value={{ auth, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
};