const WithOthers = ({ name }) => {
  return (
    <div className="max-w-[364px] w-full mt-16 flex items-center gap-2">
      <div className="bg-[#F0EDFF] flex-1 h-[2px]" />
      <div className="font-poppins">
        <span className="text-[#525252] font-bold">{name}</span>
        &nbsp;with Others
      </div>
      <div className="bg-[#F0EDFF] flex-1 h-[2px]" />
    </div>
  );
};

export default WithOthers;
