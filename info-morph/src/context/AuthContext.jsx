"use client";

import React, { createContext, useState, useEffect } from "react";
import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

const supabase = createClient(supabaseUrl, supabaseAnonKey);

console.log("Supabase URL:", supabaseUrl);
console.log("Supabase Anon Key:", supabaseAnonKey);
if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error("Supabase environment variables are missing.");
}

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  // Initialize auth state with null token
  const [auth, setAuth] = useState({ token: null });

  useEffect(() => {
    const checkSession = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();

        // Only set auth token if session exists and has a valid access_token
        if (session && session.access_token) {
          setUser(session.user || null);
          setAuth({ token: session.access_token });
          console.log("Session found, user is authenticated");
        } else {
          console.log("No active session found");
          // Ensure auth state is cleared if no session
          setAuth({ token: null });
          setUser(null);
        }
      } catch (error) {
        console.error("Error checking session:", error);
        // Ensure auth state is cleared on error
        setAuth({ token: null });
      } finally {
        setLoading(false);
      }

      const { data: { subscription } } = supabase.auth.onAuthStateChange(
        (event, session) => {
          console.log("Auth state changed:", event);
          setUser(session?.user || null);
          setAuth({ token: session?.access_token || null });
        }
      );

      return () => subscription?.unsubscribe();
    };

    checkSession();
  }, []);

  const signup = async (email, password, name) => {
    try {
      // First, sign up the user with Supabase Auth
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: { data: { name } }
      });

      if (error) throw error;

      // If signup successful, create user record in Users table
      if (data.user) {
        const { error: userError } = await supabase
          .from('Users')
          .insert([
            {
              id: data.user.id,
              name: name,
              email: email, // add email here
            }
          ]);
      
        if (userError) throw userError;
      }
      

      setAuth({ token: data.session?.access_token || null });
      return { success: true, user: data.user };
    } catch (error) {
      console.error("Signup error:", error.message);
      return { success: false, message: error.message };
    }
  };

  const login = async (email, password) => {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({ email, password });

      if (error) throw error;

      setAuth({ token: data.session?.access_token || null });

      return { success: true, user: data.user };
    } catch (error) {
      console.error("Login error:", error.message);
      return { success: false, message: error.message };
    }
  };

  const logout = async () => {
    try {
      const { error } = await supabase.auth.signOut();
  
      if (error) throw error;
  
      setAuth({ token: null });
      setUser(null);
  
      return { success: true };
    } catch (error) {
      console.error("Logout error:", error.message);
      return { success: false, message: error.message };
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, auth, signup, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
