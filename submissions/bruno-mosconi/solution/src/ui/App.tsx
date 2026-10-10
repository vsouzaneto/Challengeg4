// Entrada por pessoa (D38) e três áreas: Minha semana, Minha equipe, Como funciona (D41).
// A data de referência fica sempre visível, num controle segmentado (no celular, um seletor nativo).

import {
	type ReactNode,
	useEffect,
	useLayoutEffect,
	useMemo,
	useRef,
	useState,
} from "react";
import { availableDates } from "../core/analysis.ts";
import { REFERENCE_DATE } from "../core/rules.ts";
import { dataset as ds } from "./dataset.ts";
import { date, initials } from "./format.ts";
import { HowView } from "./HowView.tsx";
import { Icon, type IconName } from "./Icon.tsx";
import { dayModel, MANAGERS, maxPotential, PEOPLE } from "./model.ts";
import { snapshot, takeFirstOpen } from "./motion.ts";
import { EntryView, type Person } from "./Pages.tsx";
import { SellerView } from "./SellerView.tsx";
import { TeamView } from "./TeamView.tsx";

type Area = "entrada" | "semana" | "equipe" | "como-funciona";
const AREAS: Area[] = ["entrada", "semana", "equipe", "como-funciona"];
const DATES = availableDates(ds);
const STORE = "onde-focar:pessoa";
const NAV: Record<
	Exclude<Area, "entrada">,
	{ label: string; icon: IconName }
> = {
	semana: { label: "Minha semana", icon: "calendar-check" },
	equipe: { label: "Minha equipe", icon: "users-three" },
	"como-funciona": { label: "Como funciona", icon: "info" },
};

/** A escolha salva neste aparelho. Só vale se a pessoa existe nos dados. */
function loadPerson(): Person | null {
	try {
		const p = JSON.parse(
			localStorage.getItem(STORE) ?? "null",
		) as Person | null;
		if (p?.role === "gestor" && MANAGERS.some((m) => m.name === p.name))
			return p;
		if (p?.role === "vendedor" && PEOPLE.some((a) => a.name === p.name))
			return p;
	} catch {}
	return null;
}

const home = (p: Person | null): Area =>
	!p ? "entrada" : p.role === "gestor" ? "equipe" : "semana";

const areaFor = (p: Person | null): Area => {
	const h = location.hash.slice(1) as Area;
	if (h === "como-funciona") return h;
	if (!p || !AREAS.includes(h) || (h === "semana" && p.role === "gestor"))
		return home(p);
	return h;
};

// Escala de tamanho fixa dos pontos: o maior potencial em qualquer data disponível.
const PMAX = maxPotential(DATES.filter((d) => d.available).map((d) => d.t));

function Dates({ t, onPick }: { t: number; onPick: (t: number) => void }) {
	const ref = useRef<HTMLDivElement>(null);
	const thumb = useRef<HTMLSpanElement>(null);
	const moved = useRef(false);
	// O fundo do segmento escolhido desliza até a data nova; sem animar na carga, na troca de
	// fonte ou ao redimensionar.
	// biome-ignore lint/correctness/useExhaustiveDependencies: precisa rodar a cada troca de data
	useLayoutEffect(() => {
		const place = (animate: boolean) => {
			const on = ref.current?.querySelector<HTMLElement>(
				'[aria-pressed="true"]',
			);
			const th = thumb.current;
			if (!on || !th) return;
			if (!animate) th.style.transition = "none";
			th.style.width = `${on.offsetWidth}px`;
			th.style.transform = `translateX(${on.offsetLeft}px)`;
			if (!animate) {
				void th.offsetWidth;
				th.style.transition = "";
			}
		};
		place(moved.current);
		moved.current = true;
		const still = () => place(false);
		document.fonts?.ready.then(still);
		addEventListener("resize", still);
		return () => removeEventListener("resize", still);
	}, [t]);
	return (
		<>
			<span className="dates-label" aria-hidden="true">
				Dados de
			</span>
			{/* biome-ignore lint/a11y/useSemanticElements: grupo de botões de alternância; um fieldset mudaria o layout do controle */}
			<div
				ref={ref}
				className="seg dates"
				role="group"
				aria-label="Data dos dados"
			>
				<span ref={thumb} className="seg-thumb" />
				{DATES.map((d) => (
					<button
						key={d.t}
						type="button"
						aria-pressed={d.t === t}
						disabled={!d.available}
						title={
							d.available
								? undefined
								: "Data bloqueada: até esse dia, poucos negócios tinham terminado, e a chance de fechar ainda não era confiável"
						}
						onClick={() => onPick(d.t)}
					>
						{d.t === REFERENCE_DATE ? date(d.t) : date(d.t).slice(0, 5)}
					</button>
				))}
			</div>
			<select
				className="date-select"
				aria-label="Data dos dados"
				value={t}
				onChange={(e) => onPick(Number(e.target.value))}
			>
				{DATES.filter((d) => d.available).map((d) => (
					<option key={d.t} value={d.t}>
						{date(d.t)}
					</option>
				))}
			</select>
		</>
	);
}

export function App() {
	const [person, setPerson] = useState<Person | null>(loadPerson);
	const [area, setArea] = useState<Area>(() => areaFor(loadPerson()));
	const [t, setT] = useState(REFERENCE_DATE);
	const [seller, setSeller] = useState<string | null>(null); // gestor abriu a semana de alguém
	const [otherTeam, setOtherTeam] = useState<string | null>(null); // seletor de equipe (D57)
	const [intro, setIntro] = useState(false);
	const day = useMemo(() => dayModel(t), [t]);

	useEffect(() => {
		const on = () => {
			setArea(areaFor(person));
			setSeller(null);
			scrollTo(0, 0);
		};
		addEventListener("hashchange", on);
		return () => removeEventListener("hashchange", on);
	}, [person]);

	// Quem chega sem pessoa escolhida vê "Quem é você?": o endereço acompanha (#entrada).
	useEffect(() => {
		const entry = area === "entrada" || (!person && area !== "como-funciona");
		if (entry && location.hash !== "#entrada")
			history.replaceState(null, "", "#entrada");
	}, [area, person]);

	const manager =
		person?.role === "gestor"
			? person.name
			: (PEOPLE.find((a) => a.name === person?.name)?.manager ?? "");
	const ownWeek = person?.role === "vendedor" ? person.name : null;
	const showWeek = area === "semana" && (seller ?? ownWeek);
	const items: Exclude<Area, "entrada">[] =
		person?.role === "gestor"
			? ["equipe", "como-funciona"]
			: ["semana", "equipe", "como-funciona"];

	// Primeira abertura da semana, uma vez por sessão.
	useEffect(() => {
		if (area !== "semana" || seller || !ownWeek) return;
		if (!takeFirstOpen()) return;
		setIntro(true);
		const id = setTimeout(() => setIntro(false), 900);
		return () => clearTimeout(id);
	}, [area, seller, ownWeek]);

	const pickDate = (next: number) => {
		if (next === t) return;
		snapshot();
		setT(next);
	};

	const pick = (p: Person) => {
		try {
			localStorage.setItem(STORE, JSON.stringify(p));
		} catch {}
		setPerson(p);
		setOtherTeam(null);
		setSeller(null);
		setArea(home(p));
		history.replaceState(null, "", `#${home(p)}`);
		scrollTo(0, 0);
	};

	const openSeller = (name: string) => {
		setSeller(name);
		setArea("semana");
		scrollTo(0, 0);
	};

	let page: ReactNode;
	if (area === "entrada" || (!person && area !== "como-funciona"))
		page = <EntryView day={day} onPick={pick} />;
	else if (area === "como-funciona") page = <HowView day={day} />;
	else if (showWeek)
		page = (
			<SellerView
				key={showWeek}
				day={day}
				name={showWeek}
				fromTeam={!!seller}
				intro={intro && !seller}
				pmax={PMAX}
				onBack={() => {
					setSeller(null);
					setArea("equipe");
				}}
			/>
		);
	else
		page = (
			<TeamView
				day={day}
				manager={otherTeam ?? manager}
				viewerIsManager={
					person?.role === "gestor" && (otherTeam ?? manager) === person.name
				}
				onPickTeam={(m) => setOtherTeam(m === manager ? null : m)}
				ownTeam={manager}
				pmax={PMAX}
				onOpen={openSeller}
			/>
		);

	const current = seller ? "equipe" : area;
	const onEntry = area === "entrada" || !person;
	return (
		<>
			<header className="nav">
				<div className="nav-in">
					<span className="brand">Onde focar</span>
					{!onEntry && (
						<nav className="areas" aria-label="Áreas">
							{items.map((a) => (
								<a
									key={a}
									href={`#${a}`}
									aria-current={current === a ? "page" : undefined}
								>
									{NAV[a].label}
								</a>
							))}
						</nav>
					)}
					<span className="spacer" />
					{!onEntry && <Dates t={t} onPick={pickDate} />}
					{person && !onEntry && (
						<a className="who" href="#entrada" aria-label="Trocar de pessoa">
							<span className="avatar">{initials(person.name)}</span>
							<span className="who-name">{person.name}</span>
						</a>
					)}
				</div>
			</header>
			<main>{page}</main>
			{!onEntry && (
				<nav className="tabbar" aria-label="Áreas">
					{items.map((a) => (
						<a
							key={a}
							href={`#${a}`}
							aria-current={current === a ? "page" : undefined}
						>
							<Icon name={NAV[a].icon} />
							<span>{NAV[a].label}</span>
						</a>
					))}
				</nav>
			)}
		</>
	);
}
