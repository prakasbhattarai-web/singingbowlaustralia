/** Tailwind v3 config. Build with: python3 scripts/build.py */
module.exports = {
  content: ['./index.html', './*/index.html', './src/**/*.html', './scripts/build.py', './assets/site.js'],
  theme: { extend: {} },
  plugins: [],
};
