/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      // Keep your existing definitions:
      fontFamily: {
        poppins: "var(--font-poppins)",

        // 1) ADD the new 'nastaleeq' entry:
        nastaleeq: ['JameelNoori', 'serif'],
      },
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
      },
      screens: {
        xs: "550px",
        mobile: "320px",
        mobileM: "375px",
        mobileL: "425px",
        tablet: "768px",
        laptop: "1124px",
        urlLink: "1291px",
        laptopL: "1440px",
        "4k": "1920px",
        sm: "640px",
        md: "768px",
        lg: "1024px",
        xl: "1280px",
        "2xl": "1563px",
        "3xl": "1890px",
      },
    },
  },
  plugins: [],
};
