"use client";
import BurgerMenu from "@/components/Auth/burgerMenu";
import Login from "@/components/Auth/login";
import Navbar from "@/components/Auth/navbar";
import Signup from "@/components/Auth/signup";
import { useState } from "react";

const AuthPage = () => {
  const [page, setPage] = useState("login");
  return (
    <div className="flex-1 bg-[#dcebfe] flex flex-col">
      <Navbar page={page} setPage={setPage} />
      <BurgerMenu page={page} setPage={setPage} />
      {page === "login" ? <Login /> : <Signup />}
    </div>
  );
};

export default AuthPage;
