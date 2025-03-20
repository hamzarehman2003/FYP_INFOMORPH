// frontend/src/components/Auth/Login.jsx

"use client";

import { useRouter } from "next/navigation";
import Heading from "./heading";
import InputField from "./inputfield";
import AuthWrapper from "./wrapper";
import WithOthers from "./withOthers";
import WithGoogle from "./withGoogle";
import BlueButton from "./blueButton";
import { useContext, useState } from "react";
import { AuthContext } from "../../context/AuthContext"; // Adjust path as needed
import { toast } from 'react-toastify'; // Import toast from react-toastify

const Login = () => {
  const router = useRouter();
  const { login } = useContext(AuthContext);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      // Make sure your login function is using Supabase's built-in auth methods
      const result = await login(email, password);
      if (result.success) {
        toast.success("Logged in successfully!");
        router.push("/topic-selection");
      } else {
        toast.error(result.message || "Login failed. Please try again.");
      }
    } catch (error) {
      console.error("Login error:", error);
      // More specific error handling based on the error response
      if (error.response?.status === 501) {
        toast.error("Authentication service is not properly configured. Please contact support.");
      } else {
        toast.error(error.response?.data?.message || "An unexpected error occurred during login.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthWrapper>
      <Heading heading="Continue on" className="mb-10" />
      <form onSubmit={handleLogin}>
        <div className="w-[364px] flex flex-col gap-7">
          <InputField
            name="email"
            placeholder="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <InputField
            name="password"
            placeholder="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autocomplete="current-password"
            required
          />
        </div>
        <WithOthers name="Log in" />
        <WithGoogle name="Log in" />
        <div className="flex justify-center">
          <BlueButton text={isLoading ? "Logging in..." : "Login"} type="submit" disabled={isLoading} />
        </div>
      </form>
    </AuthWrapper>
  );
};

export default Login;
