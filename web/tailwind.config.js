/** @type {import('tailwindcss').Config} */
export default {
	content: ['./index.html', './src/**/*.{vue,js}'],
	theme: {
		extend: {
			height: {
				'screen/2': '50vh',
			},
		},
	},
	plugins: [],
};
