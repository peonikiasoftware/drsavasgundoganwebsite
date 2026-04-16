/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/templates/**/*.html',
    './static/src/js/**/*.js',
    './apps/**/*.py',
  ],
  theme: {
    extend: {
      colors: {
        teal: {
          50:  '#E6F7F8',
          100: '#B3E7EB',
          200: '#80D7DD',
          300: '#4DC7CF',
          400: '#26B7C1',
          500: '#00A0B0',
          600: '#008A99',
          700: '#007B8A',
          800: '#005F6B',
          900: '#00434D',
        },
        cream: {
          50:  '#FDFCF9',
          100: '#F8F5EF',
          200: '#F0EBE0',
          300: '#E4DDCE',
        },
        ink: {
          900: '#0F1720',
          700: '#3A4551',
          500: '#6B7582',
          300: '#B8BFC7',
          100: '#E8ECF0',
        },
        gold: {
          400: '#D6BC7C',
          500: '#C9A961',
          600: '#A88A48',
          700: '#856C36',
        },
      },
      fontFamily: {
        serif: ['"Fraunces"', '"Playfair Display"', 'Georgia', 'serif'],
        sans: ['"Inter"', 'system-ui', '-apple-system', 'sans-serif'],
      },
      fontSize: {
        'hero':    ['clamp(2.5rem, 5vw, 4.5rem)',    { lineHeight: '1.05', letterSpacing: '-0.02em' }],
        'display': ['clamp(2rem, 4vw, 3.25rem)',     { lineHeight: '1.1',  letterSpacing: '-0.015em' }],
        'h2':      ['clamp(1.75rem, 3vw, 2.25rem)',  { lineHeight: '1.2',  letterSpacing: '-0.01em' }],
      },
      maxWidth: {
        'main': '1200px',
        'prose-reading': '760px',
      },
      animation: {
        'fade-up': 'fadeUp 0.6s ease-out both',
        'reveal':  'reveal 1.2s cubic-bezier(0.77, 0, 0.175, 1) both',
        'float':   'floatY 4s ease-in-out infinite',
      },
      keyframes: {
        fadeUp:  {
          '0%':   { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        reveal:  {
          '0%':   { clipPath: 'inset(0 100% 0 0)' },
          '100%': { clipPath: 'inset(0 0 0 0)' },
        },
        floatY: {
          '0%,100%': { transform: 'translateY(0)' },
          '50%':     { transform: 'translateY(-6px)' },
        },
      },
      boxShadow: {
        'teal-glow': '0 20px 60px -20px rgba(0, 160, 176, 0.35)',
        'gold-glow': '0 20px 60px -20px rgba(201, 169, 97, 0.35)',
        'soft-lift': '0 10px 32px -12px rgba(15, 23, 32, 0.12)',
      },
      backgroundImage: {
        'teal-gradient': 'linear-gradient(135deg, #00A0B0 0%, #007B8A 100%)',
        'cream-noise':   'radial-gradient(circle at 0% 0%, #F8F5EF 0%, #FDFCF9 100%)',
      },
      transitionDuration: {
        '250': '250ms',
        '400': '400ms',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
};
