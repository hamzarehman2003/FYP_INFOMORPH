"use client";

import React, { createContext, useState, useEffect } from "react";
import axios from "axios";

// Create the context
export const AuthContext = createContext();

// Create the provider component
export const AuthProvider = ({ children }) => {
  const [auth, setAuth] = useState({
    token: null,
    email: null,
  });

  useEffect(() => {
    // Check for token in localStorage on mount
    const token = localStorage.getItem("token");
    const email = localStorage.getItem("email");
    if (token && email) {
      setAuth({ token, email });
    }
  }, []);

  const login = async (email, password) => {
    try {
      const response = await axios.post("http://localhost:8000/token", {
        username: email,
        password: password,
      }, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      const { access_token } = response.data;
      setAuth({ token: access_token, email });
      localStorage.setItem("token", access_token);
      localStorage.setItem("email", email);
      return { success: true };
    } catch (error) {
      console.error("Login error:", error.response?.data?.detail || error.message);
      return { success: false, message: error.response?.data?.detail || "Login failed" };
    }
  };

  const signup = async (email, password) => {
    try {
      const response = await axios.post("http://localhost:8000/signup", {
        email,
        password,
      });

      const { access_token } = response.data;
      setAuth({ token: access_token, email });
      localStorage.setItem("token", access_token);
      localStorage.setItem("email", email);
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
  };

  return (
    <AuthContext.Provider value={{ auth, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
