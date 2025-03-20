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
  const { auth, logout } = useContext(AuthContext) || {};
  const router = useRouter();

  const handleLogout = async () => {
    if (logout) {
      try {
        const result = await logout();
        // Treat a 404 or no session as a successful logout.
        if (result.success || result.message?.includes("No active session")) {
          toast.info("Logged out successfully.");
          router.push("/");
        } else {
          toast.error(result.message || "Failed to logout. Please try again.");
        }
      } catch (error) {
        console.error("Logout exception:", error);
        toast.error("An error occurred during logout.");
      }
    }
  };

  // Check if user is actually authenticated (has a token)
  const isAuthenticated = auth && auth.token;

  return (
    <>
      <BurgerMenu pathName={pathName} />
      <header className="hidden laptop:flex items-center py-8 bg-[#FCFEDC] w-full px-14">
        <div className="flex items-center w-full">
          {/* Left Side - Logo */}
          <div className="flex-1 flex items-center gap-[5px]">
            <Link href="/" className="flex items-center">
              <LogoSVG />
              <div className="text-5xl font-bold text-[#1A3453]">Info Morph</div>
            </Link>
          </div>

          {/* Center - Navigation Links */}
          <div className="flex-1 flex items-center justify-center space-x-8">
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

          {/* Right Side - Auth Buttons */}
          <div className="flex-1 flex justify-end">
            {isAuthenticated ? (
              <button
                onClick={handleLogout}
                className="px-6 py-3 bg-red-500 text-white rounded-full hover:bg-red-600 transition duration-300"
              >
                Logout
              </button>
            ) : (
              <>
                <Link
                  href="/"
                  className="mr-4 px-6 py-3 bg-blue-500 text-white rounded-full hover:bg-blue-600 transition duration-300"
                >
                  Login
                </Link>
                <Link
                  href="/"
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