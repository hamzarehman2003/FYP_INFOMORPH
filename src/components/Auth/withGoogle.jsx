import GoogleSVG from "@/assets/google";

const WithGoogle = ({ name }) => {
  return (
    <button className="w-full py-3 mt-6 font-poppins flex items-center justify-center gap-2 border border-[#FCFEDC] rounded-2xl">
      <GoogleSVG />
      <div>
        {name} up with&nbsp;
        <span className="font-bold text-[#1C1C1C]">google</span>
      </div>
    </button>
  );
};

export default WithGoogle;
