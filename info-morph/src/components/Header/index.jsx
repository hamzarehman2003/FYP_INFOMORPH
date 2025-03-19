// frontend/src/components/Header/index.jsx

"use client";

import LogoSVG from "@/assets/logo";
import { headerLinks } from "@/utils/headerLinks";
import Link from "next/link";
import { usePathname } from "next/navigation";
import BurgerMenu from "./burgerMenu";
import { useContext } from "react";
import { AuthContext } from "../../context/AuthContext";
import { useRouter } from "next/navigation";
import { toast } from "react-toastify";

const Header = () => {
  const pathName = usePathname();
  const { auth, logout } = useContext(AuthContext);
  const router = useRouter();

  const handleLogout = () => {
    logout();
    toast.info("Logged out successfully.");
    router.push("/");
  };

  return (
    <>
      <BurgerMenu pathName={pathName} />
      <header className="hidden laptop:flex items-center py-8 bg-[#FCFEDC] w-screen max-w-full"> {/* Updated */}
        <div className="container mx-auto flex items-center justify-between w-full px-4"> {/* New container */}
          <div className="flex items-center gap-[5px]">
            <Link href="/" className="flex items-center">
              <LogoSVG />
              <div className="text-5xl font-bold text-[#1A3453]">Info Morph</div>
            </Link>
          </div>
          <div className="flex items-center space-x-8">
            {headerLinks.map((item, index) => (
              <Link
                key={index}
                href={item.href}
                className={`${
                  item.href === pathName
                    ? "text-white bg-[#FF553E]"
                    : "text-gray-700 hover:text-gray-900"
                } py-4 px-8 rounded-full transition duration-300`}
              >
                {item.name}
              </Link>
            ))}
          </div>
          <div className="flex">
            {auth.token ? (
              <button
                onClick={handleLogout}
                className="px-6 py-3 bg-red-500 text-white rounded-full hover:bg-red-600 transition duration-300"
              >
                Logout
              </button>
            ) : (
              <>
                <Link
                  href="/login"
                  className="mr-4 px-6 py-3 bg-blue-500 text-white rounded-full hover:bg-blue-600 transition duration-300"
                >
                  Login
                </Link>
                <Link
                  href="/signup"
                  className="px-6 py-3 bg-green-500 text-white rounded-full hover:bg-green-600 transition duration-300"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </header>
    </>
  );
};

export default Header;