// Minha semana (D41): o negócio nº 1 é o herói; os nº 2 a 5 vêm menores; o resto fica recolhido.
// Se o nº 1 tem score baixo, o herói é a ação da semana e o nº 1 vira cartão (D46).
// O termômetro da carteira fica ao lado (fixo ao rolar) e o painel mostra a conta e o que fazer.

import {
	type KeyboardEvent,
	type ReactNode,
	useCallback,
	useEffect,
	useLayoutEffect,
	useMemo,
	useState,
} from "react";
import { REFERENCE_DATE, STALE_AFTER } from "../core/rules.ts";
import { DealPanel } from "./DealPanel.tsx";
import { date, days, first, num, plural, usd, usdShort } from "./format.ts";
import { Icon, type IconName } from "./Icon.tsx";
import {
	actionInfo,
	type DayModel,
	type DealView,
	greeting,
	type HeroAction,
	heroAction,
	type SellerModel,
	sellerModel,
	type Temp,
} from "./model.ts";
import { MOVE_MS, playFlip, reducedMotion } from "./motion.ts";
import {
	Account,
	cap,
	deadlineText,
	Meta,
	Ring,
	TempTag,
	todo,
} from "./parts.tsx";
import { Sheet } from "./Sheet.tsx";
import { Thermo } from "./Thermo.tsx";

type Tab = "prioridades" | "perda" | "prospeccao";
const TABS: { key: Tab; label: string; short: string }[] = [
	{ key: "prioridades", label: "Prioridades da semana", short: "Prioridades" },
	{ key: "perda", label: "Atualize ou dê perda", short: "Frios" },
	{ key: "prospeccao", label: "Prospecção", short: "Prospecção" },
];

/** O potencial do herói conta até o valor só na primeira abertura. */
function useCountUp(target: number, active: boolean) {
	const [v, setV] = useState(active ? 0 : target);
	useEffect(() => {
		if (!active) {
			setV(target);
			return;
		}
		let raf = 0;
		const t0 = performance.now() + 80;
		const step = (now: number) => {
			const k = Math.min(1, Math.max(0, (now - t0) / 520));
			setV(Math.round(target * (1 - (1 - k) ** 3)));
			if (k < 1) raf = requestAnimationFrame(step);
		};
		raf = requestAnimationFrame(step);
		return () => cancelAnimationFrame(raf);
	}, [target, active]);
	return v;
}

function Hero({
	d,
	intro,
	waiting,
	swapped,
	onSwapDone,
	onOpen,
}: {
	d: DealView;
	intro: boolean;
	waiting: boolean;
	swapped: boolean;
	onSwapDone: () => void;
	onOpen: (id: string) => void;
}) {
	const pot = useCountUp(d.potential, intro);
	const t = todo(d);
	return (
		<article
			className={`card hero lift${intro ? " intro" : ""}${swapped ? " swap-in" : ""}${waiting ? " waiting" : ""}`}
			data-open={d.id}
			aria-hidden={waiting || undefined}
			onClick={() => onOpen(d.id)}
			onAnimationEnd={onSwapDone}
		>
			<div className="hero-head">
				<div>
					<Meta d={d} />
					<h2>{d.product}</h2>
					<Account d={d} className="acct" />
				</div>
				{d.score !== undefined && (
					<div className="ring-cap">
						<Ring score={d.score} size="lg" />
						<span>Score</span>
					</div>
				)}
			</div>
			<p className="hero-pot">
				<span className="num">{usd(pot)}</span>de potencial
			</p>
			<div className="hero-do">
				<h3>{t.title}.</h3>
				<p>{d.phrase}</p>
			</div>
			<div className="hero-foot">
				<button
					type="button"
					className="pill primary"
					data-open={d.id}
					tabIndex={waiting ? -1 : undefined}
					onClick={(e) => {
						e.stopPropagation();
						onOpen(d.id);
					}}
				>
					Ver o motivo
				</button>
			</div>
		</article>
	);
}

/** D46: o nº 1 tem score baixo; o herói vira a ação que mais pesa na semana. */
function ActionHero({
	action,
	m,
	waiting,
	swapped,
	onSwapDone,
	go,
	fromTeam,
}: {
	action: HeroAction;
	m: SellerModel;
	fromTeam: boolean;
	waiting: boolean;
	swapped: boolean;
	onSwapDone: () => void;
	go: (t: Tab) => void;
}) {
	const pros = action === "prospeccao";
	const info = actionInfo(m, action);
	const top = m.focus[0] as DealView;
	return (
		<article
			className={`card hero hero-action${swapped ? " swap-in" : ""}${waiting ? " waiting" : ""}`}
			aria-hidden={waiting || undefined}
			onAnimationEnd={onSwapDone}
		>
			<div>
				{pros ? (
					<span className="temp">
						<Icon name="users-three" />
						Prospecção
					</span>
				) : (
					<TempTag temp="frio" label="Frios" />
				)}
				<h2>{info.title}</h2>
				<p className="acct">
					{usd(info.total)} a preço de lista
					{pros
						? ". Ainda sem data de início no CRM."
						: `, abertos há mais de ${STALE_AFTER} dias.`}
				</p>
			</div>
			<div className="hero-do">
				<h3>{pros ? "Faça o primeiro contato." : "Atualize ou dê perda."}</h3>
				<p>
					{fromTeam ? `O nº 1 de ${first(m.name)}` : "O seu nº 1"},{" "}
					{top.product}, tem score {top.score}: o potencial dele é baixo perto
					dos negócios de todos os vendedores. Por isso a semana começa{" "}
					{pros ? "pela prospecção" : "pelos frios"}.
				</p>
			</div>
			<div className="hero-foot">
				<button
					type="button"
					className="pill primary"
					tabIndex={waiting ? -1 : undefined}
					onClick={() => go(action)}
				>
					{pros ? "Ver a prospecção" : "Ver os frios"}
				</button>
			</div>
		</article>
	);
}

function MiniCard({
	d,
	i,
	intro,
	onOpen,
}: {
	d: DealView;
	i: number;
	intro: boolean;
	onOpen: (id: string) => void;
}) {
	return (
		<button
			type="button"
			className={`card mini lift${intro ? " intro" : ""}`}
			style={intro ? { animationDelay: `${120 + i * 40}ms` } : undefined}
			data-flip={d.id}
			data-open={d.id}
			onClick={() => onOpen(d.id)}
		>
			<Meta d={d} />
			<span className="mini-name">
				<span className="mini-product">{d.product}</span>
				<Account d={d} className="acct" />
			</span>
			<span className="rank">{d.position}º</span>
			<span className="pot">{usd(d.potential)}</span>
			{d.score !== undefined && <Ring score={d.score} size="sm" />}
		</button>
	);
}

function Row({ d, onOpen }: { d: DealView; onOpen: (id: string) => void }) {
	const t = d.temp;
	return (
		<button
			type="button"
			className="row"
			data-flip={d.id}
			data-open={d.id}
			onClick={() => onOpen(d.id)}
		>
			<span className="sc">
				{t === "frio" ? (
					<span className="t-frio">
						<Icon name="snowflake" />
					</span>
				) : (
					d.score
				)}
			</span>
			<span className="nm">
				<span className="nm-product">{d.product}</span>
				<Account d={d} className="acct" />
			</span>
			<span className="meta-cell">
				{t === null ? null : t === "frio" ? (
					<span className="due">Aberto há {days(d.age ?? 0)}</span>
				) : (
					<TempTag temp={t} label={cap(deadlineText(d))} />
				)}
			</span>
			<span className="v">
				{usd(t === "frio" || t === null ? d.price : d.potential)}
			</span>
			<span className="chev">
				<Icon name="caret-right" />
			</span>
		</button>
	);
}

function Empty({
	icon,
	title,
	text,
	action,
}: {
	icon: IconName;
	title: string;
	text: string;
	action?: { label: string; go: () => void };
}) {
	return (
		<section className="card empty">
			<span className="empty-icon">
				<Icon name={icon} />
			</span>
			<h2>{title}</h2>
			<p>{text}</p>
			{action && (
				<button type="button" className="pill primary" onClick={action.go}>
					{action.label}
				</button>
			)}
		</section>
	);
}

function ThermoCard({
	m,
	title,
	intro,
	pmax,
	onOpen,
}: {
	m: SellerModel;
	title: string;
	intro: boolean;
	pmax: number;
	onOpen: (id: string) => void;
}) {
	const all = [...m.focus, ...m.review];
	const parts = (["quente", "esfriando", "frio"] as const).map((k) => {
		const l = all.filter((d) => d.temp === k);
		return { k, n: l.length, v: l.reduce((a, d) => a + d.price, 0) };
	});
	const legend: Record<Temp, string> = {
		quente: "Quentes",
		esfriando: "Esfriando",
		frio: "Frios",
	};
	return (
		<section className={`card thermo-card${intro ? " intro-fade" : ""}`}>
			<div>
				<h2>{title}</h2>
				<p className="sub">
					{plural(all.length, "negócio em andamento", "negócios em andamento")}{" "}
					pela idade. Quanto maior o ponto, maior o potencial. Os números marcam
					os 5 primeiros.
				</p>
			</div>
			<Thermo deals={all} pmax={pmax} intro={intro} onOpen={onOpen} />
			<div className="th-legend">
				{parts.map((p) => (
					<div key={p.k}>
						<TempTag temp={p.k} label={legend[p.k]} />
						<span className="v">{usdShort(p.v)}</span>
						<span className="c">{plural(p.n, "negócio", "negócios")}</span>
					</div>
				))}
			</div>
			<p className="foot">Valores a preço de lista.</p>
		</section>
	);
}

/** Estado vazio da semana: diz o que fazer, na voz de quem está vendo (a pessoa ou o gestor). */
function emptyWeek(
	m: SellerModel,
	fromTeam: boolean,
	go: (t: Tab) => void,
): ReactNode {
	const name = first(m.name);
	const you = (own: string, other: string) => (fromTeam ? other : own);
	if (m.empty === "sem-negocios")
		return (
			<Empty
				icon="tray"
				title="Nada para avançar esta semana."
				text={you(
					"Você não tem negócio no CRM. Cadastre os contatos novos para eles aparecerem aqui.",
					`${name} não tem negócio no CRM. Combine com ${name} quais contatos novos cadastrar.`,
				)}
			/>
		);
	if (m.empty === "revisar")
		return (
			<Empty
				icon="snowflake"
				title="Nada para avançar esta semana."
				text={`${you("Nenhum negócio seu", `Nenhum negócio de ${name}`)} está quente ou esfriando. ${you("Você tem", `${name} tem`)} ${plural(m.review.length, "negócio frio", "negócios frios")}: confirme com o cliente ou dê perda.`}
				action={{ label: "Ver os frios", go: () => go("perda") }}
			/>
		);
	if (m.empty === "iniciar")
		return (
			<Empty
				icon="tray"
				title="Nada para avançar esta semana."
				text="Comece pela prospecção: são os contatos que ainda não viraram negócio."
				action={{ label: "Ver a prospecção", go: () => go("prospeccao") }}
			/>
		);
	return (
		<Empty
			icon="tray"
			title="Nada em andamento nesta data."
			text={you(
				"Cadastre os negócios novos no CRM ou combine com o seu gestor quais empresas abordar.",
				`Combine com ${name} quais empresas abordar e cadastre os negócios novos no CRM.`,
			)}
		/>
	);
}

export function SellerView({
	day,
	name,
	fromTeam,
	intro,
	pmax,
	onBack,
}: {
	day: DayModel;
	name: string;
	fromTeam: boolean;
	intro: boolean;
	pmax: number;
	onBack?: () => void;
}) {
	const m = useMemo(() => sellerModel(day, name), [day, name]);
	const [tab, setTab] = useState<Tab>("prioridades");
	const [all, setAll] = useState(false);
	const [openId, setOpenId] = useState<string | null>(null);

	// Troca de data com outro nº 1 (D44): o herói antigo some na hora (ele mostraria dados da
	// outra data, inclusive a empresa, D34); os cartões mudam de lugar; depois o herói novo aparece.
	// A chave cobre os dois heróis: o negócio nº 1 ou a ação da semana (D46).
	const heroNow = m.focus[0];
	const action = heroAction(m, day.t);
	const heroKey = heroNow && (action ? `acao-${action}` : heroNow.id);
	const [shownKey, setShownKey] = useState(heroKey);
	const [swapped, setSwapped] = useState(false);
	const waiting = !!heroKey && shownKey !== heroKey;
	useEffect(() => {
		if (!heroKey || heroKey === shownKey) return;
		if (reducedMotion() || shownKey === undefined) {
			setShownKey(heroKey);
			return;
		}
		const id = setTimeout(() => {
			setShownKey(heroKey);
			setSwapped(true);
		}, MOVE_MS);
		return () => clearTimeout(id);
	}, [heroKey, shownKey]);
	// biome-ignore lint/correctness/useExhaustiveDependencies: a animação roda a cada troca de data
	useLayoutEffect(() => {
		playFlip();
	}, [day]);

	const open = [...m.focus, ...m.review, ...m.prospect].find(
		(d) => d.id === openId,
	);
	const onOpen = useCallback((id: string) => setOpenId(id), []);
	const close = useCallback(() => setOpenId(null), []);
	const pickTab = (t: Tab) => {
		setTab(t);
		setOpenId(null);
	};
	// Setas do teclado entre as abas (padrão de tablist).
	const onTabKey = (e: KeyboardEvent) => {
		const i = TABS.findIndex((x) => x.key === tab);
		const step = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
		if (!step) return;
		const next = TABS[(i + step + TABS.length) % TABS.length]?.key ?? tab;
		pickTab(next);
		requestAnimationFrame(() =>
			document.getElementById(`aba-${next}`)?.focus(),
		);
	};

	const g = greeting(m, action);
	const counts = {
		prioridades: m.focus.length,
		perda: m.review.length,
		prospeccao: m.prospect.length,
	};

	let body: ReactNode;
	if (tab === "prioridades") {
		if (!heroNow) body = emptyWeek(m, fromTeam, pickTab);
		else {
			const next = m.focus.slice(action ? 0 : 1, 5);
			const rest = m.focus.slice(5);
			body = (
				<>
					{action ? (
						<ActionHero
							key={heroKey}
							action={action}
							m={m}
							waiting={waiting}
							swapped={swapped && !waiting}
							onSwapDone={() => setSwapped(false)}
							go={pickTab}
							fromTeam={fromTeam}
						/>
					) : (
						<Hero
							key={heroKey}
							d={heroNow}
							intro={intro}
							waiting={waiting}
							swapped={swapped && !waiting}
							onSwapDone={() => setSwapped(false)}
							onOpen={onOpen}
						/>
					)}
					{next.length > 0 && (
						<div className="next">
							{next.map((d, i) => (
								<MiniCard
									key={d.id}
									d={d}
									i={i}
									intro={intro}
									onOpen={onOpen}
								/>
							))}
						</div>
					)}
					{rest.length > 0 && (
						<div className="more">
							<button
								type="button"
								className="pill plain"
								aria-expanded={all}
								onClick={() => setAll(!all)}
							>
								{all ? "Mostrar menos" : `Ver todos os ${num(m.focus.length)}`}
								<Icon name="caret-down" />
							</button>
						</div>
					)}
					{rest.length > 0 && all && (
						<div className="card list">
							{rest.map((d) => (
								<Row key={d.id} d={d} onOpen={onOpen} />
							))}
						</div>
					)}
				</>
			);
		}
	} else if (tab === "perda") {
		const total = m.review.reduce((a, d) => a + d.price, 0);
		body = m.review.length ? (
			<>
				<p className="list-intro">
					<b>
						{plural(m.review.length, "negócio aberto", "negócios abertos")} há
						mais de {STALE_AFTER} dias
					</b>
					, {usdShort(total)} a preço de lista. Nenhum negócio da base fechou
					depois disso. Confirme com o cliente ou dê perda, do mais caro para o
					mais barato.
				</p>
				<div className="card list">
					{m.review.map((d) => (
						<Row key={d.id} d={d} onOpen={onOpen} />
					))}
				</div>
			</>
		) : (
			<Empty
				icon="check-circle"
				title="Nada para atualizar."
				text={`Nenhum negócio passou de ${STALE_AFTER} dias aberto. Continue avançando as prioridades da semana.`}
			/>
		);
	} else {
		body =
			day.t !== REFERENCE_DATE ? (
				<Empty
					icon="tray"
					title="Prospecção só na data mais recente."
					text="O CRM não registra quando cada prospecção começou, então não dá para saber se ela já existia nesta data."
				/>
			) : m.prospect.length ? (
				<>
					<p className="list-intro">
						Contatos que ainda não viraram negócio, do maior preço de lista para
						o menor.
					</p>
					<div className="card list">
						{m.prospect.map((d) => (
							<Row key={d.id} d={d} onOpen={onOpen} />
						))}
					</div>
				</>
			) : (
				<Empty
					icon="tray"
					title="Nenhuma prospecção esperando contato."
					text="Quando um contato novo entrar no CRM, ele aparece aqui, do maior preço para o menor."
				/>
			);
	}

	return (
		<>
			{fromTeam && (
				<button type="button" className="back" onClick={onBack}>
					<Icon name="caret-left" />
					Minha equipe
				</button>
			)}
			<div className="top">
				<p className="greet">
					{fromTeam
						? `A semana de ${first(m.name)}.`
						: `Bom dia, ${first(m.name)}.`}{" "}
					{g.lead && <b>{g.lead}</b>} {g.urg}
				</p>
				<div
					className="tabs seg"
					role="tablist"
					aria-label="Listas"
					onKeyDown={onTabKey}
				>
					{TABS.map((x) => (
						<button
							key={x.key}
							id={`aba-${x.key}`}
							type="button"
							role="tab"
							aria-selected={tab === x.key}
							aria-controls="lista"
							tabIndex={tab === x.key ? 0 : -1}
							onClick={() => pickTab(x.key)}
						>
							<span className="lg-only">{x.label}</span>
							<span className="sm-only">{x.short}</span>{" "}
							<span className="n">{num(counts[x.key])}</span>
						</button>
					))}
				</div>
			</div>
			{day.t !== REFERENCE_DATE && (
				<p className="past-note">
					Você está vendo a carteira como estava em {date(day.t)}. A empresa e a
					prospecção ficam ocultas: revelariam o que aconteceu depois.
				</p>
			)}
			<div className="desk">
				<div
					className="stack"
					role="tabpanel"
					id="lista"
					aria-labelledby={`aba-${tab}`}
				>
					{body}
				</div>
				{m.hasDeals && (
					<div className="side">
						<ThermoCard
							m={m}
							title={`${fromTeam ? `A carteira de ${first(m.name)}` : "Sua carteira"} no tempo`}
							intro={intro}
							pmax={pmax}
							onOpen={onOpen}
						/>
					</div>
				)}
			</div>
			<Sheet open={!!open} onClose={close} label="Detalhe do negócio">
				{open && (
					<DealPanel
						key={open.id}
						d={open}
						day={day}
						whose={fromTeam ? `semana de ${first(m.name)}` : "sua semana"}
					/>
				)}
			</Sheet>
		</>
	);
}
