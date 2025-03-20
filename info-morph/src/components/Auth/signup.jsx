"use client";

import { useState, useContext } from "react";
import Heading from "./heading";
import InputField from "./inputfield";
import AuthWrapper from "./wrapper";
import WithOthers from "./withOthers";
import WithGoogle from "./withGoogle";
import BlueButton from "./blueButton";
import { AuthContext } from "../../context/AuthContext"; // Adjust path as needed
import { useRouter } from "next/navigation";
import { toast } from 'react-toastify'; // Import toast from react-toastify

const Signup = () => {
  const { signup } = useContext(AuthContext);
  const router = useRouter();
  const [name, setName] = useState("");  // Add state for name
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [retypePassword, setRetypePassword] = useState("");

  const handleSignup = async (e) => {
    e.preventDefault();

    if (!name.trim()) {
      toast.error("Please enter your name");
      return;
    }

    if (password !== retypePassword) {
      toast.error("Passwords do not match");
      return;
    }

    // Password strength validation
    const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/;
    if (!passwordRegex.test(password)) {
      toast.error("Password must be at least 8 characters long and contain both letters and numbers");
      return;
    }

    const result = await signup(email, password, name); // Pass name to signup function
    if (result.success) {
      toast.success("Signed up successfully!");
      router.push("/topic-selection");
    } else {
      toast.error(result.message || "Signup failed. Please try again.");
    }
  };

  return (
    <AuthWrapper>
      <Heading heading={"Get Started Now"} className={"mb-10"} />
      <form onSubmit={handleSignup}>
        <div className="max-w-[364px] w-full flex flex-col gap-7">
          <InputField
            value={name}
            onChange={(e) => setName(e.target.value)}
            name={"name"}
            placeholder={"Full Name"}
            type={"text"}
            required
          />
          <InputField
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            name={"email"}
            placeholder={"Email"}
            type={"email"}
            required
          />
          <InputField
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            name={"password"}
            placeholder={"Password"}
            type={"password"}
            autocomplete="new-password"
            required
          />
          <InputField
            value={retypePassword}
            onChange={(e) => setRetypePassword(e.target.value)}
            name={"retypePassword"}
            placeholder={"Retype Password"}
            type={"password"}
            autocomplete="new-password"
            required
          />
        </div>
        <WithOthers name={"Sign up"} />
        <WithGoogle name={"Sign up"} />
        <div className="flex justify-center">
          <BlueButton text={"Sign Up"} type="submit" />
        </div>
      </form>
    </AuthWrapper>
  );
};

export default Signup;
