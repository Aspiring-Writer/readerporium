module.exports = {
  content: [
    './templates/*.{html,js}',
    './static/*.{html,js}'
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
