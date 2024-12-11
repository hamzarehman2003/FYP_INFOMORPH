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

const Login = () => {
  const router = useRouter();
  const { login } = useContext(AuthContext);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    const result = await login(email, password);
    if (result.success) {
      router.push("/topic-selection");
    } else {
      setError(result.message || "Login failed");
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
            required
          />
        </div>
        {error && <p className="text-red-500 mt-2">{error}</p>}
        <WithOthers name="Log in" />
        <WithGoogle name="Log in" />
        <div className="flex justify-center">
          <BlueButton text="Login" type="submit" />
        </div>
      </form>
    </AuthWrapper>
  );
};

export default Login;
