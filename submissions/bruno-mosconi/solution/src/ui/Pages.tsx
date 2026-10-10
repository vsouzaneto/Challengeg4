// Entrada ("Quem é você?") e a imagem com versão clara e escura.

import entradaClaro from "./assets/entrada-claro.webp";
import entradaEscuro from "./assets/entrada-escuro.webp";
import { initials, plural, usdShort } from "./format.ts";
import { Icon } from "./Icon.tsx";
import {
	type DayModel,
	MANAGERS,
	nothingOpen,
	PEOPLE,
	sellerModel,
	teamModel,
	weekSummary,
} from "./model.ts";

export interface Person {
	role: "vendedor" | "gestor";
	name: string;
}

export function Art({
	light,
	dark,
	alt,
	className = "",
}: {
	light: string;
	dark: string;
	alt: string;
	className?: string;
}) {
	return (
		<picture>
			<source srcSet={dark} media="(prefers-color-scheme: dark)" />
			<img className={`art ${className}`} src={light} alt={alt} />
		</picture>
	);
}

/** Três perfis sugeridos, um por situação: semana cheia, semana de prospecção e gestão. */
const SUGGESTED = [
	{ role: "vendedor", name: "Zane Levy", why: "Semana cheia" },
	{
		role: "vendedor",
		name: "Anna Snelling",
		why: "Semana que começa pela prospecção",
	},
	{ role: "gestor", name: "Summer Sewald", why: "Visão da equipe" },
] as const;

export function EntryView({
	day,
	onPick,
}: {
	day: DayModel;
	onPick: (p: Person) => void;
}) {
	const regionals = [...new Set(PEOPLE.map((a) => a.regional))].sort();
	const managerLine = (name: string) => {
		const st = teamModel(day, name);
		const cold = st.reduce((s, a) => s + a.slices.parado.listPrice, 0);
		return `${usdShort(cold)} frios na equipe`;
	};
	const sellers = PEOPLE.map((a) => ({
		...a,
		empty: nothingOpen(sellerModel(day, a.name)),
		summary: weekSummary(day, a.name),
	}));
	const row = (p: Person, summary: string, sub: string, key = "") => (
		<button
			key={`${key}${p.role}-${p.name}`}
			type="button"
			className="person"
			onClick={() => onPick(p)}
		>
			<span className="avatar lg">{initials(p.name)}</span>
			<span className="nm">
				{p.name}
				<span>{summary}</span>
				<span className="sub2">{sub}</span>
			</span>
			<span className="chev">
				<Icon name="caret-right" />
			</span>
		</button>
	);
	const byName = (a: { name: string }, b: { name: string }) =>
		a.name.localeCompare(b.name, "pt-BR");
	const idle = sellers.filter((a) => a.empty).sort(byName);
	return (
		<section className="entry">
			<Art
				light={entradaClaro}
				dark={entradaEscuro}
				className="entry-art"
				alt="Uma barra de vidro fosco iluminada por dentro, laranja numa ponta e cinza fria na outra."
			/>
			<h1>Quem é você?</h1>
			<p className="lead-sub">
				Escolha seu nome. O app abre na sua semana, com os negócios em que vale
				focar primeiro, e lembra a escolha neste aparelho.
			</p>
			<div className="people">
				<div>
					<h2>Para conhecer o app</h2>
					<p className="people-note">
						Sugestões: três perfis que mostram situações diferentes.
					</p>
					<div className="card">
						{SUGGESTED.filter((x) =>
							(x.role === "gestor" ? MANAGERS : PEOPLE).some(
								(p) => p.name === x.name,
							),
						).map((x) =>
							row(
								{ role: x.role, name: x.name },
								x.why,
								x.role === "gestor"
									? managerLine(x.name)
									: weekSummary(day, x.name),
								"sug-",
							),
						)}
					</div>
				</div>
				<div>
					<h2>Gestor(a)</h2>
					<div className="card">
						{MANAGERS.map((m) =>
							row(
								{ role: "gestor", name: m.name },
								managerLine(m.name),
								`${m.regional}, equipe de ${plural(m.team, "pessoa", "pessoas")}`,
							),
						)}
					</div>
				</div>
				{regionals.map((r) => (
					<div key={r}>
						<h2>Vendedor(a), regional {r}</h2>
						<div className="card">
							{sellers
								.filter((a) => a.regional === r && !a.empty)
								.sort(byName)
								.map((a) =>
									row(
										{ role: "vendedor", name: a.name },
										a.summary,
										`Equipe de ${a.manager}`,
									),
								)}
						</div>
					</div>
				))}
				{idle.length > 0 && (
					<div>
						<h2>Sem negócios em andamento</h2>
						<div className="card">
							{idle.map((a) =>
								row(
									{ role: "vendedor", name: a.name },
									a.summary,
									`Regional ${a.regional}, equipe de ${a.manager}`,
								),
							)}
						</div>
					</div>
				)}
			</div>
		</section>
	);
}
