import LogoSVG from "@/assets/logo";

const Layout = () => {
  return (
    <div className="md:pl-9 lg:pl-12 xl:pl-[62px] bg-[#FEDEDC] hidden basis-[40%] xl:flex flex-col">
      <div className="flex items-center gap-[5px] mt-10">
        <LogoSVG />
        <div className="text-5xl font-bold text-[#1A3453]">Info Morph</div>
      </div>
      <div className="mt-48 text-5xl font-bold">
        <div className="max-w-[455px]">
          Revolutionizing Information with AI generation
        </div>
      </div>
    </div>
  );
};

export default Layout;
