const InputField = ({ value, onChange, name, type, placeholder, autocomplete }) => {
  return (
    <input
      value={value}
      onChange={onChange}
      name={name}
      type={type}
      placeholder={placeholder}
      autoComplete={autocomplete || (type === "password" ? "new-password" : "on")}
      className={`pl-6 md:pl-12 font-poppins py-4 rounded-2xl placeholder:text-xs placeholder:text-black text-sm w-full`}
    />
  );
};

export default InputField;
