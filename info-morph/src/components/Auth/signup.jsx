"use client";
import { useState } from "react";
import Heading from "./heading";
import InputField from "./inputfield";
import AuthWrapper from "./wrapper";
import WithOthers from "./withOthers";
import WithGoogle from "./withGoogle";
import BlueButton from "./blueButton";

const Signup = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [retypePassword, setRetypePassword] = useState("");
  return (
    <AuthWrapper>
      <Heading heading={"Get Started Now"} className={"mb-10"} />
      <div className="max-w-[364px] w-full flex flex-col gap-7">
        <InputField
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          name={"email"}
          placeholder={"Email"}
          type={"text"}
        />
        <InputField
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          name={"password"}
          placeholder={"Password"}
          type={"password"}
        />
        <InputField
          value={retypePassword}
          onChange={(e) => setRetypePassword(e.target.value)}
          name={"retypePassword"}
          placeholder={"Retype Password"}
          type={"password"}
        />
      </div>
      <WithOthers name={"Sign up"} />
      <WithGoogle name={"Sign up"} />
      <BlueButton text={"Sign Up"} />
    </AuthWrapper>
  );
};

export default Signup;
