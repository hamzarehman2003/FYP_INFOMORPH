"use client";
import LogoSVG from "@/assets/logo";
import { headerLinks } from "@/utils/headerLinks";
import Link from "next/link";
import { usePathname } from "next/navigation";
import BurgerMenu from "./burgerMenu";

const Header = () => {
  const pathName = usePathname();
  return (
    <>
      <BurgerMenu pathName={pathName} />
      <header className="hidden laptop:flex items-center py-8 pl-14 bg-[#FCFEDC]">
        <div className="flex 3xl:flex-1 items-center gap-[5px]">
          <LogoSVG />
          <div className="text-5xl font-bold text-[#1A3453]">Info Morph</div>
        </div>
        <div className="flex flex-1 items-center justify-center">
          {headerLinks.map((item, index) => (
            <Link
              key={index}
              href={item.href}
              className={`${
                item.href === pathName && "text-white bg-[#FF553E]"
              } py-4 px-8 rounded-full`}
            >
              {item.name}
            </Link>
          ))}
        </div>
        <div className="hidden 3xl:block 3xl:flex-1" />
      </header>
    </>
  );
};

export default Header;
