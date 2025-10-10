// tailwind.config.js
module.exports = {
  darkMode: "class", // use class-based toggling
  theme: {
    extend: {
      keyframes: {
        fadeInDown: {
          "0%": { opacity: "0", transform: "translateY(-20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        // you could add bounce, spin, etc.
      },
      animation: {
        fadeInDown: "fadeInDown 0.8s ease-out",
        // e.g. spinSlow: "spin 3s linear infinite",
      },
    },
  },
  variants: {
    extend: {
      // any extra variants you want
    },
  },
  plugins: [],
};
