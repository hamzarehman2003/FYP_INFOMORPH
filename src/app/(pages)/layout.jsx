import Header from "@/components/Header";

const PagesLayout = ({ children }) => {
  return (
    <>
      <Header />
      <div className="bg-[#dcebfe] min-h-screen flex justify-center">
        {children}
      </div>
    </>
  );
};

export default PagesLayout;
