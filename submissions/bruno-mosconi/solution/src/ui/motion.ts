// Movimento só com transform e opacity, interrompível, e nada quando o sistema pede menos movimento.

export const EASE = "cubic-bezier(0.25, 0.1, 0.3, 1)";
export const MOVE_MS = 280;

export const reducedMotion = () =>
	typeof matchMedia === "function" &&
	matchMedia("(prefers-reduced-motion: reduce)").matches;

// FLIP da troca de data: mede antes de trocar, anima a diferença depois.
let before = new Map<string, DOMRect>();

export function snapshot() {
	before = new Map(
		[...document.querySelectorAll<HTMLElement>("[data-flip]")].map((el) => [
			el.dataset.flip as string,
			el.getBoundingClientRect(),
		]),
	);
}

export function playFlip() {
	const old = before;
	before = new Map();
	if (!old.size || reducedMotion()) return;
	for (const el of document.querySelectorAll<HTMLElement>("[data-flip]")) {
		const a = old.get(el.dataset.flip as string);
		if (!a) {
			el.animate([{ opacity: 0 }, { opacity: 1 }], {
				duration: 220,
				easing: EASE,
			});
			continue;
		}
		const b = el.getBoundingClientRect();
		const dx = a.left - b.left;
		const dy = a.top - b.top;
		if (Math.abs(dx) > 1 || Math.abs(dy) > 1)
			el.animate(
				[{ transform: `translate(${dx}px, ${dy}px)` }, { transform: "none" }],
				{ duration: MOVE_MS, easing: EASE },
			);
	}
}

// Primeira abertura: uma vez por sessão.
const KEY = "onde-focar:aberto";
export function takeFirstOpen(): boolean {
	if (reducedMotion()) return false;
	try {
		if (sessionStorage.getItem(KEY)) return false;
		sessionStorage.setItem(KEY, "1");
		return true;
	} catch {
		return false;
	}
}
