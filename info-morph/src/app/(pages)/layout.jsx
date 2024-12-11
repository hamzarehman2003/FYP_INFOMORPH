// frontend/app/urllink/layout.jsx

"use client";

const PagesLayout = ({ children }) => {
  return (
    <div className="bg-[#dcebfe] min-h-screen flex justify-center">
      {children}
    </div>
  );
};

export default PagesLayout;
