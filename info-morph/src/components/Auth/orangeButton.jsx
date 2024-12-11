import React from 'react';

const OrangeButton = ({ name, page, onClick }) => {
  return (
    <button
      onClick={onClick}
      className={`${
        page === name 
          ? 'bg-[#FF553E] text-white' 
          : name === 'signup' 
          ? 'text-[#FF553E]' 
          : 'text-[#FF553E] border border-[#FF553E]'
      } px-6 py-2 rounded-full font-medium hover:bg-[#FF553E] hover:text-white transition duration-300`}
    >
      {name === 'login' ? 'Login' : name === 'signup' ? 'Sign Up' : name}
    </button>
  );
};

export default OrangeButton;
