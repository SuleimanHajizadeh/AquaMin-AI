module.exports = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        aqua: {
          50: '#e6f7ff', 100: '#b3e5fc', 200: '#4fc3f7',
          300: '#03a9f4', 400: '#0288d1', 500: '#01579b',
          600: '#013a6b', 700: '#012a50', 800: '#011b35', 900: '#000d1a'
        }
      },
      fontFamily: { sans: ['Inter', 'sans-serif'] },
      animation: {
        pulse2: 'pulse 2s cubic-bezier(0.4,0,0.6,1) infinite',
        'fade-in': 'fadeIn 0.5s ease-in-out'
      },
      keyframes: {
        fadeIn: { '0%': {opacity:'0',transform:'translateY(8px)'}, '100%': {opacity:'1',transform:'translateY(0)'} }
      }
    }
  },
  plugins: []
}
