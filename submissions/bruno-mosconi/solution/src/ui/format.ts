import { isoDate } from "../core/data.ts";

const int = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 });
const two = new Intl.NumberFormat("pt-BR", {
	minimumFractionDigits: 2,
	maximumFractionDigits: 2,
});
const one = new Intl.NumberFormat("pt-BR", {
	minimumFractionDigits: 1,
	maximumFractionDigits: 1,
});

export const num = (n: number) => int.format(n);
export const usd = (n: number) => `US$ ${int.format(n)}`;

/** Para a barra de números: "US$ 3,89 mi", "US$ 466 mil". Abaixo de 10 mil, o valor inteiro. */
export const usdShort = (n: number) =>
	n >= 1e6
		? `US$ ${two.format(n / 1e6)} mi`
		: n >= 1e4
			? `US$ ${int.format(n / 1e3)} mil`
			: usd(n);

export const pct = (x: number) => `${one.format(x * 100)}%`;

export const date = (day: number) =>
	isoDate(day).split("-").reverse().join("/");

export const plural = (n: number, one: string, many: string) =>
	`${int.format(n)} ${n === 1 ? one : many}`;

export const days = (n: number) => plural(n, "dia", "dias");

export const first = (name: string) => name.split(" ")[0] ?? name;
export const initials = (name: string) =>
	name
		.split(" ")
		.map((x) => x[0])
		.join("");
