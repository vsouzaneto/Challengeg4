// Protótipo: textos, componentes e movimento comuns às variações A e B. Dados reais em dados.js.
// Movimento sem biblioteca: Web Animations API (FLIP), só transform e opacity, interrompível.

const P = (() => {
	const q = new URLSearchParams(location.search);
	if (q.get("fonte") === "b") document.documentElement.dataset.font = "b";
	if (q.get("tema")) document.documentElement.dataset.theme = q.get("tema") === "escuro" ? "dark" : "light";

	const D = window.DADOS;
	const REDUCED = matchMedia("(prefers-reduced-motion: reduce)").matches;
	const EASE = "cubic-bezier(0.2, 0.8, 0.2, 1)";
	const int = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 });
	const two = new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
	const num = (n) => int.format(n);
	const usd = (n) => `US$ ${int.format(n)}`;
	const usdShort = (n) => (n >= 1e6 ? `US$ ${two.format(n / 1e6)} mi` : n >= 1e4 ? `US$ ${int.format(n / 1e3)} mil` : usd(n));
	const date = (iso) => iso.split("-").reverse().join("/");
	const dateShort = (iso) => {
		const [, m, d] = iso.split("-");
		return `${d}/${m}`;
	};
	const days = (n) => `${num(n)} ${n === 1 ? "dia" : "dias"}`;
	const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

	const STALE = 138;
	const COOL = 90;
	const situation = (age) => (age > STALE ? "frio" : age >= COOL ? "esfriando" : "quente");
	const LABEL = { quente: "Quente", esfriando: "Esfriando", frio: "Frio" };

	const at = (iso) => D.dates.find((d) => d.iso === iso);
	const latest = D.dates[D.dates.length - 1].iso;

	// "De cada 100": número e frase iguais à chance usada na conta (inteira; nenhuma inversão de ordem).
	const chancePhrase = (deal) =>
		deal.bandFrom === 0
			? `De cada 100 negócios iniciados, ${deal.chance} fecharam venda.`
			: `De cada 100 negócios que chegaram aos ${deal.bandFrom} dias ainda abertos, ${deal.chance} fecharam venda.`;

	const deadlineText = (deal) => {
		const d = deal.deadline;
		if (!d) return "";
		return d.kind === "esfria" ? `esfria em ${days(d.days)}` : `fica frio em ${days(d.days)}`;
	};

	// "O que fazer" por situação: quente, esfriando, perto de ficar frio (≤ 14 dias), frio.
	const todo = (deal) => {
		const s = situation(deal.age);
		if (s === "frio")
			return {
				title: "Atualize ou dê perda",
				text: "Nenhum negócio da base fechou depois de 138 dias aberto. Confirme com o cliente se ainda existe a compra. Se não existir, registre a perda e libere o seu tempo.",
			};
		if (s === "esfriando" && deal.deadline.days <= 14)
			return {
				title: `Peça uma resposta em até ${days(deal.deadline.days)}`,
				text: "Este negócio está perto de ficar frio. Pergunte ao cliente se ele segue adiante ou se o assunto acabou. Uma resposta clara vale mais que mais um follow-up.",
			};
		if (s === "esfriando")
			return {
				title: "Retome o contato esta semana",
				text: `Faz ${days(deal.age)} que o negócio começou. Confirme se ainda há interesse, quem decide e qual é o próximo passo. Ele ${deadlineText(deal)}.`,
			};
		if (deal.deadline.days <= 14)
			return {
				title: `Avance antes de esfriar, em ${days(deal.deadline.days)}`,
				text: "Marque o próximo passo com o cliente agora: demonstração, proposta ou reunião com quem decide.",
			};
		return {
			title: "Marque o próximo passo",
			text: "O negócio está no melhor momento. Combine com o cliente a próxima conversa e registre a data no CRM.",
		};
	};

	const tag = (age) => `<span class="tag ${situation(age)}">${LABEL[situation(age)]}</span>`;

	// Régua do tempo: escala 0–160 dias, marcas em 90 e 138.
	const SCALE = 160;
	const ruler = (deal, { text = true } = {}) => {
		const s = situation(deal.age);
		const k = Math.min(deal.age, SCALE) / SCALE;
		const rest = deal.deadline ? `, ${deadlineText(deal)}` : "";
		return `<div class="ruler" role="img" aria-label="${days(deal.age)}${rest}">
			<div class="ruler-track">
				<span class="ruler-fill ${s}" style="transform: scaleX(${k})"></span>
				<span class="ruler-tick" style="left: ${(COOL / SCALE) * 100}%"></span>
				<span class="ruler-tick" style="left: ${(STALE / SCALE) * 100}%"></span>
			</div>
			${text ? `<span class="ruler-text"><b>${days(deal.age)}</b>${rest}</span>` : ""}
		</div>`;
	};

	const scoreHtml = (deal, cls = "") =>
		`<div class="score ${cls}" aria-label="Score ${deal.score}"><b>${deal.score}</b><span>score</span></div>`;

	const funnelHtml = (slices) => {
		const parts = [
			["quente", slices["no-prazo"]],
			["esfriando", slices.esfriando],
			["frio", slices.parado],
		];
		const total = parts.reduce((s, [, x]) => s + x.listPrice, 0) || 1;
		let x = 0;
		const segs = parts
			.map(([k, v]) => {
				const w = v.listPrice / total;
				const html = `<span class="seg ${k}" data-k="${k}" style="transform: translateX(${x * 100}%) scaleX(${Math.max(w - 0.004, 0)})"></span>`;
				x += w;
				return html;
			})
			.join("");
		const legend = parts
			.map(
				([k, v]) => `<div><span class="k"><i class="seg ${k}"></i>${LABEL[k]}</span><span class="v">${usdShort(v.listPrice)}</span><span class="t-caption">${num(v.deals)} ${v.deals === 1 ? "negócio" : "negócios"}</span></div>`,
			)
			.join("");
		return `<div class="funnel"><div class="funnel-bar" role="img" aria-label="${parts.map(([k, v]) => `${LABEL[k]}: ${usdShort(v.listPrice)}`).join("; ")}">${segs}</div><div class="funnel-legend">${legend}</div></div>`;
	};

	// Barra do funil se transforma: anima transform de cada parte do estado antigo para o novo.
	const morphFunnel = (oldEl, newEl) => {
		if (REDUCED || !oldEl) return;
		const before = Object.fromEntries([...oldEl.querySelectorAll(".seg[data-k]")].map((s) => [s.dataset.k, s.style.transform]));
		for (const s of newEl.querySelectorAll(".seg[data-k]")) {
			const from = before[s.dataset.k];
			if (from) s.animate([{ transform: from }, { transform: s.style.transform }], { duration: 260, easing: EASE });
		}
	};

	// FLIP: mede antes, troca o conteúdo, anima a diferença. Itens novos entram com opacidade.
	const flip = (container, render) => {
		const prev = new Map([...container.querySelectorAll("[data-id]")].map((el) => [el.dataset.id, el.getBoundingClientRect()]));
		render();
		if (REDUCED) return;
		for (const el of container.querySelectorAll("[data-id]")) {
			const a = prev.get(el.dataset.id);
			const b = el.getBoundingClientRect();
			if (a) {
				const dy = a.top - b.top;
				if (Math.abs(dy) > 1)
					el.animate([{ transform: `translateY(${dy}px)` }, { transform: "none" }], { duration: 260, easing: EASE });
			} else {
				el.animate([{ opacity: 0, transform: "translateY(6px)" }, { opacity: 1, transform: "none" }], {
					duration: 220,
					easing: EASE,
				});
			}
		}
	};

	// Barras que crescem uma vez ao abrir a equipe.
	const growOnce = (root) => {
		if (REDUCED) return;
		[...root.querySelectorAll(".grow")].forEach((el, i) => {
			el.animate([{ transform: `${el.style.transform} scaleX(0)` }, { transform: el.style.transform || "none" }], {
				duration: 280,
				delay: Math.min(i * 24, 120),
				easing: EASE,
				fill: "backwards",
			});
		});
	};

	// Folha de detalhe
	const sheet = document.createElement("aside");
	sheet.className = "sheet";
	sheet.setAttribute("aria-label", "Detalhe do negócio");
	const scrim = document.createElement("div");
	scrim.className = "scrim";
	document.addEventListener("DOMContentLoaded", () => document.body.append(scrim, sheet));
	const closeSheet = () => {
		sheet.classList.remove("open");
		scrim.classList.remove("open");
	};
	scrim.addEventListener("click", closeSheet);
	addEventListener("keydown", (e) => e.key === "Escape" && closeSheet());

	const dealDetail = (deal, ctx) => {
		const s = situation(deal.age);
		const t = todo(deal);
		const where = deal.account ? `${esc(deal.account)}` : "Empresa não informada no CRM";
		const rank =
			deal.priceRank && deal.priceRank !== deal.position
				? ` Pela ordem de preço, estaria em ${deal.priceRank}º.`
				: "";
		return `<button class="sheet-close" aria-label="Fechar">×</button>
		<div>
			<h2>${esc(deal.product)}</h2>
			<p class="sub">${where}. ${deal.id}.</p>
		</div>
		<div class="sheet-head">${scoreHtml(deal, "lg")}<p class="t-caption">Mais potencial que ${deal.score}% dos ${num(ctx.scoreBase)} negócios quentes e esfriando da empresa em ${date(ctx.iso)}. ${deal.position}º na sua semana.${rank}</p></div>
		<div>${tag(deal.age)}</div>
		${ruler(deal)}
		<p class="why">${chancePhrase(deal)}</p>
		<dl class="calc">
			<dt>Preço de lista</dt><dd>${usd(deal.price)}</dd>
			<dt>Chance de fechar, pelo histórico</dt><dd>× ${deal.chance}%</dd>
			<dt class="total">Potencial</dt><dd class="total">${usd(deal.potential)}</dd>
		</dl>
		<div class="todo"><h3>${t.title}</h3><p class="muted">${t.text}</p></div>
		<p class="footnote">A chance usa só a idade do negócio. Vendedor, produto e empresa foram testados e não mudam a ordem. <a class="link" href="#como-funciona">Como funciona</a></p>`;
	};

	const coldDetail = (deal) => {
		const t = todo(deal);
		return `<button class="sheet-close" aria-label="Fechar">×</button>
		<div><h2>${esc(deal.product)}</h2><p class="sub">${deal.account ? esc(deal.account) : "Empresa não informada no CRM"}. ${deal.id}.</p></div>
		<div>${tag(deal.age)}</div>
		${ruler(deal)}
		<dl class="calc"><dt>Preço de lista</dt><dd>${usd(deal.price)}</dd><dt>Aberto há</dt><dd>${days(deal.age)}</dd></dl>
		<div class="todo"><h3>${t.title}</h3><p class="muted">${t.text}</p></div>`;
	};

	const openSheet = (html) => {
		sheet.innerHTML = html;
		sheet.querySelector(".sheet-close").addEventListener("click", closeSheet);
		sheet.scrollTop = 0;
		sheet.classList.add("open");
		scrim.classList.add("open");
	};

	const datesHtml = (current) =>
		`<span class="date-label">Dados de</span><div class="dates" role="group" aria-label="Data dos dados">${D.dates
			.map(
				(d) =>
					`<button type="button" data-date="${d.iso}" aria-pressed="${d.iso === current}" ${d.available ? "" : `disabled title="Histórico insuficiente: a margem de erro passa de 5 pontos"`}>${d.iso === latest ? date(d.iso) : dateShort(d.iso)}</button>`,
			)
			.join("")}</div>`;

	const greet = (name) => `Bom dia, ${name.split(" ")[0]}.`;

	const weekNumbers = (seller) => {
		const f = seller.focus;
		return {
			count: f.length,
			listPrice: f.reduce((s, x) => s + x.price, 0),
			potential: f.reduce((s, x) => s + x.potential, 0),
			coolSoon: f.filter((x) => x.deadline?.kind === "esfria" && x.deadline.days <= 14).length,
			coldSoon: f.filter((x) => x.deadline?.kind === "parado" && x.deadline.days <= 14).length,
			cold: seller.review.length,
		};
	};

	return {
		D,
		at,
		latest,
		num,
		usd,
		usdShort,
		date,
		days,
		esc,
		situation,
		LABEL,
		chancePhrase,
		deadlineText,
		todo,
		tag,
		ruler,
		scoreHtml,
		funnelHtml,
		morphFunnel,
		flip,
		growOnce,
		openSheet,
		closeSheet,
		dealDetail,
		coldDetail,
		datesHtml,
		greet,
		weekNumbers,
		REDUCED,
		EASE,
	};
})();
