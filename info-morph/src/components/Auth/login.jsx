"use client";
import { useRouter } from "next/navigation";
import Heading from "./heading";
import InputField from "./inputfield";
import AuthWrapper from "./wrapper";
import WithOthers from "./withOthers";
import WithGoogle from "./withGoogle";
import BlueButton from "./blueButton";

const Login = () => {
  const router = useRouter();

  const handleLogin = (e) => {
    e.preventDefault();
    router.push("/url-link");
  };

  return (
    <AuthWrapper>
      <Heading heading="Continue on" className="mb-10" />
      <form onSubmit={handleLogin}>
        <div className="w-[364px] flex flex-col gap-7">
          <InputField
            name="email"
            placeholder="Email"
            type="text"
          />
          <InputField
            name="password"
            placeholder="Password"
            type="password"
          />
        </div>
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