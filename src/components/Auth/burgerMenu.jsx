import { authNavbarOptions } from "@/utils/authNavbar";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";

const BurgerMenu = ({ page, setPage }) => {
  const modalRef = useRef(null);
  const [isBurgerMenuOpen, setIsBurgerMenuOpen] = useState(false);

  const handleLoginButton = () => {
    setPage("login");
    setIsBurgerMenuOpen(false);
  };

  const handleSignUpButton = () => {
    setPage("signup");
    setIsBurgerMenuOpen(false);
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (modalRef.current && !modalRef.current.contains(event.target)) {
        setIsBurgerMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [setIsBurgerMenuOpen]);
  return (
    <>
      <div className="mt-10 px-8 flex md:hidden">
        <div className={`relative transition-all duration-300 ease-in-out`}>
          <button
            onClick={() => setIsBurgerMenuOpen(!isBurgerMenuOpen)}
            className={`${
              isBurgerMenuOpen && "bg-[#1A3453]"
            } flex flex-col w-9 h-8 items-center justify-center gap-[6px] rounded-[4px] active:scale-90`}
          >
            {[...Array(3)].map((item, index) => (
              <div
                key={index}
                className={`h-[2px] ${
                  isBurgerMenuOpen ? "bg-white" : "bg-[#1A3453]"
                } w-[20px]`}
              />
            ))}
          </button>
          <div
            ref={modalRef}
            className={`${
              isBurgerMenuOpen ? "opacity-100 scale-100" : "opacity-0 scale-75"
            } absolute top-full left-full w-[250px] bg-[#1A3453] duration-300 transition-all ease-in-out z-[3] rounded-lg flex flex-col`}
          >
            {authNavbarOptions.map((item, index) => (
              <Link
                href={item.href}
                key={index}
                className="pl-4 py-3 font-medium font-poppins text-white"
              >
                {item.name}
              </Link>
            ))}
            <div
              onClick={handleLoginButton}
              className={`pl-4 py-3 font-medium font-poppins text-white cursor-pointer`}
            >
              Login
            </div>
            <div
              onClick={handleSignUpButton}
              className={`pl-4 py-3 font-medium font-poppins text-white cursor-pointer`}
            >
              Signup
            </div>
          </div>
        </div>
      </div>
      <div
        className={`${
          isBurgerMenuOpen
            ? "pointer-events-auto bg-[rgba(0,0,0,0.5)]"
            : "pointer-events-none bg-transparent"
        } fixed z-[2] inset-0 transition-all duration-300 ease-in-out`}
      />
    </>
  );
};

export default BurgerMenu;
