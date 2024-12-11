// frontend/components/PageHeading.jsx

import React from "react";

const PageHeading = ({ text, className }) => {
  return (
    <h1 className={`text-4xl font-bold ${className}`}>
      {text}
    </h1>
  );
};

export default PageHeading;
