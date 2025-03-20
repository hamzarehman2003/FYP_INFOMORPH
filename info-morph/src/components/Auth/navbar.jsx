import { authNavbarOptions } from "@/utils/authNavbar";
import Link from "next/link";
import { useContext } from "react";
import { AuthContext } from "../../context/AuthContext"; // Adjust path
import { useRouter } from "next/navigation";
import { toast } from "react-toastify";
import OrangeButton from "./orangeButton";

const Navbar = ({ page, setPage }) => {
  const { auth, logout } = useContext(AuthContext) || {};
  const router = useRouter();
  
  // Check if user is actually authenticated (has a token)
  const isAuthenticated = auth && auth.token;

  const handleLogout = async () => {
    if (logout) {
      try {
        const result = await logout();
        if (result && result.success) {
          toast.info("Logged out successfully.");
          router.push("/");
        } else if (result && !result.success) {
          toast.error(result.message || "Failed to logout. Please try again.");
        } else {
          // Fallback if result is undefined or in an unexpected shape
          toast.error("An unexpected error occurred during logout.");
        }
      } catch (error) {
        console.error("Logout exception:", error);
        toast.error("An error occurred during logout.");
      }
    }
  };
  

  return (
    <div className="mt-10 px-8 hidden md:flex items-center justify-between font-poppins">
      <div className="flex items-center gap-12">
        {authNavbarOptions.map((item, index) => (
          <Link key={index} href={item.href}>
            {item.name}
          </Link>
        ))}
      </div>
      <div>
        {isAuthenticated ? (
          <button
            onClick={handleLogout}
            className="px-6 py-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition duration-300"
          >
            Logout
          </button>
        ) : (
          <>
            <OrangeButton
              name={"login"}
              page={page}
              onClick={() => setPage("login")}
            />
            <OrangeButton
              name={"signup"}
              page={page}
              onClick={() => setPage("signup")}
            />
          </>
        )}
      </div>
    </div>
  );
};

export default Navbar;