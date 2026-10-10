// Minha equipe (D29, D41): o protagonista é a frase com o principal problema da equipe e quem
// concentra o valor frio. Retrato da carteira, não ranking: os dados não separam vendedor,
// carteira e região.

import { useMemo, useState } from "react";
import type { AgentStatus } from "../core/analysis.ts";
import { first, initials, num, plural, usd, usdShort } from "./format.ts";
import { Icon } from "./Icon.tsx";
import {
	actionInfo,
	type DayModel,
	heroAction,
	MANAGERS,
	sellerModel,
	teamModel,
} from "./model.ts";
import { Ring } from "./parts.tsx";
import { MiniThermo, Thermo } from "./Thermo.tsx";

const totalOf = (a: AgentStatus) =>
	a.slices["no-prazo"].listPrice +
	a.slices.esfriando.listPrice +
	a.slices.parado.listPrice;
const narrow = () => matchMedia("(max-width: 1060px)").matches;

function Preview({
	day,
	name,
	pmax,
	onOpen,
}: {
	day: DayModel;
	name: string;
	pmax: number;
	onOpen: (name: string) => void;
}) {
	const m = useMemo(() => sellerModel(day, name), [day, name]);
	// A prévia segue a regra da semana do vendedor (D46): com score baixo, começa pela ação.
	const action = heroAction(m, day.t);
	const info = action && actionInfo(m, action);
	return (
		<section className="card preview" key={name}>
			<div>
				<h2>{name}</h2>
				<p className="sub">
					{plural(m.focus.length, "prioridade", "prioridades")} na semana.{" "}
					{plural(m.review.length, "frio", "frios")} para atualizar ou dar
					perda.
				</p>
			</div>
			<Thermo deals={[...m.focus, ...m.review]} pmax={pmax} />
			{info && (
				<div>
					<p className="pv-title">
						Começaria{" "}
						{action === "prospeccao" ? "pela prospecção" : "pelos frios"}
					</p>
					<p className="pv-action">
						{info.title}, {usd(info.total)} a preço de lista. O nº 1 tem score{" "}
						{m.focus[0]?.score}.
					</p>
				</div>
			)}
			{m.focus.length > 0 && (
				<div>
					<p className="pv-title">
						{info ? "Prioridades" : "Começaria por estes"}
					</p>
					{m.focus.slice(0, 3).map((d) => (
						<div className="pv-row" key={d.id}>
							{d.score !== undefined && <Ring score={d.score} size="sm" />}
							<span className="nm">
								{d.product}
								{d.account !== undefined && (
									<span className={d.account ? "" : "none"}>
										{d.account ?? "Sem empresa no CRM"}
									</span>
								)}
							</span>
							<span className="v">{usd(d.potential)}</span>
						</div>
					))}
				</div>
			)}
			<button
				type="button"
				className="pill primary"
				onClick={() => onOpen(name)}
			>
				Abrir a semana de {first(name)}
			</button>
		</section>
	);
}

export function TeamView({
	day,
	manager,
	viewerIsManager,
	pmax,
	onOpen,
	onPickTeam,
	ownTeam,
}: {
	day: DayModel;
	manager: string;
	viewerIsManager: boolean;
	pmax: number;
	onOpen: (seller: string) => void;
	onPickTeam: (manager: string) => void;
	ownTeam: string;
}) {
	const status = useMemo(() => teamModel(day, manager), [day, manager]);
	const models = useMemo(
		() => new Map(status.map((a) => [a.agent, sellerModel(day, a.agent)])),
		[day, status],
	);
	const active = status.filter((a) => a.open > 0);
	const idle = status.filter((a) => a.open === 0);
	const [picked, setPicked] = useState<string | undefined>(undefined);
	const previewed = active.some((a) => a.agent === picked)
		? picked
		: active[0]?.agent;

	const cold = active.reduce((s, a) => s + a.slices.parado.listPrice, 0);
	const total = active.reduce((s, a) => s + totalOf(a), 0);
	const top = active[0];
	const coldMax = Math.max(...active.map((a) => a.slices.parado.deals), 1);
	// Acima de 99,5%, o arredondamento diria 100% com prioridades na equipe: uma casa decimal.
	const share = total ? cold / total : 0;
	const pct =
		share >= 0.995 && share < 1
			? (share * 100).toLocaleString("pt-BR", { maximumFractionDigits: 1 })
			: String(Math.round(share * 100));
	// Prospecção da equipe (só na data padrão, D13): na Central, é onde está o trabalho.
	const prospect = [...models.values()].flatMap((m) => m.prospect);
	const live = status.reduce((s, a) => s + a.focus, 0);
	// Quem não tem o que avançar nesta semana (D29: situação, não ranking).
	const noFocus = status.filter((a) => a.focus === 0).map((a) => a.agent);

	return (
		<>
			<section className="team-head">
				{/* D57: qualquer equipe, sem voltar à entrada (filtro por regional e gestor) */}
				<div className="team-pick">
					<label htmlFor="ver-equipe">Ver a equipe de</label>
					<select
						id="ver-equipe"
						value={manager}
						onChange={(e) => onPickTeam(e.target.value)}
					>
						{[...new Set(MANAGERS.map((m) => m.regional))].sort().map((r) => (
							<optgroup key={r} label={`Regional ${r}`}>
								{MANAGERS.filter((m) => m.regional === r).map((m) => (
									<option key={m.name} value={m.name}>
										{m.name}, {m.regional}
									</option>
								))}
							</optgroup>
						))}
					</select>
					{ownTeam && manager !== ownTeam && (
						<button
							type="button"
							className="inline-link"
							onClick={() => onPickTeam(ownTeam)}
						>
							Voltar à minha equipe
						</button>
					)}
				</div>
				<p className="greet">
					{viewerIsManager
						? `Bom dia, ${first(manager)}.`
						: `A equipe de ${manager}.`}
				</p>
				<h1 className="lead-h1">
					{!active.length
						? "Nenhum negócio em andamento na equipe."
						: cold && top
							? `${usdShort(cold)} frios na equipe. ${first(top.agent)} concentra ${usdShort(top.slices.parado.listPrice)}.`
							: "Nenhum negócio frio na equipe."}
				</h1>
				{cold > 0 && (
					<p className="lead-sub">
						{pct}% do valor em andamento está frio: aberto há mais de 138 dias,
						quando nenhum negócio da base fechou. Peça para atualizar ou dar
						perda.
					</p>
				)}
				{prospect.length > live && (
					<p className="lead-note prospect-note">
						{plural(prospect.length, "negócio", "negócios")} em prospecção
						esperam o primeiro contato (
						{usdShort(prospect.reduce((s, d) => s + d.price, 0))} a preço de
						lista), contra{" "}
						{plural(
							live,
							"negócio quente ou esfriando",
							"negócios quentes ou esfriando",
						)}
						. A equipe precisa transformar prospecção em negócio.
					</p>
				)}
				{noFocus.length > 0 && (
					<p className="lead-note">
						Sem prioridade nesta semana:{" "}
						{noFocus.map((n, i) => (
							<span key={n}>
								{i > 0 && (i === noFocus.length - 1 ? " e " : ", ")}
								<button
									type="button"
									className="inline-link"
									onClick={() => onOpen(n)}
								>
									{n}
								</button>
							</span>
						))}
						.
					</p>
				)}
			</section>
			<div className="desk">
				<div>
					<div className="card">
						{active.map((a) => {
							const m = models.get(a.agent);
							return (
								<button
									key={a.agent}
									type="button"
									className="member"
									data-flip={`m-${a.agent}`}
									aria-current={previewed === a.agent}
									onClick={() =>
										narrow() ? onOpen(a.agent) : setPicked(a.agent)
									}
								>
									<span className="avatar lg">{initials(a.agent)}</span>
									<span className="nm">
										{a.agent}
										<span>
											{plural(a.focus, "prioridade", "prioridades")},{" "}
											{plural(a.slices.parado.deals, "frio", "frios")}
										</span>
									</span>
									<MiniThermo
										deals={m ? [...m.focus, ...m.review] : []}
										coldMax={coldMax}
									/>
									<span className="v">
										{usdShort(a.slices.parado.listPrice)}
										<span>frios</span>
									</span>
									<span className="chev">
										<Icon name="caret-right" />
									</span>
								</button>
							);
						})}
						{idle.map((a) => (
							<button
								key={a.agent}
								type="button"
								className="member"
								onClick={() => onOpen(a.agent)}
							>
								<span className="avatar lg">{initials(a.agent)}</span>
								<span className="nm">
									{a.agent}
									<span>
										{models.get(a.agent)?.hasDeals
											? a.prospecting
												? `Sem negócio em andamento, ${num(a.prospecting)} em prospecção`
												: "Sem negócio em andamento"
											: "Nenhum negócio no CRM"}
									</span>
								</span>
								<span className="chev">
									<Icon name="caret-right" />
								</span>
							</button>
						))}
					</div>
					<p className="note">
						Retrato da carteira, não ranking: os dados não separam o efeito do
						vendedor do efeito da carteira e da região. Valores a preço de
						lista.
					</p>
				</div>
				{previewed && (
					<div className="side">
						<Preview
							key={previewed}
							day={day}
							name={previewed}
							pmax={pmax}
							onOpen={onOpen}
						/>
					</div>
				)}
			</div>
		</>
	);
}
