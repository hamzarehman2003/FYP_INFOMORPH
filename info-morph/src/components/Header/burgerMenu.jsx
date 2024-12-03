import { headerLinks } from "@/utils/headerLinks";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";

const BurgerMenu = ({ pathName }) => {
  const modalRef = useRef(null);
  const [isBurgerMenuOpen, setIsBurgerMenuOpen] = useState(false);

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
      <div className="pt-10 px-8 flex laptop:hidden bg-[#dcebfe]">
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
            } absolute top-full left-full w-[250px] bg-[#1A3453] overflow-hidden duration-300 transition-all ease-in-out z-[3] rounded-lg flex flex-col`}
          >
            {headerLinks.map((item, index) => (
              <Link
                href={item.href}
                key={index}
                className={`${
                  pathName === item.href && "bg-[#FF553E]"
                } pl-4 py-3 font-medium font-poppins text-white`}
              >
                {item.name}
              </Link>
            ))}
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
