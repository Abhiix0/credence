import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        monad: {
          50: "#f5f3ff",
          500: "#8b5cf6",
          600: "#7c3aed",
          900: "#4c1d95",
        },
      },
    },
  },
  plugins: [],
};
export default config;
