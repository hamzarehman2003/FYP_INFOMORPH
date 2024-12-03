import PageHeading from "@/components/pageHeading";
import styles from "../style.module.css";
const UrlLinkPage = () => {
  return (
    <div className="w-full flex flex-col items-center">
      <div className="max-w-[1440px] w-full px-5 pb-24">
        <PageHeading
          text={"Make a video from a url in minutes"}
          className={"mt-24"}
        />

        <div className="mt-24 flex flex-col urlLink:flex-row flex-wrap items-center gap-10">
          <div className="flex flex-wrap items-center justify-center urlLink:justify-end w-full urlLink:w-auto urlLink:flex-1">
            <label className="w-[120px] font-poppins" htmlFor="">
              Enter the Url
            </label>
            <input
              type="text"
              className="max-w-[772px] w-full rounded-2xl h-[52px] pl-6"
            />
          </div>
          <div className="urlLink:w-[300px]">
            <select
              className={`${styles.selectClass} py-2 px-4 rounded-lg text-[#5533FF] font-medium border border-[rgba(0,0,0,0.1)]`}
              name=""
              id=""
            >
              <option value="" selected>
                Output language
              </option>
              <option value="">English</option>
              <option value="">Urdu</option>
            </select>
          </div>
        </div>

        <div className="w-full flex items-center justify-center mt-7">
          <button className="active:scale-90 duration-300 ease-in-out transition-all text-lg font-poppins font-medium bg-[#DEDCFE] py-4 px-8 rounded-full">
            Begin Summarization
          </button>
        </div>

        <div className="mt-24 w-full flex flex-col urlLink:flex-row flex-wrap items-center gap-10">
          <div className="flex flex-wrap justify-center urlLink:justify-end w-full urlLink:w-auto urlLink:flex-1">
            <label className="w-[120px] font-poppins" htmlFor="">
              Summary
            </label>
            <textarea
              type="text"
              className="max-w-[772px] w-full rounded-2xl h-[242px] pl-4 py-2.5"
            />
          </div>
          <div className="urlLink:w-[300px] urlLink:h-[242px] flex-wrap flex urlLink:flex-col items-end justify-end gap-[12px]">
            <button className="active:scale-90 duration-300 ease-in-out transition-all font-poppins text-lg py-4 px-8 rounded-full bg-[#DCFCFE]">
              Download Video
            </button>
            <button className="active:scale-90 duration-300 ease-in-out transition-all font-poppins text-lg py-4 px-8 rounded-full bg-[#DCFCFE]">
              Report Feedback
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UrlLinkPage;
