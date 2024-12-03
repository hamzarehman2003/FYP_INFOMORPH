const PageHeading = ({ text, className }) => {
  return (
    <h1
      className={`text-4xl text-[#1A3453] font-bold text-center px-5 ${className}`}
    >
      {text}
    </h1>
  );
};

export default PageHeading;
