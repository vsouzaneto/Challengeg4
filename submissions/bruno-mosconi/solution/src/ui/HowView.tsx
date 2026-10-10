// Como funciona (incremento 5, CA16): a regra numa tela, com o nº 1 do Zane passo a passo; as três
// provas com o número real; e o que a lista não sabe. Texto principal na língua do gerente; os
// termos técnicos ficam em "Ver detalhes" (e no README).

import type { ReactNode } from "react";
import { TOP_N, WINDOW_DAYS } from "../core/backtest.ts";
import { shownPercent } from "../core/reason.ts";
import {
	COOLING_FROM,
	curveHalfWidth,
	REFERENCE_DATE,
	STALE_AFTER,
} from "../core/rules.ts";
import comoClaro from "./assets/como-funciona-claro.webp";
import comoEscuro from "./assets/como-funciona-escuro.webp";
import { date, days, first, num, usd } from "./format.ts";
import {
	type DayModel,
	evidenceOnce,
	illusionCurve,
	sellerModel,
} from "./model.ts";
import { Art } from "./Pages.tsx";
import { Account, Meta, Ring, TempTag } from "./parts.tsx";
import { Thermo } from "./Thermo.tsx";

const EXAMPLE = "Zane Levy";
/** Proporção em % inteira, para o texto principal. */
const p100 = (x: number) => Math.round(x * 100);
/** Com uma casa, para os detalhes. */
const p1 = (x: number) =>
	(x * 100).toLocaleString("pt-BR", {
		minimumFractionDigits: 1,
		maximumFractionDigits: 1,
	});
const pv = (p: number) =>
	p < 0.001
		? "menor que 0,001"
		: p.toLocaleString("pt-BR", { maximumFractionDigits: p < 0.01 ? 4 : 2 });
const ci = ([lo, hi]: [number, number]) => `${p1(lo)} a ${p1(hi)} pontos`;

function More({ children }: { children: ReactNode }) {
	return (
		<details className="more-details">
			<summary>Ver detalhes</summary>
			<div className="more-body">{children}</div>
		</details>
	);
}

function Bar({
	label,
	v,
	strong,
}: {
	label: string;
	v: number;
	strong?: boolean;
}) {
	return (
		<div className={`bar-row${strong ? " strong" : ""}`}>
			<span className="bar-label">{label}</span>
			<span className="bar-track" aria-hidden="true">
				<span className="bar-fill" style={{ transform: `scaleX(${v})` }} />
			</span>
			<span className="bar-v">{p100(v)}%</span>
		</div>
	);
}

export function HowView({ day }: { day: DayModel }) {
	const ev = evidenceOnce();
	const zane = sellerModel(day, EXAMPLE).focus[0];
	const wrong = illusionCurve(day.t);
	const bt = ev.backtest;
	const bands = day.curve.map((c, i) => {
		const to = (day.curve[i + 1]?.from ?? STALE_AFTER + 1) - 1;
		return {
			temp:
				c.from < COOLING_FROM ? ("quente" as const) : ("esfriando" as const),
			age: `${c.from} a ${to} dias`,
			short: `${c.from}–${to}`,
			v: shownPercent(c.chance),
			wrong: shownPercent(wrong[i]?.chance ?? 0),
			mine:
				zane?.age !== null &&
				zane?.age !== undefined &&
				zane.age >= c.from &&
				zane.age <= to,
			c,
		};
	});
	const seller = ev.factors.find((f) => f.key === "agent");
	const range = (rates: readonly number[]) =>
		`${p100(Math.min(...rates))}% a ${p100(Math.max(...rates))}%`;
	const lo = 0.4;
	const hi = 0.85;
	const at = (r: number) =>
		`${((Math.min(hi, Math.max(lo, r)) - lo) / (hi - lo)) * 100}%`;
	const last = ev.calibration.at(-1);

	return (
		<section className="how">
			<Art
				light={comoClaro}
				dark={comoEscuro}
				className="how-art"
				alt="Sete placas de vidro fosco em fila, do laranja quente, à esquerda, ao cinza frio, à direita."
			/>
			<header className="how-head">
				<h1>Como a lista é feita</h1>
				<p className="lead-sub">
					O preço de lista vezes a chance de fechar, que depende só da idade,
					decide a ordem.
				</p>
			</header>

			<section className="card rule" aria-labelledby="regra">
				<div className="rule-table">
					<h2 id="regra">
						De cada 100 negócios que chegaram a cada idade ainda em andamento,
						quantos fecharam venda
					</h2>
					<table>
						<thead>
							<tr>
								<th scope="col">Situação</th>
								<th scope="col">Idade</th>
								<th scope="col" className="r">
									Fecharam
								</th>
							</tr>
						</thead>
						<tbody>
							{bands.map((b) => (
								<tr key={b.age} className={b.mine ? "mine" : undefined}>
									<td>
										<TempTag temp={b.temp} />
									</td>
									<td>
										{b.age}
										{b.mine && <span className="mine-tag">o exemplo</span>}
									</td>
									<td className="r v">{b.v}</td>
								</tr>
							))}
							<tr>
								<td>
									<TempTag temp="frio" />
								</td>
								<td>Mais de {STALE_AFTER} dias</td>
								<td className="r v">0</td>
							</tr>
						</tbody>
					</table>
				</div>

				{zane ? (
					<ol className="steps">
						<li>
							<h3>A idade diz a temperatura</h3>
							<p>
								O nº 1 do {first(EXAMPLE)} em {date(day.t)}: {zane.product}
								<Account d={zane} className="acct-inline" />, aberto há{" "}
								{days(zane.age ?? 0)}.
							</p>
							<Meta d={zane} />
							<Thermo deals={[zane]} pmax={zane.potential || 1} single />
						</li>
						<li>
							<h3>O potencial decide a ordem</h3>
							<p>{zane.phrase}</p>
							<dl className="calc">
								<dt>Preço de lista</dt>
								<dd>{usd(zane.price)}</dd>
								<dt>Chance de fechar, pelo histórico</dt>
								<dd>× {zane.percent}%</dd>
								<dt className="sum">Potencial</dt>
								<dd className="sum">{usd(zane.potential)}</dd>
							</dl>
						</li>
						<li>
							<h3>O score mostra a posição</h3>
							<div className="score-line">
								{zane.score !== undefined && (
									<Ring score={zane.score} size="md" />
								)}
								<p>
									Score {zane.score}: o potencial dele passa o de {zane.score}{" "}
									de cada 100 negócios quentes e esfriando de todos os
									vendedores.
								</p>
							</div>
						</li>
					</ol>
				) : (
					<p className="note">
						{EXAMPLE} não tem negócio quente ou esfriando em {date(day.t)}.
					</p>
				)}
			</section>

			<h2 className="how-h2">Por que dá para confiar na lista</h2>

			<section className="card proof" aria-labelledby="prova-idade">
				<h3 id="prova-idade">
					Quanto mais tempo o negócio fica aberto, menor a chance de fechar.
				</h3>
				<div className="pair-legend">
					<span className="k k-real">
						Todos os negócios que chegaram à idade
					</span>
					<span className="k k-wrong">Só os já ganhos ou perdidos</span>
				</div>
				<div
					className="pair-chart"
					role="img"
					aria-label={`De cada 100 negócios, quantos fecharam, por idade. Todos: ${bands.map((b) => b.v).join(", ")}. Só os já ganhos ou perdidos: ${bands.map((b) => b.wrong).join(", ")}.`}
				>
					{bands.map((b) => (
						<div key={b.age} className="pair">
							<div className="pair-bars">
								<span className="pb real" style={{ height: `${b.v}%` }}>
									<b>{b.v}</b>
								</span>
								<span className="pb wrong" style={{ height: `${b.wrong}%` }}>
									<b>{b.wrong}</b>
								</span>
							</div>
							<span className="pair-age">{b.short}</span>
						</div>
					))}
				</div>
				<p className="pair-axis">Idade do negócio, em dias</p>
				<table className="by-date pair-table">
					<caption>
						Os números do gráfico: de cada 100, quantos fecharam venda
					</caption>
					<thead>
						<tr>
							<th scope="col">Idade</th>
							<th scope="col" className="r">
								Todos os negócios
							</th>
							<th scope="col" className="r">
								Só os já ganhos ou perdidos
							</th>
						</tr>
					</thead>
					<tbody>
						{bands.map((b) => (
							<tr key={b.age}>
								<th scope="row">{b.age}</th>
								<td className="r">{b.v}</td>
								<td className="r">{b.wrong}</td>
							</tr>
						))}
					</tbody>
				</table>
				<div className="callout">
					<h4>O engano evitado</h4>
					<p>
						Olhando só os negócios já ganhos ou perdidos, pareceria que esperar
						ajuda. É ilusão: os que nunca fecham ficam fora da conta.
					</p>
				</div>
				<More>
					<p>
						Coorte: negócios iniciados até {STALE_AFTER} dias antes de{" "}
						{date(day.t)}, com o desfecho visto nessa data. Em cada faixa, a
						chance é ganhos ÷ negócios que passaram daquela idade ainda em
						andamento; quem continua aberto conta como não ganho. Negócios em
						risco por faixa: {bands.map((b) => num(b.c.atRisk)).join(", ")}.
						Margem de erro (IC 95%, Wilson) de no máximo ±
						{p1(curveHalfWidth(day.curve))} pontos.
					</p>
					<p>
						O cálculo errado usa só os concluídos: ganhos ÷ concluídos com ciclo
						maior que a idade. Ele deixa de fora os negócios que nunca fecharam,
						e por isso a chance parece subir com a idade.
					</p>
				</More>
			</section>

			<section className="card proof" aria-labelledby="prova-passado">
				<h3 id="prova-passado">Testamos a lista no passado.</h3>
				<p>
					Voltamos a datas de 2017, montamos a lista como se fosse aquele dia e
					vimos o que aconteceu. Os 10 primeiros de cada vendedor trouxeram{" "}
					{p100(bt.weighted)}% do que a carteira vendeu nos três meses
					seguintes; pelo preço, {p100(bt.price)}%; no sorteio,{" "}
					{p100(bt.random)}%.
				</p>
				<div className="bars">
					<Bar label="Pela lista (potencial)" v={bt.weighted} strong />
					<Bar label="Pelo preço" v={bt.price} />
					<Bar label="No sorteio" v={bt.random} />
				</div>
				<table className="by-date">
					<caption>O resultado se repetiu nas três datas.</caption>
					<thead>
						<tr>
							<th scope="col">Lista montada em</th>
							<th scope="col" className="r">
								Pela lista
							</th>
							<th scope="col" className="r">
								Pelo preço
							</th>
							<th scope="col" className="r">
								No sorteio
							</th>
						</tr>
					</thead>
					<tbody>
						{bt.dates.map((d) => (
							<tr key={d.t}>
								<th scope="row">{date(d.t)}</th>
								<td className="r">{p100(d.weighted)}%</td>
								<td className="r">{p100(d.price)}%</td>
								<td className="r">{p100(d.random)}%</td>
							</tr>
						))}
					</tbody>
				</table>
				<p>
					Um modelo de inteligência artificial mais complexo chegou a{" "}
					{p100(bt.ml)}%: uma diferença do tamanho que o acaso produz. Ficamos
					com a regra que o vendedor consegue explicar.
				</p>
				<More>
					<p>
						Backtest nas datas com histórico suficiente (
						{bt.dates.map((d) => date(d.t)).join(", ")}). Em cada data, curva,
						idade e coorte usam só o que se sabia no dia. Medida: receita dos
						negócios ganhos nos {WINDOW_DAYS} dias seguintes que estavam entre
						os {TOP_N} primeiros de cada vendedor ÷ receita ganha de todos os
						negócios em andamento do vendedor. Sorteio = valor esperado de{" "}
						{TOP_N} negócios ao acaso.
					</p>
					<p>
						Teste pareado, unidade = vendedor (as datas somadas): lista − preço
						= {p1(bt.weightedVsPrice.difference)} pontos (margem de erro de{" "}
						{ci(bt.weightedVsPrice.ci95)}, IC 95% bootstrap; p-valor{" "}
						{pv(bt.weightedVsPrice.pSignFlip)}). Contra "quente, depois
						esfriando, depois frio, e dentro de cada um pelo preço", empate:{" "}
						{p1(bt.weightedVsSituation.difference)} pontos (
						{ci(bt.weightedVsSituation.ci95)}; p-valor{" "}
						{pv(bt.weightedVsSituation.pSignFlip)}). O potencial fica porque dá
						a frase de motivo e o score.
					</p>
					<p>
						Modelo de ML: gradient boosting (analysis/significancia_ml.py), nas
						mesmas unidades vendedor × data: {p1(bt.ml)}% contra{" "}
						{p1(bt.weighted)}
						%; diferença de {p1(bt.mlVsWeighted.difference)} pontos (
						{ci(bt.mlVsWeighted.ci95)}; p-valor {pv(bt.mlVsWeighted.pSignFlip)}
						).
					</p>
				</More>
			</section>

			<section className="card proof" aria-labelledby="prova-fatores">
				<h3 id="prova-fatores">
					Testamos se vendedor, produto, região, setor e porte da empresa mudam
					a chance de fechar.
				</h3>
				<p>
					Não mudam: a diferença é do tamanho que o acaso produz. Por isso a
					lista não usa nenhum deles. Olhamos a taxa de ganho: de cada 100
					negócios concluídos, quantos foram ganhos. Cada ponto é um grupo (um
					vendedor, um produto, uma regional); a linha é a média,{" "}
					{p100(ev.overallWinRate)}
					%. A última coluna diz em quantas de 100 vezes o puro acaso daria uma
					diferença igual ou maior. Abaixo de 5 em 100, seria sinal de que o
					fator muda a taxa.
				</p>
				<div className="strips">
					{ev.factors.map((f) => (
						<div key={f.key} className="strip-row">
							<span className="strip-label">{f.label}</span>
							<span className="strip" aria-hidden="true">
								<span
									className="strip-mean"
									style={{ left: at(ev.overallWinRate) }}
								/>
								{f.rates.map((r, i) => (
									// biome-ignore lint/suspicious/noArrayIndexKey: os grupos não mudam de ordem
									<span key={i} className="strip-dot" style={{ left: at(r) }} />
								))}
							</span>
							<span className="strip-range">{range(f.rates)}</span>
							<span className="strip-p">{Math.round(f.p * 100)} em 100</span>
						</div>
					))}
				</div>
				<div className="callout">
					<h4>Para o gestor</h4>
					<p>
						O vendedor não muda a chance de fechar, mas muda quanto do funil
						dele esfria: dos negócios iniciados há mais de {STALE_AFTER} dias
						até {date(REFERENCE_DATE)}, os que continuam abertos vão de{" "}
						{p100(ev.agentCold.min)}% a {p100(ev.agentCold.max)}%, conforme o
						vendedor. Os dados não separam o efeito do vendedor do efeito da
						carteira e da região. A tela Minha equipe mostra quanto da carteira
						de cada um está frio.
					</p>
				</div>
				<More>
					<p>
						Taxa de ganho entre os concluídos (ganhos ÷ ganhos + perdidos) por
						grupo, com qui-quadrado de independência. p-valor:{" "}
						{ev.factors
							.map((f) => `${f.label.toLowerCase()} ${pv(f.p)}`)
							.join("; ")}
						. Porte em quartis das 85 empresas. Diferença entre o melhor e o
						pior vendedor:{" "}
						{p1(
							Math.max(...(seller?.rates ?? [0])) -
								Math.min(...(seller?.rates ?? [0])),
						)}{" "}
						pontos.
					</p>
					<p>
						Na coorte de {date(REFERENCE_DATE)} (aberto conta como não ganho,
						sem a correção de entrada tardia), o vendedor muda o desfecho
						(p-valor {pv(ev.agentCold.p)}), e a regional também: o efeito está
						no que fica parado, não na taxa de ganho. Ele multiplica todos os
						negócios do vendedor e não muda a ordem da lista dele. Setor e porte
						só podem ser testados entre concluídos:{" "}
						{p100(ev.noAccount.inProgress)}% dos negócios em andamento não têm
						empresa no CRM, e{" "}
						{ev.noAccount.concluded === 0
							? "nenhum concluído está sem empresa"
							: `${num(ev.noAccount.concluded)} concluídos estão sem empresa`}
						.
					</p>
				</More>
			</section>

			<h2 className="how-h2">O que a lista não sabe</h2>
			<section className="card limits">
				<div>
					<h3>A base começa cortada em março de 2017.</h3>
					<p>
						Os {num(ev.truncation.startedBefore)} negócios iniciados antes de{" "}
						{date(ev.truncation.firstClose)} só aparecem se ainda estavam
						abertos nessa data. Para não contar só os que sobreviveram, cada um
						entra na conta a partir da idade que tinha em março.
					</p>
				</div>
				<div>
					<h3>A chance é histórico, não previsão, e superestima a venda.</h3>
					<p>
						Nas datas testadas, a chance média dos negócios em andamento ficou
						acima do que de fato virou venda até o fim do ano. Use a chance para
						pôr os negócios em ordem, não para prever a receita.
					</p>
					<table className="by-date">
						<thead>
							<tr>
								<th scope="col">Data</th>
								<th scope="col" className="r">
									A chance dizia
								</th>
								<th scope="col" className="r">
									Virou venda até 31/12
								</th>
							</tr>
						</thead>
						<tbody>
							{ev.calibration.map((c) => (
								<tr key={c.t}>
									<th scope="row">{date(c.t)}</th>
									<td className="r">{p100(c.predicted)}%</td>
									<td className="r">{p100(c.realized)}%</td>
								</tr>
							))}
						</tbody>
					</table>
					{last && (
						<p className="note">
							Em {date(last.t)}, {p100(last.stillOpen)}% desses negócios ainda
							estavam em andamento em 31/12 e podiam fechar.
						</p>
					)}
				</div>
				<div>
					<h3>
						O fim de trimestre pesa, mas não dá para usar num negócio em
						andamento.
					</h3>
					<p>
						No último mês do trimestre, {p100(ev.quarter.last)} de cada 100
						negócios concluídos foram ganhos; no primeiro mês,{" "}
						{p100(ev.quarter.first)}. Só que o mês em que um negócio vai fechar
						só se sabe depois que ele fecha.
					</p>
				</div>
			</section>

			<p className="note center">
				A regra e a primeira prova usam a data escolhida no topo, {date(day.t)}.
				As outras usam a base inteira, até {date(REFERENCE_DATE)}.
			</p>
		</section>
	);
}
