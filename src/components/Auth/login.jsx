"use client";
import { useState } from "react";
import Heading from "./heading";
import InputField from "./inputfield";
import AuthWrapper from "./wrapper";
import WithOthers from "./withOthers";
import WithGoogle from "./withGoogle";
import BlueButton from "./blueButton";
const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  return (
    <AuthWrapper>
      <Heading heading={"Continue on"} className={"mb-10"} />
      <div className="w-[364px] flex flex-col gap-7">
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
      </div>
      <WithOthers name={"Log in"} />
      <WithGoogle name={"Log in"} />
      <BlueButton text={"Login"} />
    </AuthWrapper>
  );
};

export default Login;
