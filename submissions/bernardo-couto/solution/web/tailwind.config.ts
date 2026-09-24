import type { Config } from 'tailwindcss';

// G4 tokens verified from g4business.com (see .claude/skills/g4-design-system/SKILL.md).
// Semantic additions (muted, tints, row states) documented in docs/design/design-tokens.md
// with WCAG ratios; do not add a color here without adding its contrast row there.
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        g4: {
          primary: '#001F35',
          secondary: '#B9915B',
          text: '#031A26',
          muted: '#5B6673', // 5.84:1 on white — replaces signal.neutral for text
          disabled: '#8A939E', // disabled controls only (WCAG-exempt)
          surface: '#F5F4F3',
          navy700: '#184560',
          risk: '#842E20',
          riskDeep: '#441B1B',
          highlight: '#FFCB00',
          tintNavy: '#E6EBF0', // active filter chip bg
          tintGold: '#F4ECE0', // optional tier A tint
          rowHover: '#F9F8F7',
          rowSelected: '#EEF2F6',
        },
        tier: {
          A: '#B9915B', // text must be g4.primary (5.82:1)
          B: '#184560', // text white (10.20:1)
          C: '#6B7A8C', // icon/border only; badge uses Cbg/Ctext
          D: '#9AA3AE', // icon/border only; badge uses Dbg/Dtext
          Cbg: '#E8EBEF',
          Ctext: '#3F4C5C', // 7.32:1 on Cbg
          Dbg: '#F0F2F4',
          Dtext: '#55606C', // 5.71:1 on Dbg
        },
        signal: {
          pos: '#1F6F5F', // 6.00:1 on white
          neg: '#842E20', // 8.78:1 on white
          neutral: '#6B7A8C', // icons only (4.39:1 fails for small text)
          posBg: '#E3F1EC',
          negBg: '#F6E7E4',
          infoBg: '#E8EBEF',
        },
      },
      fontFamily: {
        sans: ['Manrope', 'system-ui', 'sans-serif'],
        serif: ['"Libre Baskerville"', 'Georgia', 'serif'],
      },
      fontSize: {
        xs: ['12px', '1.5'],
        sm: ['14px', '1.5'],
        base: ['16px', '1.5'],
        xl: ['20px', '1.3'],
        '2xl': ['24px', '1.25'],
        '3xl': ['32px', '1.1'],
      },
      borderRadius: { DEFAULT: '10px', lg: '20px' },
      borderColor: { g4line: '#001F3526' },
      outlineColor: { focus: '#184560' },
      width: { sidebar: '264px', drawer: '480px' },
      maxWidth: { content: '1120px' },
      boxShadow: { card: '0 1px 2px rgba(0,31,53,0.06), 0 1px 3px rgba(0,31,53,0.10)' },
    },
  },
  plugins: [],
} satisfies Config;
