// O painel do negócio: a posição, a régua, a frase com o mesmo número da conta e o que fazer.

import { date, days, num, usd } from "./format.ts";
import type { DayModel, DealView } from "./model.ts";
import { Meta, Ring, todo } from "./parts.tsx";
import { Thermo } from "./Thermo.tsx";

export function DealPanel({
	d,
	day,
	whose,
}: {
	d: DealView;
	day: DayModel;
	whose: string;
}) {
	const t = todo(d);
	const live = d.temp === "quente" || d.temp === "esfriando";
	const rank =
		d.priceRank && d.priceRank !== d.position
			? ` Pela ordem de preço, estaria em ${d.priceRank}º.`
			: "";
	return (
		<>
			<div>
				<h2>{d.product}</h2>
				<p className="acct">
					{d.account === undefined
						? ""
						: `${d.account ?? "Sem empresa no CRM"}. `}
					Negócio {d.id}.
				</p>
			</div>
			{live && d.score !== undefined && (
				<div className="score-line">
					<Ring score={d.score} size="md" />
					<p>
						{d.score === 0
							? "Está entre os de menor potencial"
							: `Mais potencial que ${d.score}%`}{" "}
						dos {num(day.scoreBase)} negócios quentes e esfriando de todos os
						vendedores em {date(day.t)}. {d.position}º na {whose}.{rank}
					</p>
				</div>
			)}
			{d.temp !== null && (
				<div className="panel-ruler">
					<Meta d={d} />
					<Thermo deals={[d]} pmax={d.potential || 1} single />
				</div>
			)}
			{live ? (
				<>
					<p className="why">{d.phrase}</p>
					<dl className="calc">
						<dt>Preço de lista</dt>
						<dd>{usd(d.price)}</dd>
						<dt>Chance de fechar, pelo histórico</dt>
						<dd>× {d.percent}%</dd>
						<dt className="sum">Potencial</dt>
						<dd className="sum">{usd(d.potential)}</dd>
					</dl>
				</>
			) : (
				<dl className="calc">
					<dt>Preço de lista</dt>
					<dd>{usd(d.price)}</dd>
					{d.age !== null && (
						<>
							<dt>Aberto há</dt>
							<dd>{days(d.age)}</dd>
						</>
					)}
				</dl>
			)}
			<div className="todo">
				<h3>{t.title}</h3>
				<p>{t.text}</p>
			</div>
			{live && (
				<p className="foot">
					A chance usa só a idade do negócio. Vendedor, produto e empresa foram
					testados e não mudam a ordem.{" "}
					<a href="#como-funciona">Como funciona</a>
				</p>
			)}
		</>
	);
}
