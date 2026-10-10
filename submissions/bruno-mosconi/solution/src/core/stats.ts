// Estatística sem dependência. Cada função é testada contra o scipy nos mesmos dados (D23).

/** Gerador pseudoaleatório com semente (mulberry32): mesmo resultado em toda execução. */
export function rng(seed: number): () => number {
	let a = seed >>> 0;
	return () => {
		a = (a + 0x6d2b79f5) >>> 0;
		let t = a;
		t = Math.imul(t ^ (t >>> 15), t | 1);
		t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
		return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
	};
}

const LANCZOS = [
	0.99999999999980993, 676.5203681218851, -1259.1392167224028,
	771.32342877765313, -176.61502916214059, 12.507343278686905,
	-0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7,
];

export function lnGamma(z: number): number {
	if (z < 0.5)
		return Math.log(Math.PI / Math.sin(Math.PI * z)) - lnGamma(1 - z);
	const zz = z - 1;
	let x = LANCZOS[0] as number;
	for (let i = 1; i < LANCZOS.length; i++)
		x += (LANCZOS[i] as number) / (zz + i);
	const t = zz + 7.5;
	return (
		0.5 * Math.log(2 * Math.PI) + (zz + 0.5) * Math.log(t) - t + Math.log(x)
	);
}

/** Gama incompleta regularizada superior Q(a, x): série para x < a+1, fração contínua (Lentz) acima. */
export function gammaQ(a: number, x: number): number {
	if (x <= 0) return 1;
	const front = Math.exp(-x + a * Math.log(x) - lnGamma(a));
	if (x < a + 1) {
		let ap = a;
		let del = 1 / a;
		let sum = del;
		for (let n = 0; n < 10_000; n++) {
			ap += 1;
			del *= x / ap;
			sum += del;
			if (Math.abs(del) < Math.abs(sum) * 1e-16) break;
		}
		return 1 - sum * front;
	}
	const tiny = 1e-300;
	let b = x + 1 - a;
	let c = 1 / tiny;
	let d = 1 / b;
	let h = d;
	for (let i = 1; i < 10_000; i++) {
		const an = -i * (i - a);
		b += 2;
		d = an * d + b;
		if (Math.abs(d) < tiny) d = tiny;
		c = b + an / c;
		if (Math.abs(c) < tiny) c = tiny;
		d = 1 / d;
		const del = d * c;
		h *= del;
		if (Math.abs(del - 1) < 1e-16) break;
	}
	return front * h;
}

export const chi2Sf = (x: number, df: number): number => gammaQ(df / 2, x / 2);

export interface ChiSquareResult {
	statistic: number;
	df: number;
	p: number;
}

/** Qui-quadrado de independência (sem correção de Yates). Linhas e colunas vazias são descartadas. */
export function chiSquare(
	table: readonly (readonly number[])[],
): ChiSquareResult {
	const rowsKept = table.filter((r) => r.some((v) => v > 0));
	const nCols = rowsKept[0]?.length ?? 0;
	const colTotals = Array.from({ length: nCols }, (_, j) =>
		rowsKept.reduce((s, r) => s + (r[j] ?? 0), 0),
	);
	const cols = colTotals.flatMap((t, j) => (t > 0 ? [j] : []));
	const total = colTotals.reduce((s, v) => s + v, 0);
	let statistic = 0;
	for (const r of rowsKept) {
		const rowTotal = r.reduce((s, v) => s + v, 0);
		for (const j of cols) {
			const expected = (rowTotal * (colTotals[j] as number)) / total;
			statistic += ((r[j] as number) - expected) ** 2 / expected;
		}
	}
	const df = (rowsKept.length - 1) * (cols.length - 1);
	return { statistic, df, p: chi2Sf(statistic, df) };
}

const Z95 = 1.959963984540054;

export function wilson(k: number, n: number, z = Z95): [number, number] {
	const p = k / n;
	const den = 1 + z ** 2 / n;
	const center = (p + z ** 2 / (2 * n)) / den;
	const half = (z / den) * Math.sqrt((p * (1 - p)) / n + z ** 2 / (4 * n ** 2));
	return [center - half, center + half];
}

export function normalCi(k: number, n: number, z = Z95): [number, number] {
	const p = k / n;
	const half = z * Math.sqrt((p * (1 - p)) / n);
	return [p - half, p + half];
}

function ranks(xs: readonly number[]): number[] {
	const order = xs.map((v, i) => [v, i] as const).sort((a, b) => a[0] - b[0]);
	const r = new Array<number>(xs.length);
	for (let i = 0; i < order.length; ) {
		let j = i;
		while (j + 1 < order.length && order[j + 1]?.[0] === order[i]?.[0]) j++;
		for (let k = i; k <= j; k++) r[order[k]?.[1] as number] = (i + j) / 2 + 1;
		i = j + 1;
	}
	return r;
}

function pearson(x: readonly number[], y: readonly number[]): number {
	const n = x.length;
	const mx = x.reduce((s, v) => s + v, 0) / n;
	const my = y.reduce((s, v) => s + v, 0) / n;
	let sxy = 0;
	let sxx = 0;
	let syy = 0;
	for (let i = 0; i < n; i++) {
		const dx = (x[i] as number) - mx;
		const dy = (y[i] as number) - my;
		sxy += dx * dy;
		sxx += dx * dx;
		syy += dy * dy;
	}
	return sxy / Math.sqrt(sxx * syy);
}

export const spearman = (x: readonly number[], y: readonly number[]): number =>
	pearson(ranks(x), ranks(y));

/** Quantil com interpolação linear (o padrão do numpy). */
export function quantile(sorted: readonly number[], q: number): number {
	const pos = q * (sorted.length - 1);
	const lo = Math.floor(pos);
	const hi = Math.ceil(pos);
	return (
		(sorted[lo] as number) +
		((sorted[hi] as number) - (sorted[lo] as number)) * (pos - lo)
	);
}

export interface RangeTest {
	observed: number; // maior − menor taxa entre os grupos
	shareAtLeast: number; // fração dos sorteios com diferença ≥ observada
}

/**
 * Embaralha o desfecho (y) entre as observações, mantendo grupo e peso de cada uma, e compara
 * a diferença entre a maior e a menor taxa ponderada por grupo. Com peso 1, é a taxa de ganho.
 */
export function permutationRange(
	group: readonly number[],
	y: readonly number[],
	opts: {
		weights?: readonly number[];
		iterations?: number;
		seed?: number;
	} = {},
): RangeTest {
	const w = opts.weights ?? y.map(() => 1);
	const nGroups = Math.max(...group) + 1;
	const range = (ys: readonly number[]) => {
		const num = new Float64Array(nGroups);
		const den = new Float64Array(nGroups);
		for (let i = 0; i < ys.length; i++) {
			const g = group[i] as number;
			num[g] = (num[g] as number) + (w[i] as number) * (ys[i] as number);
			den[g] = (den[g] as number) + (w[i] as number);
		}
		let max = -Infinity;
		let min = Infinity;
		for (let g = 0; g < nGroups; g++) {
			if ((den[g] as number) <= 0) continue;
			const r = (num[g] as number) / (den[g] as number);
			max = Math.max(max, r);
			min = Math.min(min, r);
		}
		return max - min;
	};
	const observed = range(y);
	const iterations = opts.iterations ?? 10_000;
	const rand = rng(opts.seed ?? 20171231);
	const ys = [...y];
	let hits = 0;
	for (let it = 0; it < iterations; it++) {
		for (let i = ys.length - 1; i > 0; i--) {
			const j = Math.floor(rand() * (i + 1));
			[ys[i], ys[j]] = [ys[j] as number, ys[i] as number];
		}
		if (range(ys) >= observed - 1e-12) hits++;
	}
	return { observed, shareAtLeast: hits / iterations };
}

export interface PairedUnit {
	a: number; // receita capturada pelo método A
	b: number; // pelo método B
	den: number; // receita disponível
}

export interface PairedTest {
	difference: number; // (Σa − Σb) / Σden
	ci95: [number, number]; // bootstrap por unidade, percentil
	pSignFlip: number; // bilateral
}

/** Teste pareado com unidade = vendedor (as 4 fotos de um vendedor ficam juntas). */
export function pairedTest(
	units: readonly PairedUnit[],
	opts: { iterations?: number; seed?: number } = {},
): PairedTest {
	const iterations = opts.iterations ?? 10_000;
	const diff = (us: readonly PairedUnit[]) =>
		us.reduce((s, u) => s + u.a - u.b, 0) / us.reduce((s, u) => s + u.den, 0);
	const difference = diff(units);

	const randB = rng((opts.seed ?? 20171231) + 1);
	const boots: number[] = [];
	for (let it = 0; it < iterations; it++) {
		const sample = units.map(
			() => units[Math.floor(randB() * units.length)] as PairedUnit,
		);
		boots.push(diff(sample));
	}
	boots.sort((x, y) => x - y);

	const randS = rng((opts.seed ?? 20171231) + 2);
	const den = units.reduce((s, u) => s + u.den, 0);
	let hits = 0;
	for (let it = 0; it < iterations; it++) {
		let s = 0;
		for (const u of units) s += (randS() < 0.5 ? -1 : 1) * (u.a - u.b);
		if (Math.abs(s / den) >= Math.abs(difference) - 1e-12) hits++;
	}
	return {
		difference,
		ci95: [quantile(boots, 0.025), quantile(boots, 0.975)],
		pSignFlip: hits / iterations,
	};
}
