// O termômetro: cada negócio em andamento é um ponto. Posição = idade (0 a 138 dias, depois os
// frios numa zona comprimida), tamanho = potencial, cor + ícone + rótulo = temperatura.
// Os pontos mudam de lugar por transição de CSS: na troca de data, eles andam (D41).

import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { COOLING_FROM, STALE_AFTER } from "../core/rules.ts";
import { days, usd } from "./format.ts";
import { Icon } from "./Icon.tsx";
import { type DealView, type Temp, tempOf } from "./model.ts";

const COLD_CAP = 440; // dias; a zona fria vai de 139 até aqui
const RMAX = 14;
const LABEL: Record<Temp, string> = {
	quente: "Quente",
	esfriando: "Esfriando",
	frio: "Frio",
};
const ICON = {
	quente: "fire",
	esfriando: "thermometer-simple",
	frio: "snowflake",
} as const;

function useWidth<T extends HTMLElement>() {
	const ref = useRef<T>(null);
	const [w, setW] = useState(0);
	useLayoutEffect(() => {
		const el = ref.current;
		if (!el) return;
		setW(el.clientWidth);
		const ro = new ResizeObserver(() => setW(el.clientWidth));
		ro.observe(el);
		return () => ro.disconnect();
	}, []);
	return [ref, w] as const;
}

interface Placed {
	d: DealView;
	x: number;
	y: number;
	r: number;
}

/** Escala de idade: 0–138 dias em `hot` da largura; os frios depois de um respiro. */
function scaleX(width: number, hot: number, gap: number) {
	const h = width * hot;
	return (age: number) =>
		age <= STALE_AFTER
			? (age / STALE_AFTER) * h
			: h +
				gap +
				Math.min((age - STALE_AFTER - 1) / (COLD_CAP - STALE_AFTER - 1), 1) *
					(width - h - gap - 4);
}

/** Enxame determinístico: os maiores primeiro, cada ponto no lugar livre mais perto do meio. */
function swarm(
	deals: readonly DealView[],
	x: (age: number) => number,
	radius: (d: DealView) => number,
	height: number,
): Placed[] {
	const mid = height / 2;
	const placed: Placed[] = [];
	const order = [...deals].sort(
		(a, b) =>
			radius(b) - radius(a) ||
			(a.age ?? 0) - (b.age ?? 0) ||
			(a.id < b.id ? -1 : 1),
	);
	for (const d of order) {
		const px = x(d.age ?? 0);
		const r = radius(d);
		let best = mid;
		let bestGap = Number.NEGATIVE_INFINITY;
		// Se não couber, fica onde a sobreposição é menor, e não empilha no meio.
		for (let k = 0; k < 400; k++) {
			const py = mid + (k % 2 ? 1 : -1) * Math.ceil(k / 2) * 0.75;
			if (py - r < 0 || py + r > height) continue;
			let g = Number.POSITIVE_INFINITY;
			for (const p of placed)
				g = Math.min(g, Math.hypot(p.x - px, p.y - py) - p.r - r);
			if (g >= 1) {
				best = py;
				break;
			}
			if (g > bestGap) {
				bestGap = g;
				best = py;
			}
		}
		placed.push({ d, x: px, y: best, r });
	}
	return placed;
}

const dotStyle = (p: Placed, intro: boolean) => ({
	width: 2 * RMAX,
	height: 2 * RMAX,
	transform: `translate(${(intro ? 0 : p.x) - RMAX}px, ${p.y - RMAX}px) scale(${p.r / RMAX})`,
});

function summary(deals: readonly DealView[]) {
	const n = { quente: 0, esfriando: 0, frio: 0 };
	for (const d of deals) n[tempOf(d.age ?? 0)]++;
	return `${deals.length} negócios por idade: ${n.quente} quentes, ${n.esfriando} esfriando, ${n.frio} frios.`;
}

/** Versão completa: vendedor, prévia da equipe e régua do painel (`single`). */
export function Thermo({
	deals,
	pmax,
	intro = false,
	single = false,
	onOpen,
}: {
	deals: readonly DealView[];
	pmax: number;
	intro?: boolean;
	single?: boolean;
	onOpen?: (id: string) => void;
}) {
	const [ref, width] = useWidth<HTMLDivElement>();
	const [entering, setEntering] = useState(intro);
	const [tip, setTip] = useState<Placed | null>(null);
	useEffect(() => {
		if (!entering || !width) return;
		const id = requestAnimationFrame(() =>
			requestAnimationFrame(() => setEntering(false)),
		);
		return () => cancelAnimationFrame(id);
	}, [entering, width]);

	const H = single ? 30 : 132;
	const zoneH = 24;
	const axisH = 20;
	const x = scaleX(width, single ? 0.8 : 0.7, 14);
	const radius = (d: DealView) =>
		d.potential > 0
			? Math.max(4, 4 + 10 * Math.sqrt(d.potential / Math.max(pmax, 1)))
			: 4;
	const placed = width ? swarm(deals, x, radius, H) : [];
	const Tag = onOpen ? "button" : "span";

	return (
		<div
			ref={ref}
			className={`thermo${entering ? " entering" : ""}`}
			{...(onOpen
				? { role: "group", "aria-label": summary(deals) }
				: { role: "img", "aria-label": summary(deals) })}
		>
			{width > 0 && (
				<div className="th-plot" style={{ height: H + zoneH + axisH }}>
					<span className="th-zone t-quente" style={{ left: 0 }}>
						<Icon name="fire" />
						{single ? "" : "Quente"}
					</span>
					<span
						className="th-zone t-esfriando"
						style={{ left: x(COOLING_FROM) + 6 }}
					>
						<Icon name="thermometer-simple" />
						{single ? "" : "Esfriando"}
					</span>
					<span
						className="th-zone t-frio"
						style={{ left: x(STALE_AFTER + 1) - 2 }}
					>
						<Icon name="snowflake" />
						{single ? "" : "Frio"}
					</span>
					<div className="th-area" style={{ top: zoneH, height: H }}>
						<span className="th-track" style={{ top: H / 2 - 1 }} />
						<span className="th-mark" style={{ left: x(COOLING_FROM) }} />
						<span className="th-mark" style={{ left: x(STALE_AFTER) }} />
						{placed.map((p) => {
							const top = single || p.d.position <= 5;
							const t = tempOf(p.d.age ?? 0);
							return (
								<Tag
									key={p.d.id}
									className={`dot ${t}${top && p.d.temp !== "frio" ? " top" : ""}`}
									style={dotStyle(p, entering)}
									{...(onOpen
										? {
												type: "button" as const,
												"data-open": p.d.id,
												"aria-label": `${p.d.product}, ${days(p.d.age ?? 0)}`,
												onClick: () => onOpen(p.d.id),
												onPointerEnter: () => setTip(p),
												onPointerLeave: () => setTip(null),
												onFocus: () => setTip(p),
												onBlur: () => setTip(null),
											}
										: {})}
								/>
							);
						})}
						{!single &&
							placed
								.filter((p) => p.d.temp !== "frio" && p.d.position <= 5)
								.map((p) => (
									<span
										key={`n-${p.d.id}`}
										className="dot-label"
										style={{
											transform: `translate(${(entering ? 0 : p.x) - 3.5}px, ${p.y - p.r - 17}px)`,
										}}
									>
										{p.d.position}
									</span>
								))}
					</div>
					<span className="th-axis" style={{ left: 0 }}>
						0
					</span>
					<span className="th-axis" style={{ left: x(COOLING_FROM) - 10 }}>
						90 dias
					</span>
					<span
						className="th-axis"
						style={{ left: x(STALE_AFTER) - (single ? 10 : 24) }}
					>
						138
					</span>
					{tip && (
						<span
							className="tip"
							style={{
								left: Math.min(Math.max(tip.x - 110, 0), width - 220),
								top: zoneH + tip.y - tip.r - 8,
							}}
						>
							<b>{tip.d.product}</b>
							{tip.d.account && <span>{tip.d.account}</span>}
							<span>
								{LABEL[tempOf(tip.d.age ?? 0)]}, {days(tip.d.age ?? 0)}
							</span>
							<span>
								{tip.d.potential
									? `Potencial ${usd(tip.d.potential)}`
									: `Preço de lista ${usd(tip.d.price)}`}
							</span>
						</span>
					)}
				</div>
			)}
		</div>
	);
}

/**
 * Versão mínima da equipe (D44: os pontos da rodada 3 ficaram carregados): um traço por negócio
 * quente ou esfriando, na idade dele, e os frios como uma barra cinza cujo comprimento compara
 * os vendedores da equipe.
 */
export function MiniThermo({
	deals,
	coldMax,
}: {
	deals: readonly DealView[];
	coldMax: number;
}) {
	const [ref, width] = useWidth<HTMLSpanElement>();
	const hot = deals.filter((d) => d.temp !== "frio");
	const cold = deals.length - hot.length;
	const H = 12;
	const x = scaleX(width, 0.66, 8);
	const coldStart = x(STALE_AFTER + 1);
	return (
		<span ref={ref} className="thermo mini" aria-hidden="true">
			{width > 0 && (
				<span className="th-area" style={{ top: 0, height: H }}>
					<span className="th-track" style={{ top: H / 2 - 1 }} />
					<span className="th-mark" style={{ left: x(COOLING_FROM) }} />
					<span className="th-mark" style={{ left: x(STALE_AFTER) }} />
					{hot.map((d) => (
						<span
							key={d.id}
							className={`tick ${tempOf(d.age ?? 0)}`}
							style={{ transform: `translateX(${x(d.age ?? 0) - 1}px)` }}
						/>
					))}
					{cold > 0 && (
						<span
							className="cold-bar"
							style={{
								left: coldStart,
								top: H / 2 - 3,
								width: width - coldStart,
								// transform, não largura: a barra anima na troca de data
								transform: `scaleX(${Math.max(cold / Math.max(coldMax, 1), 6 / (width - coldStart))})`,
							}}
						/>
					)}
				</span>
			)}
		</span>
	);
}

export { ICON as TEMP_ICON, LABEL as TEMP_LABEL };
