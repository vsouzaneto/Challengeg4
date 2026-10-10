// Painel do negócio: lateral no computador, folha que sobe no celular. Fecha pelo botão, pela
// tecla Esc, pelo fundo (celular), por clique fora (computador) e arrastando para baixo (celular).

import {
	type ReactNode,
	type PointerEvent as ReactPointerEvent,
	useEffect,
	useRef,
} from "react";
import { createPortal } from "react-dom";
import { Icon } from "./Icon.tsx";

const narrow = () => matchMedia("(max-width: 640px)").matches;
const CLOSE_AT = 120; // px arrastados
const FLICK = 0.6; // px/ms

export function Sheet({
	open,
	onClose,
	label,
	children,
}: {
	open: boolean;
	onClose: () => void;
	label: string;
	children: ReactNode;
}) {
	const ref = useRef<HTMLDivElement>(null);
	const closeRef = useRef<HTMLButtonElement>(null);
	const back = useRef<Element | null>(null);

	useEffect(() => {
		if (!open) return;
		back.current = document.activeElement;
		closeRef.current?.focus({ preventScroll: true });
		const key = (e: KeyboardEvent) => e.key === "Escape" && onClose();
		const outside = (e: PointerEvent) => {
			const t = e.target as Element;
			if (!narrow() && !ref.current?.contains(t) && !t.closest("[data-open]"))
				onClose();
		};
		addEventListener("keydown", key);
		document.addEventListener("pointerdown", outside);
		// Modal no celular: o foco não sai da folha.
		const behind = [
			...document.querySelectorAll<HTMLElement>("main, .nav, .tabbar"),
		];
		const modal = narrow();
		if (modal) for (const el of behind) el.inert = true;
		return () => {
			for (const el of behind) el.inert = false;
			removeEventListener("keydown", key);
			document.removeEventListener("pointerdown", outside);
			(back.current as HTMLElement | null)?.focus?.({ preventScroll: true });
		};
	}, [open, onClose]);

	// Arrastar para baixo, a partir da alça e do cabeçalho (o resto rola o conteúdo).
	const drag = useRef<{ y: number; t: number; dy: number } | null>(null);
	const onDown = (e: ReactPointerEvent) => {
		if (!narrow()) return;
		drag.current = { y: e.clientY, t: performance.now(), dy: 0 };
		(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
	};
	const onMove = (e: ReactPointerEvent) => {
		const d = drag.current;
		const el = ref.current;
		if (!d || !el) return;
		d.dy = Math.max(0, e.clientY - d.y);
		el.style.transition = "none";
		el.style.transform = `translateY(${d.dy}px)`;
	};
	const onUp = () => {
		const d = drag.current;
		const el = ref.current;
		drag.current = null;
		if (!d || !el) return;
		el.style.transition = "";
		el.style.transform = "";
		const speed = d.dy / Math.max(performance.now() - d.t, 1);
		if (d.dy > CLOSE_AT || speed > FLICK) onClose();
	};

	return createPortal(
		<>
			{/* Diálogo não modal no computador (a lista continua usável) e modal no celular. */}
			<div
				ref={ref}
				className={`panel${open ? " open" : ""}`}
				aria-label={label}
				role="dialog"
				aria-modal={open && narrow()}
				inert={!open}
			>
				<div
					className="panel-grip"
					onPointerDown={onDown}
					onPointerMove={onMove}
					onPointerUp={onUp}
					onPointerCancel={onUp}
				>
					<span className="grabber" aria-hidden="true" />
					<button
						ref={closeRef}
						type="button"
						className="close"
						aria-label="Fechar"
						onClick={onClose}
						onPointerDown={(e) => e.stopPropagation()}
					>
						<Icon name="x" />
					</button>
				</div>
				<div className="panel-in">{children}</div>
			</div>
			<div
				className={`scrim${open ? " on" : ""}`}
				onClick={onClose}
				aria-hidden="true"
			/>
		</>,
		document.body,
	);
}
