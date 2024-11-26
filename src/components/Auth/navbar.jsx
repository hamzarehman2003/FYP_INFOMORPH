import { authNavbarOptions } from "@/utils/authNavbar";
import Link from "next/link";

const Navbar = ({ page, setPage }) => {
  return (
    <>
      <div className="mt-10 px-8 hidden md:flex items-center justify-between font-poppins">
        <div className="flex items-center gap-12">
          {authNavbarOptions.map((item, index) => (
            <Link key={index} href={item.href}>
              {item.name}
            </Link>
          ))}
        </div>
        <div>
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
        </div>
      </div>
    </>
  );
};

export default Navbar;

const OrangeButton = ({ name, page, onClick }) => {
  return (
    <button
      onClick={onClick}
      className={`${
        page === name ? "bg-[#FF553E] text-white" : "text-[#FF553E]"
      } px-8 py-4 rounded-full font-medium`}
    >
      {name === "login" && "Login"}
      {name === "signup" && "Sign Up"}
    </button>
  );
};
