// Score de 0 a 100 (D39). Não muda a ordem: é o potencial (valor ponderado) dito como posição.

import { type ScoredDeal, STALE_AFTER } from "./rules.ts";

/**
 * Para cada negócio quente ou esfriando (até 138 dias), a % dos negócios quentes e esfriando
 * da mesma base com potencial menor, arredondada para baixo: score 92 = mais potencial que
 * 92% deles. Empates têm o mesmo score. Frios ficam fora e não têm score.
 * `scored` deve ser a empresa inteira na data (scoreOpen sem filtro de vendedor).
 */
export function potentialScores(
	scored: readonly ScoredDeal[],
): Map<string, number> {
	const live = scored.filter((s) => s.age <= STALE_AFTER);
	const sorted = live.map((s) => s.weighted).sort((a, b) => a - b);
	const below = (w: number) => {
		let lo = 0;
		let hi = sorted.length;
		while (lo < hi) {
			const mid = (lo + hi) >> 1;
			if ((sorted[mid] as number) < w) lo = mid + 1;
			else hi = mid;
		}
		return lo;
	};
	return new Map(
		live.map((s) => [
			s.deal.id,
			Math.floor((100 * below(s.weighted)) / live.length),
		]),
	);
}
