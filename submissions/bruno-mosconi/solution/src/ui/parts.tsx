// Peças comuns às telas: temperatura, prazo, empresa, score e o que fazer.

import { STALE_AFTER } from "../core/rules.ts";
import { days } from "./format.ts";
import { Icon } from "./Icon.tsx";
import { type DealView, LOW_SCORE, type Temp } from "./model.ts";
import { TEMP_ICON, TEMP_LABEL } from "./Thermo.tsx";

export const cap = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

export const deadlineText = (d: DealView) =>
	d.deadline
		? d.deadline.kind === "esfria"
			? `esfria em ${days(d.deadline.days)}`
			: `fica frio em ${days(d.deadline.days)}`
		: "";

/** O que fazer, por situação: quente, quente perto de esfriar, esfriando, perto de ficar frio, frio. */
export function todo(d: DealView): { title: string; text: string } {
	if (d.temp === null)
		return {
			title: "Faça o primeiro contato",
			text: "É uma prospecção sem contato registrado. Ligue, registre a data de início no CRM e ela entra na semana.",
		};
	if (d.temp === "frio")
		return {
			title: "Atualize ou dê perda",
			text: `Nenhum negócio da base fechou depois de ${STALE_AFTER} dias aberto. Confirme com o cliente se a compra ainda existe. Se não existir, registre a perda e libere o tempo para os negócios quentes.`,
		};
	// D56: com score baixo (o mesmo corte da D46), o potencial não justifica urgência.
	if ((d.score ?? 100) < LOW_SCORE)
		return {
			title: "Resolva com uma mensagem rápida",
			text: "O potencial dele é baixo perto dos negócios de todos os vendedores: não gaste a semana aqui. Pergunte ao cliente se segue adiante; se não, dê perda.",
		};
	const left = d.deadline?.days ?? 0;
	if (d.temp === "esfriando" && left <= 14)
		return {
			title: `Peça uma resposta em até ${days(left)}`,
			text: "Este negócio está perto de ficar frio. Pergunte ao cliente se ele segue adiante ou se o assunto acabou. Uma resposta clara vale mais que mais um follow-up.",
		};
	if (d.temp === "esfriando")
		return {
			title: "Retome o contato esta semana",
			text: `Faz ${days(d.age ?? 0)} que o negócio começou. Confirme se ainda há interesse, quem decide e qual é o próximo passo. Ele ${deadlineText(d)}.`,
		};
	if (left <= 14)
		return {
			title: `Avance antes de esfriar, em ${days(left)}`,
			text: "Marque o próximo passo com o cliente agora: demonstração, proposta ou reunião com quem decide.",
		};
	return {
		title: "Marque o próximo passo",
		text: "O negócio está no melhor momento. Combine com o cliente a próxima conversa e registre a data no CRM.",
	};
}

export function TempTag({ temp, label }: { temp: Temp; label?: string }) {
	return (
		<span className={`temp t-${temp}`}>
			<Icon name={TEMP_ICON[temp]} />
			{label ?? TEMP_LABEL[temp]}
		</span>
	);
}

export function Meta({ d }: { d: DealView }) {
	if (!d.temp) return null;
	return (
		<div className="meta">
			<TempTag temp={d.temp} />
			{d.deadline && <span className="due">{cap(deadlineText(d))}</span>}
		</div>
	);
}

/** Empresa: o nome, "Sem empresa no CRM" em cinza na data padrão, ou nada nas datas passadas (D34). */
export function Account({ d, className }: { d: DealView; className: string }) {
	if (d.account === undefined) return null;
	return (
		<span className={`${className}${d.account ? "" : " none"}`}>
			{d.account ?? "Sem empresa no CRM"}
		</span>
	);
}

const RING = { lg: [34, 5], md: [22, 4], sm: [15, 3] } as const;

/** Score num anel monocromático: a parte cheia do anel é o próprio score (D39). */
export function Ring({
	score,
	size,
}: {
	score: number;
	size: keyof typeof RING;
}) {
	const [r, w] = RING[size];
	const box = 2 * (r + w);
	const c = 2 * Math.PI * r;
	return (
		<div
			className={`ring ring-${size}`}
			role="img"
			aria-label={`Score ${score} de 100`}
		>
			<svg viewBox={`0 0 ${box} ${box}`} width={box} height={box}>
				<title>Score {score}</title>
				<circle
					className="track"
					cx={box / 2}
					cy={box / 2}
					r={r}
					strokeWidth={w}
				/>
				<circle
					className="val"
					cx={box / 2}
					cy={box / 2}
					r={r}
					strokeWidth={w}
					strokeDasharray={c.toFixed(2)}
					strokeDashoffset={(c * (1 - score / 100)).toFixed(2)}
					transform={`rotate(-90 ${box / 2} ${box / 2})`}
				/>
			</svg>
			<b aria-hidden="true">{score}</b>
		</div>
	);
}
