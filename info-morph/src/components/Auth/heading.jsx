const Heading = ({ heading, className }) => {
  return (
    <h1 className={`text-5xl text-[#1A3453] font-bold ${className}`}>
      {heading}
    </h1>
  );
};

export default Heading;
