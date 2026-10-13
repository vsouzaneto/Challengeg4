/* Decisor de Campanha - interface. Le o ENGINE e desenha na tela.
   OS-10: todo texto de tela em linguagem simples, sem jargao. */
(function () {
  "use strict";

  var ENG = ENGINE;
  var MIN_ESTRATO = 30;   // mesmo piso do motor; ele nao exporta a constante

  var estado = {
    base: null, nomeDados: "", resultado: null,
    periodo: "tudo", de: null, ate: null,
    plataformas: [], margem: 0.10,
    expandido: {}, abertos: {},
    ideia: null, plano: null, tema: "automatico"
  };

  // ---------------------------------------------------------------- textos

  var NOMES = {
    image: "Imagem", mixed: "Misto", text: "Texto", video: "Vídeo",
    beauty: "Beleza", lifestyle: "Estilo de vida", tech: "Tecnologia",
    female: "Mulheres", male: "Homens", "non-binary": "Não binários", unknown: "Não informado",
    Brazil: "Brasil", China: "China", Germany: "Alemanha", India: "Índia",
    Japan: "Japão", Russia: "Rússia", UK: "Reino Unido", USA: "Estados Unidos"
  };

  var PAIS_EM = {
    Brazil: "no Brasil", China: "na China", Germany: "na Alemanha", India: "na Índia",
    Japan: "no Japão", Russia: "na Rússia", UK: "no Reino Unido", USA: "nos Estados Unidos"
  };

  var FAIXA_FRASE = {
    "até 50K": "de até 50 mil seguidores",
    "50–100K": "de 50 mil a 100 mil seguidores",
    "100–500K": "de 100 mil a 500 mil seguidores",
    "500K–1M": "de 500 mil a 1 milhão de seguidores",
    "acima de 1M": "com mais de 1 milhão de seguidores"
  };

  var FAIXA_OPCAO = {
    "até 50K": "Até 50 mil seguidores",
    "50–100K": "De 50 mil a 100 mil seguidores",
    "100–500K": "De 100 mil a 500 mil seguidores",
    "500K–1M": "De 500 mil a 1 milhão de seguidores",
    "acima de 1M": "Mais de 1 milhão de seguidores"
  };

  var ROTULO_VEREDITO = {
    funciona: "Funcionou melhor", nao_funciona: "Funcionou pior",
    sem_efeito: "Não faz diferença", inconclusivo: "Ainda não dá para saber"
  };

  var ROTULO_PAT = {
    funciona: "Vale a pena", nao_funciona: "Não vale a pena",
    sem_efeito: "Não vale a pena", inconclusivo: "Ainda não dá para saber"
  };

  /* Ordem de leitura: quem tem rank menor manda na frase. */
  var RANK = {
    formato: 1, categoria: 2, faixa: 3, plataforma: 4,
    genero: 1, idade: 2, pais: 3
  };

  var AJUDAS = {
    organico: "Post que você publica sem pagar ninguém para divulgar.",
    patrocinado: "Post em que você paga um influenciador para publicar.",
    interacoes: "Tudo que as pessoas fazem no post: curtir, comentar e compartilhar.",
    alcance: "Quantas vezes o post foi visto."
  };

  // ---------------------------------------------------------------- numeros

  function num(v, dec) {
    var s = v.toLocaleString("pt-BR", {
      minimumFractionDigits: dec || 0, maximumFractionDigits: dec || 0
    });
    return s.replace("-", "−");
  }

  /* Numero redondo de gente: 2.010 / 404 mil / 1,2 milhão. */
  function aprox(v) {
    if (!isFinite(v)) return "—";
    var a = Math.abs(v);
    if (a < 10000) return num(Math.round(v));
    if (a < 1e6) return num(Math.round(v / 1000)) + " mil";
    var mi = v / 1e6;
    return num(mi, 1) + (Math.abs(mi) >= 2 ? " milhões" : " milhão");
  }

  /* Diferenca em % inteira, sempre positiva: quem usa escolhe "mais" ou "menos". */
  function pctInt(dif) {
    return num(Math.round(Math.abs(dif) * 100));
  }

  function moeda(v) {
    return "R$ " + num(v, v !== 0 && Math.abs(v) < 100 ? 2 : 0);
  }

  function posts(n) {
    return num(n) + (n === 1 ? " post" : " posts");
  }

  function analisamos(n) {
    return "analisamos " + posts(n);
  }

  function dataISO(ms) {
    var d = new Date(ms);
    return d.getUTCFullYear() + "-" + ("0" + (d.getUTCMonth() + 1)).slice(-2) +
      "-" + ("0" + d.getUTCDate()).slice(-2);
  }

  function dataBR(ms) {
    var p = dataISO(ms).split("-");
    return p[2] + "/" + p[1] + "/" + p[0];
  }

  // ---------------------------------------------------------------- nomes

  function idadeFrase(v) {
    var s = String(v);
    if (!/\d/.test(s)) return "de idade não informada";
    return "de " + s.replace(/\s*[–-]\s*/g, " a ") + " anos";
  }

  function idadeOpcao(v) {
    var s = String(v);
    if (!/\d/.test(s)) return NOMES[s] || s;
    return s.replace(/\s*[–-]\s*/g, " a ") + " anos";
  }

  /* Rotulo curto, para as opcoes dos campos da aba Planejar. */
  function rotuloOpcao(varId, v) {
    if (varId === "faixa") return FAIXA_OPCAO[v] || v;
    if (varId === "idade") return idadeOpcao(v);
    return NOMES[v] || v;
  }

  /* Forma principal: abre a frase. */
  function formaPrincipal(varId, v) {
    if (varId === "plataforma") return "Posts no " + v;
    if (varId === "formato") return NOMES[v] || v;
    if (varId === "categoria") return "Posts sobre " + (NOMES[v] || v).toLowerCase();
    if (varId === "faixa") return "Influenciadores " + (FAIXA_FRASE[v] || v);
    if (varId === "idade") return "Pessoas " + idadeFrase(v);
    if (varId === "genero") return NOMES[v] || v;
    if (varId === "pais") return "Público " + (PAIS_EM[v] || ("de " + (NOMES[v] || v)));
    return NOMES[v] || v;
  }

  /* Forma complemento: entra depois da principal. */
  function formaComplemento(varId, v) {
    if (varId === "plataforma") return "no " + v;
    if (varId === "formato") return "em " + (NOMES[v] || v).toLowerCase();
    if (varId === "categoria") return "sobre " + (NOMES[v] || v).toLowerCase();
    if (varId === "faixa") return "com influenciadores " + (FAIXA_FRASE[v] || v);
    if (varId === "idade") return idadeFrase(v);
    if (varId === "genero") return "para " + (NOMES[v] || v).toLowerCase();
    if (varId === "pais") return PAIS_EM[v] || ("de " + (NOMES[v] || v));
    return NOMES[v] || v;
  }

  /* "Vídeo no TikTok", "Imagem com influenciadores de até 50 mil seguidores". */
  function nomeEscolha(seg) {
    if (seg.vars.length === 1) return formaPrincipal(seg.vars[0], seg.valores[0]);
    var ord = seg.vars.map(function (v, i) {
      return { v: v, val: seg.valores[i], r: RANK[v] || 9 };
    }).sort(function (a, b) { return a.r - b.r; });
    return formaPrincipal(ord[0].v, ord[0].val) + " " + formaComplemento(ord[1].v, ord[1].val);
  }

  // ---------------------------------------------------------------- DOM

  function el(tag, attrs, filhos) {
    var n = document.createElement(tag), k;
    if (attrs) for (k in attrs) {
      if (k === "class") n.className = attrs[k];
      else if (k === "text") n.textContent = attrs[k];
      else if (attrs[k] === true) n.setAttribute(k, "");
      else if (attrs[k] != null && attrs[k] !== false) n.setAttribute(k, attrs[k]);
    }
    (filhos || []).forEach(function (f) { if (f) n.appendChild(f); });
    return n;
  }

  function txt(s) {
    return document.createTextNode(s);
  }

  function selo(tipo, rotulo, grande) {
    return el("span", {
      class: "selo selo-" + tipo + (grande ? " selo-grande" : ""),
      text: rotulo || ROTULO_VEREDITO[tipo]
    });
  }

  function tipoSeloPat(tipo) {
    if (tipo === "funciona") return "funciona";
    if (tipo === "inconclusivo") return "inconclusivo";
    return "nao_funciona";
  }

  function patrocinioSemGanho(r) {
    if (!r || !r.patrocinio) return false;
    var t = r.patrocinio.metricas.taxa.tipo;
    return t === "nao_funciona" || t === "sem_efeito";
  }

  // ---------------------------------------------------------------- ajuda "?"

  function fecharBaloes() {
    [].slice.call(document.querySelectorAll(".balao")).forEach(function (b) {
      b.hidden = true;
    });
    [].slice.call(document.querySelectorAll("button.ajuda")).forEach(function (b) {
      b.setAttribute("aria-expanded", "false");
    });
  }

  /* Palavra + botao "?" + balao de uma frase. Abre no clique e no Enter. */
  function termo(texto, chave) {
    var balao = el("span", { class: "balao", role: "note", text: AJUDAS[chave] });
    balao.hidden = true;
    var b = el("button", {
      class: "ajuda", type: "button", "aria-expanded": "false",
      "aria-label": "O que quer dizer " + texto, text: "?"
    });
    b.addEventListener("click", function (ev) {
      ev.stopPropagation();
      var estavaAberto = !balao.hidden;
      fecharBaloes();
      if (estavaAberto) return;
      balao.hidden = false;
      b.setAttribute("aria-expanded", "true");
    });
    return el("span", { class: "termo" }, [txt(texto), b, balao]);
  }

  // ---------------------------------------------------------------- barras

  /* Barras horizontais na mesma escala, comecando em zero. Cores so por CSS. */
  function barras(itens) {
    var max = 0;
    itens.forEach(function (it) {
      if (isFinite(it.valor) && it.valor > max) max = it.valor;
    });
    var g = el("div", { class: "barras" });
    itens.forEach(function (it) {
      var rot = el("span", { class: "barra-rotulo" });
      if (it.rotulo && it.rotulo.nodeType) rot.appendChild(it.rotulo);
      else rot.textContent = it.rotulo;
      var cheia = el("span", { class: "barra-cheia", "data-cor": it.cor || "neutro" });
      cheia.style.width = (max > 0 && isFinite(it.valor)
        ? Math.max(0, it.valor) / max * 100 : 0) + "%";
      g.appendChild(rot);
      g.appendChild(el("div", { class: "barra-trilha" }, [cheia]));
      g.appendChild(el("span", { class: "barra-valor", text: it.texto }));
    });
    return g;
  }

  function tabela(colunas, linhas, classe) {
    var t = el("table", { class: "tabela" + (classe ? " " + classe : "") });
    var tr = el("tr", {});
    colunas.forEach(function (c) {
      tr.appendChild(el("th", { class: c.num ? "num" : "", text: c.rotulo }));
    });
    t.appendChild(el("thead", {}, [tr]));
    var tb = el("tbody", {});
    linhas.forEach(function (l) {
      var f = el("tr", {});
      colunas.forEach(function (c) {
        var v = c.valor(l);
        var td = el("td", { class: c.num ? "num" : "" });
        if (v && v.nodeType) td.appendChild(v); else td.textContent = v;
        f.appendChild(td);
      });
      tb.appendChild(f);
    });
    t.appendChild(tb);
    return t;
  }

  /* Recolhivel que lembra se estava aberto entre redesenhos. */
  function recolhivel(id, titulo, extras, abrePadrao) {
    var d = el("details", { class: "secao", id: id });
    var aberto = estado.abertos[id];
    if (aberto === undefined) aberto = !!abrePadrao;
    if (aberto) d.setAttribute("open", "");
    d.appendChild(el("summary", {}, [el("span", { text: titulo })].concat(extras || [])));
    d.addEventListener("toggle", function () { estado.abertos[id] = d.open; });
    return d;
  }

  // ---------------------------------------------------------------- listas

  /* Agrupa as escolhas de um ou mais blocos pelo tipo de resposta. */
  function porTipo(blocos, metrica) {
    var r = { funciona: [], nao_funciona: [], sem_efeito: [], inconclusivo: [] };
    [].concat(blocos).forEach(function (bloco) {
      if (!bloco) return;
      bloco.segmentos.forEach(function (s) {
        var v = s.metricas[metrica];
        if (v) r[v.tipo].push({ seg: s, v: v });
      });
    });
    Object.keys(r).forEach(function (t) {
      r[t].sort(function (a, b) { return Math.abs(b.v.lift - 1) - Math.abs(a.v.lift - 1); });
    });
    return r;
  }

  function ordenarPorDiferenca(entradas, crescente) {
    return entradas.slice().sort(function (a, b) {
      return crescente ? a.v.lift - b.v.lift : b.v.lift - a.v.lift;
    });
  }

  /* Ate 3 nomes, sem porcentagem: "Imagem, Texto, Misto". */
  function listaCurta(entradas, crescente) {
    return ordenarPorDiferenca(entradas, crescente).slice(0, 3).map(function (e) {
      return nomeEscolha(e.seg);
    }).join(", ");
  }

  function frasesPrioridade(grupos) {
    var out = [];
    if (grupos.funciona.length) out.push("Priorize: " + listaCurta(grupos.funciona, false) + ".");
    if (grupos.nao_funciona.length) out.push("Evite: " + listaCurta(grupos.nao_funciona, true) + ".");
    return out;
  }

  /* Uma linha de resposta: selo, frase e quantos posts entraram. */
  function linhaEscolha(entrada, mostrarSelo) {
    var v = entrada.v, nome = nomeEscolha(entrada.seg), frase;
    if (v.tipo === "funciona") {
      frase = nome + ": rendeu " + pctInt(v.lift - 1) + "% mais interações que o resto.";
    } else if (v.tipo === "nao_funciona") {
      frase = nome + ": rendeu " + pctInt(v.lift - 1) + "% menos interações que o resto.";
    } else if (v.tipo === "sem_efeito") {
      frase = nome + ": praticamente igual ao resto.";
    } else {
      var faltam = v.faltam == null ? Math.max(0, 100 - v.n) : v.faltam;
      frase = nome + ": faltam cerca de " + num(faltam) + " posts para saber.";
    }
    return el("div", { class: "item" }, [
      mostrarSelo ? selo(v.tipo) : null,
      el("span", { class: "nome", text: frase }),
      el("span", { class: "base", text: analisamos(v.n) })
    ]);
  }

  /* Lista com no maximo 10 linhas e botao "Mostrar todos (N)". */
  function listaLimitada(chave, entradas, mostrarSelo, textoVazio) {
    var caixa = el("div", {});
    if (!entradas.length) {
      caixa.appendChild(el("p", { class: "vazio", text: textoVazio }));
      return caixa;
    }
    var todos = !!estado.expandido[chave];
    var lista = el("div", { class: "linhas" });
    (todos ? entradas : entradas.slice(0, 10)).forEach(function (e) {
      lista.appendChild(linhaEscolha(e, mostrarSelo));
    });
    caixa.appendChild(lista);
    if (entradas.length > 10) {
      var b = el("button", {
        class: "botao mais nao-imprimir",
        text: todos ? "Mostrar só 10" : "Mostrar todos (" + num(entradas.length) + ")"
      });
      b.addEventListener("click", function () {
        estado.expandido[chave] = !todos;
        renderDiagnostico();
      });
      caixa.appendChild(b);
    }
    return caixa;
  }

  // ---------------------------------------------------------------- medias cruas

  /* O motor devolve o efeito em indice, nao a media por post. Para as barras,
     repetimos aqui o pareamento dele (rede x tema x formato x tamanho, com 30
     de cada lado) e tiramos a media crua dos posts pareados. */
  function mediasPatrocinio(base, pos) {
    var nCat = base.catRotulos.length, nTipo = base.tipoRotulos.length;
    var nFx = base.faixaRotulos.length;
    var mapa = Object.create(null), i, r, chave, e;
    for (i = 0; i < pos.length; i++) {
      r = pos[i];
      chave = ((base.plat[r] * nCat + base.cat[r]) * nTipo + base.tipo[r]) * nFx + base.faixa[r];
      e = mapa[chave];
      if (!e) e = mapa[chave] = { p: [], o: [] };
      (base.pat[r] ? e.p : e.o).push(r);
    }
    var pagos = [], gratis = [];
    Object.keys(mapa).forEach(function (k) {
      var est = mapa[k];
      if (est.p.length >= MIN_ESTRATO && est.o.length >= MIN_ESTRATO) {
        pagos = pagos.concat(est.p);
        gratis = gratis.concat(est.o);
      }
    });
    function media(campo, lista) {
      var s = 0, j;
      if (!lista.length) return NaN;
      for (j = 0; j < lista.length; j++) s += base[campo][lista[j]];
      return s / lista.length;
    }
    return {
      postsUsados: pagos.length + gratis.length,
      nPatrocinado: pagos.length, nOrganico: gratis.length,
      pat: { interacoes: media("interacoes", pagos), views: media("views", pagos) },
      org: { interacoes: media("interacoes", gratis), views: media("views", gratis) }
    };
  }

  var CAMPOS_IDEIA = [
    { id: "plataforma", campo: "plat", rotulos: "platRotulos", pergunta: "Em qual rede social?" },
    { id: "formato", campo: "tipo", rotulos: "tipoRotulos", pergunta: "Em qual formato?" },
    { id: "categoria", campo: "cat", rotulos: "catRotulos", pergunta: "Sobre qual tema?" },
    { id: "faixa", campo: "faixa", rotulos: "faixaRotulos", pergunta: "Tamanho do influenciador", extra: true },
    { id: "idade", campo: "idade", rotulos: "idadeRotulos", pergunta: "Idade do público", extra: true },
    { id: "genero", campo: "genero", rotulos: "generoRotulos", pergunta: "Gênero do público", extra: true },
    { id: "pais", campo: "pais", rotulos: "paisRotulos", pergunta: "País do público", extra: true }
  ];

  /* Mesmo pareamento de ideia do motor, para tirar a media crua de interacoes. */
  function criteriosIdeia(base, ideia) {
    var out = [], i, c, v, cod;
    for (i = 0; i < CAMPOS_IDEIA.length; i++) {
      c = CAMPOS_IDEIA[i];
      v = ideia[c.id];
      if (v == null || v === "" || !base[c.rotulos]) continue;
      cod = base[c.rotulos].indexOf(v);
      if (cod < 0) continue;
      out.push({ campo: c.campo, cod: cod });
    }
    return out;
  }

  function mediasIdeia(base, pos, ideia) {
    var crits = criteriosIdeia(base, ideia);
    var pago = ideia.patrocinado === "sim" || ideia.patrocinado === "nao" ? ideia.patrocinado : "";
    var dentro = 0, fora = 0, somaD = 0, somaF = 0, i, r, j, ok;
    for (i = 0; i < pos.length; i++) {
      r = pos[i];
      ok = true;
      for (j = 0; j < crits.length; j++) {
        if (base[crits[j].campo][r] !== crits[j].cod) { ok = false; break; }
      }
      if (ok && pago === "sim" && !base.pat[r]) ok = false;
      if (ok && pago === "nao" && base.pat[r]) ok = false;
      if (ok) { dentro++; somaD += base.interacoes[r]; }
      else { fora++; somaF += base.interacoes[r]; }
    }
    return {
      nDentro: dentro, nFora: fora,
      mediaDentro: dentro ? somaD / dentro : NaN,
      mediaFora: fora ? somaF / fora : NaN
    };
  }

  // ------------------------------------------------- 2.1 resumo da campanha

  function frasePagarResumo(v) {
    if (v.tipo === "inconclusivo") return "Ainda não há posts parecidos suficientes para comparar.";
    if (v.tipo === "funciona") {
      return "Posts pagos renderam " + pctInt(v.efeito - 1) +
        "% a mais. Teste com poucos posts antes de aumentar o investimento.";
    }
    return "Posts pagos tiveram o mesmo resultado que posts sem pagar. " +
      "Use o dinheiro em outra coisa.";
  }

  function montarResumo(r) {
    var desemp = porTipo(r.desempenho, "taxa");
    var pub = r.publico ? porTipo(r.publico, "taxa") : null;
    var vPat = r.patrocinio.metricas.taxa;
    var melhores = desemp.funciona.concat(pub ? pub.funciona : []);
    var piores = desemp.nao_funciona.concat(pub ? pub.nao_funciona : []);
    var frase;

    if (melhores.length) {
      frase = "Neste histórico, " + listaCurta(melhores, false) + " trouxeram mais resultado.";
    } else if (piores.length) {
      frase = "Neste histórico, nada se destacou para melhor, mas " +
        listaCurta(piores, true) + " renderam menos.";
    } else if (vPat.tipo === "nao_funciona" || vPat.tipo === "sem_efeito") {
      frase = "Neste histórico, nenhuma escolha mudou o resultado. " +
        "E pagar influenciador não trouxe nada a mais.";
    } else {
      frase = "Neste histórico, nenhuma escolha mudou o resultado.";
    }

    var linhas = [];
    linhas.push({
      rotulo: "Onde e como postar",
      frases: desemp.funciona.length || desemp.nao_funciona.length
        ? frasesPrioridade(desemp)
        : ["Pode continuar como está. Nenhuma rede social, formato ou tema rendeu " +
          "mais que os outros."]
    });
    linhas.push({
      rotulo: "Para quem falar",
      frases: !pub
        ? ["Inclua a idade, o gênero e o país do seu público no arquivo para " +
          "responder esta parte (veja Como usar)."]
        : (pub.funciona.length || pub.nao_funciona.length
          ? frasesPrioridade(pub)
          : ["Pode falar com o mesmo público. Nenhum grupo de pessoas respondeu " +
            "melhor que os outros."])
    });
    linhas.push({
      rotulo: "Pagar influenciador?",
      selo: { tipo: tipoSeloPat(vPat.tipo), rotulo: ROTULO_PAT[vPat.tipo] },
      frases: [frasePagarResumo(vPat)]
    });
    linhas.push({
      rotulo: "O que testar nesta campanha",
      frases: ["Crie duas versões bem diferentes do mesmo post (por exemplo, um vídeo e " +
        "uma imagem) e publique pelo menos " + num(r.ab.posts) + " de cada. No fim, " +
        "compare qual teve mais interações."]
    });
    return { frase: frase, linhas: linhas };
  }

  function resumoTexto(r) {
    var b = montarResumo(r);
    var out = ["Resumo para a sua próxima campanha", ""];
    out.push("Dados: " + estado.nomeDados + " · " + posts(r.n) + " · " +
      dataBR(r.dataMin) + " a " + dataBR(r.dataMax));
    out.push("");
    out.push(b.frase);
    out.push("");
    b.linhas.forEach(function (l) {
      out.push(l.rotulo + ": " + (l.selo ? l.selo.rotulo + " — " : "") + l.frases[0]);
      l.frases.slice(1).forEach(function (f) { out.push("  " + f); });
    });
    return out.join("\n");
  }

  function copiaManual(texto) {
    var ta = el("textarea", {});
    ta.value = texto;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand("copy"); } catch (e) { /* navegador sem suporte */ }
    document.body.removeChild(ta);
  }

  function renderResumo(r) {
    var b = montarResumo(r);
    var sec = el("div", { class: "secao resumo", id: "secao-resumo" });

    var bCopiar = el("button", { class: "botao", text: "Copiar resumo" });
    var bImprimir = el("button", { class: "botao", text: "Imprimir resumo" });
    bCopiar.addEventListener("click", function () {
      var texto = resumoTexto(r);
      function ok() {
        bCopiar.textContent = "Copiado";
        setTimeout(function () { bCopiar.textContent = "Copiar resumo"; }, 1500);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(texto).then(ok, function () { copiaManual(texto); ok(); });
      } else { copiaManual(texto); ok(); }
    });
    bImprimir.addEventListener("click", function () {
      document.body.setAttribute("data-imprimir", "resumo");
      window.print();
      document.body.removeAttribute("data-imprimir");
    });

    sec.appendChild(el("div", { class: "secao-cabecalho" }, [
      el("h2", { text: "Resumo para a sua próxima campanha" }),
      el("div", { class: "acoes nao-imprimir" }, [bCopiar, bImprimir])
    ]));
    sec.appendChild(el("p", { class: "frase-principal", text: b.frase }));

    b.linhas.forEach(function (l) {
      var conteudo = el("div", { class: "conteudo" }, [
        l.selo ? selo(l.selo.tipo, l.selo.rotulo) : null
      ]);
      l.frases.forEach(function (f) {
        conteudo.appendChild(el("span", { class: "frase", text: f }));
      });
      sec.appendChild(el("div", { class: "linha-resumo" }, [
        el("span", { class: "rotulo", text: l.rotulo }), conteudo
      ]));
    });
    return sec;
  }

  // ------------------------------------------------- 2.2 confianca nos dados

  var PERGUNTAS_SAUDE = {
    alcance_seguidores: {
      pergunta: "Quem tem mais seguidores é mais visto?",
      sim: "Sim.", nao: "Não. Isso é estranho: normalmente é."
    },
    likes_alcance: {
      pergunta: "Posts mais vistos recebem mais curtidas?",
      sim: "Sim.", nao: "Não. Isso é estranho: normalmente recebem."
    },
    virais: {
      pergunta: "Alguns posts bombam e outros flopam?",
      sim: "Sim.", nao: "Não. Todos tiveram quase o mesmo resultado, o que é raro."
    },
    fracassos: {
      pergunta: "Existem posts que quase ninguém viu?",
      sim: "Sim.", nao: "Não. Na vida real, sempre existem alguns."
    }
  };

  function renderConfianca(r) {
    var alertas = r.saude.alertas;
    var tipo = alertas ? "inconclusivo" : "funciona";
    var rotulo = alertas ? "Atenção" : "Parecem confiáveis";
    var sec = recolhivel("secao-confianca", "Dá para confiar nestes dados?",
      [selo(tipo, rotulo)], false);

    sec.appendChild(el("p", {
      class: "leitura",
      text: alertas
        ? "Estes dados têm padrões estranhos para redes sociais. As conclusões valem " +
          "para eles, mas confirme de onde vieram."
        : "Os dados se comportam como dados reais de redes sociais."
    }));

    var lista = el("div", { class: "linhas" });
    r.saude.testes.forEach(function (t) {
      var pergunta, resposta;
      if (t.id === "volume") {
        pergunta = "Tem posts suficientes para concluir algo?";
        resposta = t.alerta
          ? "Não, só " + num(t.valor) + ". O ideal é ter pelo menos 500."
          : "Sim, " + posts(t.valor) + ".";
      } else {
        var p = PERGUNTAS_SAUDE[t.id];
        pergunta = p.pergunta;
        resposta = t.alerta ? p.nao : p.sim;
      }
      lista.appendChild(el("div", { class: "item" }, [
        el("span", { class: "nome", text: pergunta }),
        el("span", { class: "resposta", text: resposta })
      ]));
    });
    sec.appendChild(lista);
    return sec;
  }

  // ------------------------------------------------- 2.3 vale pagar?

  function fraseConclusaoPagar(v) {
    if (v.tipo === "inconclusivo") return "Ainda não há posts parecidos suficientes para comparar.";
    if (v.tipo === "funciona") {
      return "Os posts pagos tiveram " + pctInt(v.efeito - 1) + "% mais interações.";
    }
    return "Os posts pagos tiveram praticamente o mesmo resultado que os posts sem " +
      "pagar. Pagar não trouxe nada a mais.";
  }

  /* Mediana do custo dos posts pagos; so aparece com a coluna de custo. */
  function tabelaCustos(custos) {
    var linhas = [];
    if (custos.porInteracao) {
      linhas.push({ nome: "Custo de cada interação", q: custos.porInteracao });
    }
    if (custos.porConversao) {
      linhas.push({ nome: "Custo de cada venda", q: custos.porConversao });
    }
    if (!linhas.length) return null;
    return tabela([
      { rotulo: "No meio dos posts pagos", valor: function (l) { return l.nome; } },
      { rotulo: "Valor típico", num: true, valor: function (l) { return moeda(l.q.mediana); } },
      { rotulo: "Posts", num: true, valor: function (l) { return num(l.q.n); } }
    ], linhas);
  }

  function renderPagar(r) {
    var sec = el("div", { class: "secao" });
    sec.appendChild(el("h2", { text: "Vale a pena pagar influenciador?" }));
    sec.appendChild(el("p", {
      class: "secundario leitura",
      text: "Comparamos posts pagos e posts sem pagar que eram parecidos: mesma rede " +
        "social, mesmo tema, mesmo formato e influenciadores do mesmo tamanho."
    }));

    var med = mediasPatrocinio(estado.base, ENG.filtrar(estado.base, opcoesAtuais()));
    var vPat = r.patrocinio.metricas.taxa;
    var cor = tipoSeloPat(vPat.tipo);

    if (med.postsUsados) {
      sec.appendChild(el("h3", {}, [termo("Interações (curtidas, comentários e " +
        "compartilhamentos)", "interacoes")]));
      sec.appendChild(barras([
        {
          rotulo: termo("Sem pagar (orgânico)", "organico"), valor: med.org.interacoes,
          cor: "neutro", texto: "cerca de " + aprox(med.org.interacoes) + " interações por post"
        },
        {
          rotulo: termo("Pago (patrocinado)", "patrocinado"), valor: med.pat.interacoes,
          cor: cor, texto: "cerca de " + aprox(med.pat.interacoes) + " interações por post"
        }
      ]));
      sec.appendChild(el("h3", {}, [termo("Pessoas alcançadas (visualizações)", "alcance")]));
      sec.appendChild(barras([
        {
          rotulo: "Sem pagar (orgânico)", valor: med.org.views, cor: "neutro",
          texto: "cerca de " + aprox(med.org.views) + " visualizações por post"
        },
        {
          rotulo: "Pago (patrocinado)", valor: med.pat.views, cor: cor,
          texto: "cerca de " + aprox(med.pat.views) + " visualizações por post"
        }
      ]));
    }

    sec.appendChild(el("div", { class: "linhas" }, [
      el("div", { class: "item" }, [
        selo(cor, ROTULO_PAT[vPat.tipo]),
        el("span", { class: "nome", text: fraseConclusaoPagar(vPat) }),
        el("span", {
          class: "base",
          text: med.postsUsados ? analisamos(med.postsUsados) : ""
        })
      ])
    ]));

    if (r.custos) {
      sec.appendChild(el("h3", { text: "Quanto você pagou" }));
      sec.appendChild(el("p", {
        class: "secundario leitura",
        text: "Nos " + posts(r.custos.nPatrocinado) + " pagos deste período, " +
          moeda(r.custos.custoTotal) + " no total."
      }));
      var tc = tabelaCustos(r.custos);
      if (tc) sec.appendChild(tc);
    }
    if (!estado.base.temConversoes || !estado.base.temCusto) {
      sec.appendChild(el("p", {
        class: "vazio",
        text: "Quer saber se o patrocínio traz vendas? Inclua cliques, vendas e custo " +
          "no seu arquivo (veja Como usar)."
      }));
    }
    return sec;
  }

  // ------------------------------------------------- 2.4 a 2.7 respostas

  function renderMelhorPior(r) {
    var d = porTipo(r.desempenho, "taxa");
    var sec = el("div", { class: "secao" });
    sec.appendChild(el("h2", { text: "O que funcionou melhor e o que funcionou pior" }));
    if (!d.funciona.length && !d.nao_funciona.length) {
      sec.appendChild(el("p", {
        class: "vazio",
        text: "Testamos " + num(r.desempenho.segmentos.length) + " jeitos diferentes de " +
          "postar (redes sociais, formatos, temas e tamanhos de influenciador, sozinhos " +
          "e combinados). Nenhum rendeu mais ou menos que os outros. Ou seja: o resultado " +
          "não dependeu dessas escolhas."
      }));
      return sec;
    }
    sec.appendChild(el("h3", { text: "Funcionou melhor" }));
    sec.appendChild(listaLimitada("funciona", d.funciona, true,
      "Nada rendeu mais que os outros."));
    sec.appendChild(el("h3", { text: "Funcionou pior" }));
    sec.appendChild(listaLimitada("nao_funciona", d.nao_funciona, true,
      "Nada rendeu menos que os outros."));
    return sec;
  }

  function renderSemDiferenca(r) {
    var d = porTipo(r.desempenho, "taxa");
    var sec = recolhivel("secao-sem-diferenca", "Não faz diferença",
      [el("span", { class: "secundario", text: "(" + num(d.sem_efeito.length) + ")" })], false);
    sec.appendChild(el("p", {
      class: "leitura",
      text: "São escolhas que testamos e que deram praticamente o mesmo resultado. " +
        "Você não precisa se preocupar com elas."
    }));
    sec.appendChild(listaLimitada("sem_efeito", d.sem_efeito, false,
      "Nenhuma escolha ficou nesta situação."));
    return sec;
  }

  function renderSemResposta(r) {
    var d = porTipo(r.desempenho, "taxa");
    var sec = recolhivel("secao-sem-resposta", "Ainda não dá para saber",
      [el("span", { class: "secundario", text: "(" + num(d.inconclusivo.length) + ")" })], false);
    sec.appendChild(el("p", {
      class: "leitura",
      text: "Para estas escolhas, ainda faltam posts para ter certeza."
    }));
    sec.appendChild(listaLimitada("inconclusivo", d.inconclusivo, false,
      "Nenhuma: todas as escolhas tiveram posts suficientes para uma resposta."));
    return sec;
  }

  function renderPublico(r) {
    var sec = el("div", { class: "secao" });
    sec.appendChild(el("h2", { text: "Para quem falar?" }));
    if (!r.publico) {
      sec.appendChild(el("p", {
        class: "vazio",
        text: "Inclua a idade, o gênero e o país do seu público no arquivo para " +
          "responder esta pergunta (veja Como usar)."
      }));
      return sec;
    }
    var p = porTipo(r.publico, "taxa");
    if (!p.funciona.length && !p.nao_funciona.length) {
      sec.appendChild(el("p", {
        class: "vazio",
        text: "Nenhum grupo de pessoas (por idade, gênero ou país) respondeu melhor que " +
          "os outros. Pode manter o mesmo público."
      }));
      return sec;
    }
    sec.appendChild(el("h3", { text: "Respondeu melhor" }));
    sec.appendChild(listaLimitada("pub_funciona", p.funciona, true,
      "Nenhum grupo de pessoas respondeu melhor que os outros."));
    sec.appendChild(el("h3", { text: "Respondeu pior" }));
    sec.appendChild(listaLimitada("pub_nao_funciona", p.nao_funciona, true,
      "Nenhum grupo de pessoas respondeu pior que os outros."));
    return sec;
  }

  /* So aparece quando o arquivo tem a coluna de vendas. */
  function renderVendas(r) {
    var c = porTipo([r.desempenho, r.publico], "taxaConv");
    var sec = recolhivel("secao-vendas", "Quem vendeu mais e quem vendeu menos",
      [el("span", {
        class: "secundario",
        text: "(" + num(c.funciona.length) + " acima, " + num(c.nao_funciona.length) + " abaixo)"
      })], false);
    sec.appendChild(el("p", {
      class: "leitura",
      text: "Mesma conta, olhando vendas em vez de interações."
    }));
    sec.appendChild(el("h3", { text: "Vendeu mais" }));
    sec.appendChild(listaLimitada("venda_funciona", c.funciona, true,
      "Nada vendeu mais que os outros."));
    sec.appendChild(el("h3", { text: "Vendeu menos" }));
    sec.appendChild(listaLimitada("venda_nao_funciona", c.nao_funciona, true,
      "Nada vendeu menos que os outros."));
    return sec;
  }

  // ------------------------------------------------- 2.8 como calculamos

  function renderMetodo(r) {
    var sec = recolhivel("secao-metodo", "Como calculamos (para especialistas)", [], false);
    var dl = el("dl", { class: "metodo" });
    function item(dt, dd) {
      dl.appendChild(el("dt", { text: dt }));
      dl.appendChild(el("dd", { text: dd }));
    }
    item("Índice de cada post",
      "Dividimos o valor do post pela média da mesma métrica na plataforma dele, " +
      "sempre dentro do recorte filtrado. Assim um post do TikTok é comparado com " +
      "posts do TikTok. Para avaliar a própria plataforma, usamos a média geral do recorte.");
    item("Diferença do segmento",
      "Comparamos a média do índice dentro do segmento com a média do índice no resto do " +
      "recorte, fora dele. +5% quer dizer 5% acima do resto. Não comparamos com a média " +
      "geral, porque ela inclui o próprio segmento e encolhe a diferença.");
    item("Intervalo de confiança (IC)",
      "Para cada segmento calculamos erro padrão = √(dp²dentro ÷ n dentro + dp²fora ÷ n fora). " +
      "O IC de decisão usa correção de Bonferroni para o número de comparações do bloco (k = " +
      num(r.desempenho.k) + " em desempenho" +
      (r.publico ? " e k = " + num(r.publico.k) + " em público" : "") +
      "), com z = " + num(ENG.qnorm(1 - 0.05 / (2 * r.desempenho.k)), 3) +
      ". O IC de equivalência é de 90% e não leva correção (z = 1,645).");
    item("Margem relevante",
      "Está em " + num(r.margem * 100) + "%. Só chamamos de ganho ou perda o que passa dessa " +
      "margem e tem o IC de decisão inteiro acima (ou abaixo) de 1. Na tela, essa margem " +
      "aparece como \"Diferença mínima que importa\".");
    item("Não faz diferença (sem efeito comprovado)",
      "O IC de equivalência cabe todo dentro de [" + num(1 - r.margem, 2) + "; " +
      num(1 + r.margem, 2) + "]. É uma conclusão: o segmento não muda o resultado além da margem.");
    item("Ainda não dá para saber (inconclusivo)",
      "Menos de 100 posts, ou o IC largo demais para decidir. Nesse caso estimamos quantos " +
      "posts faltariam com n = 2 × ((1,96 + 0,84) × desvio padrão ÷ margem)², usando o desvio " +
      "padrão do índice no recorte.");
    item("Patrocínio",
      "Comparamos patrocinados e orgânicos dentro de estratos de plataforma × categoria × " +
      "formato × faixa de creator, exigindo " + num(MIN_ESTRATO) + " de cada lado. " +
      num(r.patrocinio.estratosUsados) + " de " + num(r.patrocinio.estratosExistentes) +
      " estratos entraram, somando " + num(r.patrocinio.postsUsados) + " posts (" +
      num(r.patrocinio.nPatrocinado) + " patrocinados e " + num(r.patrocinio.nOrganico) +
      " orgânicos). O efeito é a média das diferenças de índice, ponderada pelo tamanho do " +
      "estrato, e usa a mesma regra de veredito sem correção (k = 1). As barras da tela " +
      "mostram a média crua de interações e de views desses mesmos posts pareados, por post.");
    item("Testar uma ideia",
      "Os posts que combinam com a ideia contra o resto do recorte, pela mesma regra, " +
      "sem correção (k = 1), porque é uma comparação só. As barras mostram a média crua " +
      "de interações por post dentro e fora da ideia.");
    item("Resultado do mês",
      "Médias por post do recorte filtrado, multiplicadas pelo número de posts do mês. " +
      "O ganho do patrocínio usa o efeito estratificado: (efeito − 1) × média do orgânico × " +
      "posts patrocinados. A coluna \"Se todos fossem sem pagar\" é o total do plano menos " +
      "esse ganho.");
    item("Dá para confiar nestes dados?",
      "Cinco testes de sanidade: alcance acompanha seguidores (correlação dos logs ≥ 0,3), " +
      "likes acompanham alcance (correlação ≥ 0,3), existe variação de alcance " +
      "(variância ÷ média ≥ 10), existem posts fracassados (≥ 1% abaixo de 10% da mediana " +
      "de interações) e volume mínimo (≥ 500 posts).");
    sec.appendChild(dl);
    return sec;
  }

  function renderDiagnostico() {
    var painel = document.getElementById("painel-diag");
    var r = estado.resultado;
    painel.textContent = "";

    if (!r || r.vazio) {
      painel.appendChild(el("div", { class: "secao" }, [
        el("h2", { text: "Nenhum post neste período" }),
        el("p", {
          class: "leitura secundario",
          text: "Escolha um período maior ou marque mais redes sociais."
        })
      ]));
      return;
    }

    painel.appendChild(renderResumo(r));
    painel.appendChild(renderConfianca(r));
    painel.appendChild(renderPagar(r));
    painel.appendChild(renderMelhorPior(r));
    painel.appendChild(renderSemDiferenca(r));
    painel.appendChild(renderSemResposta(r));
    painel.appendChild(renderPublico(r));
    if (r.metricas.indexOf("taxaConv") >= 0) painel.appendChild(renderVendas(r));
    painel.appendChild(renderMetodo(r));
  }

  // ---------------------------------------------------------------- como usar

  var DICIONARIO = [
    ["post_date", "data", "sim", "Data e hora da publicação (AAAA-MM-DD HH:MM)"],
    ["platform", "texto", "sim", "Instagram, TikTok, YouTube…"],
    ["content_type", "texto", "sim", "video, image, text, mixed"],
    ["content_category", "texto", "sim", "Tema do conteúdo"],
    ["follower_count", "número", "sim", "Seguidores do perfil no dia do post"],
    ["is_sponsored", "sim/não", "sim", "Você pagou um influenciador por este post?"],
    ["views", "número", "sim", "Visualizações (quantas vezes o post foi visto)"],
    ["likes", "número", "sim", "Curtidas"],
    ["shares", "número", "sim", "Compartilhamentos"],
    ["comments_count", "número", "sim", "Comentários"],
    ["audience_age_distribution", "texto", "não", "Idade da maior parte do seu público"],
    ["audience_gender_distribution", "texto", "não", "Gênero da maior parte do seu público"],
    ["audience_location", "texto", "não", "País da maior parte do seu público"],
    ["hashtags", "texto", "não", "Hashtags separadas por vírgula"],
    ["clicks", "número", "não", "Cliques no link do post"],
    ["conversions", "número", "não", "Vendas ou cadastros vindos do post"],
    ["cost", "número", "não", "Quanto você pagou pelo post (0 se não pagou nada)"]
  ];

  var ONDE_EXPORTAR = [
    ["Meta Business Suite (Instagram)", "Insights → Conteúdo: a lista de posts traz alcance, " +
      "curtidas, comentários e compartilhamentos; use \"Exportar dados\"."],
    ["TikTok Studio", "Analytics → Conteúdo: desempenho por vídeo, com visualizações, curtidas, " +
      "comentários e compartilhamentos; use \"Baixar dados\"."],
    ["YouTube Studio", "Analytics → Conteúdo: métricas por vídeo, com visualizações, curtidas e " +
      "comentários; use o botão de download da tabela."]
  ];

  var COMO_LER = [
    ["funciona", "Rendeu mais que os outros posts. Use na próxima campanha e confirme " +
      "com um teste antes de investir mais."],
    ["nao_funciona", "Rendeu menos que os outros posts. Repense ou tire do plano."],
    ["sem_efeito", "Rendeu praticamente o mesmo que os outros. Escolha pelo que for " +
      "mais barato ou combinar mais com a sua marca."],
    ["inconclusivo", "Ainda faltam posts para responder. Teste antes, com o número de " +
      "posts que a ferramenta indica."]
  ];

  var DICAS = [
    "Use pelo menos 500 posts. Com menos que isso, a maioria das respostas vai ser " +
      "\"Ainda não dá para saber\".",
    "Não divida as interações pelo número de seguidores: perfis pequenos parecem " +
      "melhores só por terem menos seguidores.",
    "Um campeão isolado não é prova. Quando você olha muitos grupos ao mesmo tempo, " +
      "alguns parecem melhores por sorte. A ferramenta já desconta isso.",
    "\"Funcionou melhor\" quer dizer que rendeu mais no passado. Teste antes de " +
      "investir muito.",
    "Inclua cliques, vendas e custo no arquivo para avaliar campanhas de venda."
  ];

  /* Cabecalho + 3 linhas de exemplo (1 sem pagar, 2 pagas). */
  var EXEMPLO_TEMPLATE = [
    ["2026-03-02 18:30", "Instagram", "video", "beauty", "48000", "nao", "21500", "1480",
      "210", "96", "25-34", "female", "Brazil", "tutorial,beleza", "320", "9", "0"],
    ["2026-03-05 12:00", "TikTok", "video", "tech", "120000", "sim", "86000", "5400",
      "910", "380", "18-24", "male", "Brazil", "review,tecnologia", "2100", "64", "3500"],
    ["2026-03-09 09:15", "YouTube", "mixed", "lifestyle", "75000", "sim", "40200", "2600",
      "310", "145", "25-34", "unknown", "USA", "rotina,lifestyle", "980", "27", "2800"]
  ];

  function baixarTemplate() {
    var linhas = [DICIONARIO.map(function (c) { return c[0]; }).join(",")];
    EXEMPLO_TEMPLATE.forEach(function (l) { linhas.push(l.join(",")); });
    var blob = new Blob(["﻿" + linhas.join("\n") + "\n"], { type: "text/csv;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var a = el("a", { href: url, download: "modelo_decisor.csv" });
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 0);
    aviso("modelo_decisor.csv baixado");
  }

  function montarComoUsar() {
    var t = tabela([
      { rotulo: "Coluna", valor: function (l) { return el("code", { text: l[0] }); } },
      { rotulo: "Tipo", valor: function (l) { return l[1]; } },
      { rotulo: "Obrigatória", valor: function (l) { return l[2]; } },
      { rotulo: "O que é", valor: function (l) { return l[3]; } }
    ], DICIONARIO);
    t.id = "tabela-dicionario";
    document.getElementById("tabela-dicionario").replaceWith(t);

    var exportar = document.getElementById("lista-exportar");
    ONDE_EXPORTAR.forEach(function (l) {
      exportar.appendChild(el("div", { class: "item" }, [
        el("span", { class: "chave", text: l[0] }),
        el("span", { class: "texto", text: l[1] })
      ]));
    });

    var selos = document.getElementById("lista-selos");
    COMO_LER.forEach(function (l) {
      selos.appendChild(el("div", { class: "item" }, [
        selo(l[0]),
        el("span", { class: "texto", text: l[1] })
      ]));
    });

    var dicas = document.getElementById("lista-dicas");
    DICAS.forEach(function (d) { dicas.appendChild(el("li", { text: d })); });

    document.getElementById("btn-template").addEventListener("click", baixarTemplate);
  }

  // ---------------------------------------------------------------- passo 1: ideia

  var EXEMPLOS = [
    { nome: "Vídeo no TikTok", valores: { plataforma: "TikTok", formato: "video" } },
    { nome: "Post pago no Instagram", valores: { plataforma: "Instagram", patrocinado: "sim" } },
    { nome: "Imagem sobre tecnologia", valores: { formato: "image", categoria: "tech" } }
  ];

  function campoIdeia(c) {
    var rotulos = estado.base[c.rotulos];
    if (!rotulos) return null;
    var sel = el("select", { id: "i-" + c.id }, [el("option", { value: "", text: "Qualquer" })]);
    rotulos.forEach(function (v) {
      sel.appendChild(el("option", { value: v, text: rotuloOpcao(c.id, v) }));
    });
    sel.addEventListener("change", conferirIdeia);
    return el("div", { class: "campo" }, [
      el("label", { for: "i-" + c.id, text: c.pergunta }), sel
    ]);
  }

  function montarCamposIdeia() {
    var visiveis = document.getElementById("campos-ideia");
    var caixaExtra = document.getElementById("mais-opcoes-caixa");
    visiveis.textContent = "";
    caixaExtra.textContent = "";

    CAMPOS_IDEIA.filter(function (c) { return !c.extra; }).forEach(function (c) {
      var campo = campoIdeia(c);
      if (campo) visiveis.appendChild(campo);
    });

    var pat = el("select", { id: "i-patrocinado" }, [
      el("option", { value: "", text: "Tanto faz" }),
      el("option", { value: "sim", text: "Sim" }),
      el("option", { value: "nao", text: "Não" })
    ]);
    pat.addEventListener("change", conferirIdeia);
    visiveis.appendChild(el("div", { class: "campo" }, [
      el("label", { for: "i-patrocinado", text: "Vai pagar influenciador?" }), pat
    ]));

    var extras = el("div", { class: "form-campos" });
    CAMPOS_IDEIA.filter(function (c) { return c.extra; }).forEach(function (c) {
      var campo = campoIdeia(c);
      if (campo) extras.appendChild(campo);
    });
    if (!extras.childNodes.length) return;
    extras.hidden = true;
    var link = el("button", { class: "botao-texto", type: "button", "aria-expanded": "false" },
      [txt("Mais opções")]);
    link.addEventListener("click", function () {
      extras.hidden = !extras.hidden;
      link.setAttribute("aria-expanded", extras.hidden ? "false" : "true");
      link.textContent = extras.hidden ? "Mais opções" : "Menos opções";
    });
    caixaExtra.appendChild(link);
    caixaExtra.appendChild(extras);
  }

  function lerIdeia() {
    var ideia = {};
    CAMPOS_IDEIA.forEach(function (c) {
      var sel = document.getElementById("i-" + c.id);
      if (sel) ideia[c.id] = sel.value;
    });
    var pat = document.getElementById("i-patrocinado");
    ideia.patrocinado = pat ? pat.value : "";
    return ideia;
  }

  function ideiaVazia(ideia) {
    return !Object.keys(ideia).some(function (k) { return ideia[k]; });
  }

  /* O botao so libera quando pelo menos um campo sai de "Qualquer". */
  function conferirIdeia() {
    var vazia = ideiaVazia(lerIdeia());
    document.getElementById("btn-ideia").disabled = vazia;
    document.getElementById("dica-ideia").hidden = !vazia;
  }

  function aplicarExemplo(valores) {
    CAMPOS_IDEIA.forEach(function (c) {
      var sel = document.getElementById("i-" + c.id);
      if (sel) sel.value = valores[c.id] || "";
    });
    var pat = document.getElementById("i-patrocinado");
    if (pat) pat.value = valores.patrocinado || "";
    conferirIdeia();
    avaliarIdeia();
  }

  /* Um exemplo so aparece se todos os valores dele existirem nos dados. */
  function exemploServe(ex) {
    return CAMPOS_IDEIA.every(function (c) {
      var v = ex.valores[c.id];
      if (!v) return true;
      var rotulos = estado.base[c.rotulos];
      return !!rotulos && rotulos.indexOf(v) >= 0;
    });
  }

  function montarExemplos() {
    var caixa = document.getElementById("exemplos-ideia");
    caixa.textContent = "";
    var usaveis = EXEMPLOS.filter(exemploServe);
    if (!usaveis.length) return;
    caixa.appendChild(el("span", { class: "titulo-exemplos", text: "Exemplos prontos" }));
    var lista = el("div", { class: "lista-exemplos" });
    usaveis.forEach(function (ex) {
      var b = el("button", { class: "botao botao-pequeno", type: "button", text: ex.nome });
      b.addEventListener("click", function () { aplicarExemplo(ex.valores); });
      lista.appendChild(b);
    });
    caixa.appendChild(lista);
  }

  /* Tabela de vereditos da OS-10 secao 3.2. */
  function textoIdeia(v, patrocinada) {
    var quer, fazer, tipo = v.tipo;
    if (tipo === "funciona") {
      quer = "Posts parecidos com a sua ideia tiveram " + pctInt(v.lift - 1) +
        "% mais interações que os outros.";
      fazer = "Boa ideia. Comece com poucos posts e confira se o resultado se repete " +
        "antes de investir mais.";
    } else if (tipo === "nao_funciona") {
      quer = "Posts parecidos com a sua ideia tiveram " + pctInt(v.lift - 1) +
        "% menos interações que os outros.";
      fazer = "Repense a ideia ou teste uma alternativa.";
    } else if (tipo === "sem_efeito") {
      quer = "Posts parecidos com a sua ideia tiveram praticamente o mesmo resultado " +
        "que os outros.";
      fazer = "Pode fazer, mas não espere um resultado melhor. Escolha pelo que for mais " +
        "barato ou combinar mais com a sua marca.";
    } else {
      var semanas = Math.max(1, Math.round(v.semanas || 0));
      quer = "Ainda não há posts parecidos suficientes para responder.";
      fazer = "Teste: publique cerca de " + num(v.ab.posts) + " posts dessa ideia (umas " +
        num(semanas) + (semanas === 1 ? " semana" : " semanas") +
        " no seu ritmo atual) e volte aqui.";
    }
    if (patrocinada && patrocinioSemGanho(estado.resultado)) {
      fazer += " Lembre: posts pagos tiveram o mesmo resultado que posts sem pagar.";
    }
    return { tipo: tipo, rotulo: ROTULO_VEREDITO[tipo], quer: quer, fazer: fazer };
  }

  function renderResIdeia() {
    var caixa = document.getElementById("res-ideia");
    caixa.textContent = "";
    caixa.className = "resultado-ideia fade";
    var res = estado.ideia;

    if (!res) {
      caixa.className = "resultado-ideia";
      caixa.appendChild(el("p", {
        class: "vazio",
        text: "Monte uma ideia ao lado e clique em \"Ver se a ideia funciona\"."
      }));
      return;
    }
    caixa.appendChild(el("h2", { text: "O que dizem os seus posts" }));
    if (res.vazio || !res.n) {
      caixa.appendChild(el("p", {
        class: "vazio",
        text: "Nenhum post seu combina com essa ideia. Deixe algum campo em \"Qualquer\" " +
          "ou escolha um período maior."
      }));
      return;
    }
    if (res.semComparacao) {
      caixa.appendChild(el("p", {
        class: "vazio",
        text: "A ideia inclui todos os seus posts, então não há com o que comparar. " +
          "Escolha menos opções."
      }));
      return;
    }

    var v = res.metricas.taxa;
    var t = textoIdeia(v, res.patrocinada);
    caixa.appendChild(selo(t.tipo, t.rotulo, true));
    caixa.appendChild(el("p", { class: "explica" }, [
      el("span", { class: "rotulo", text: "O que isso quer dizer:" }),
      el("span", { text: t.quer })
    ]));
    caixa.appendChild(el("p", { class: "explica" }, [
      el("span", { class: "rotulo", text: "O que fazer:" }),
      el("span", { text: t.fazer })
    ]));

    var med = mediasIdeia(estado.base, ENG.filtrar(estado.base, opcoesAtuais()), lerIdeia());
    if (isFinite(med.mediaDentro) && isFinite(med.mediaFora)) {
      caixa.appendChild(el("h3", {}, [termo("Interações (curtidas, comentários e " +
        "compartilhamentos)", "interacoes")]));
      caixa.appendChild(barras([
        {
          rotulo: "Posts como a sua ideia", valor: med.mediaDentro, cor: t.tipo,
          texto: "cerca de " + aprox(med.mediaDentro) + " interações por post"
        },
        {
          rotulo: "Todos os outros posts", valor: med.mediaFora, cor: "neutro",
          texto: "cerca de " + aprox(med.mediaFora) + " interações por post"
        }
      ]));
    }
    caixa.appendChild(el("p", {
      class: "secundario",
      text: "Analisamos " + posts(res.n) + " parecidos com a sua ideia."
    }));
  }

  function avaliarIdeia() {
    if (!estado.resultado || estado.resultado.vazio) {
      estado.ideia = { vazio: true, n: 0 };
    } else {
      estado.ideia = ENG.avaliarIdeia(estado.base, opcoesAtuais(), lerIdeia());
    }
    renderResIdeia();
  }

  // ---------------------------------------------------------------- passo 2: o mês

  var CAMPOS_PLANO = [
    { id: "s-org", rotulo: "Posts sem pagar (orgânicos)", ajuda: "organico", valor: 30 },
    { id: "s-pat", rotulo: "Posts pagos (com influenciador)", ajuda: "patrocinado", valor: 10 },
    { id: "s-valor", rotulo: "Quanto vai pagar por post pago (R$)", valor: 2000 }
  ];

  function montarCamposPlano() {
    var caixa = document.getElementById("campos-plano");
    caixa.textContent = "";
    CAMPOS_PLANO.forEach(function (c) {
      var rot = el("label", { for: c.id });
      if (c.ajuda) rot.appendChild(termo(c.rotulo, c.ajuda));
      else rot.textContent = c.rotulo;
      caixa.appendChild(el("div", { class: "campo" }, [
        rot,
        el("input", { type: "number", id: c.id, min: "0", step: "1", value: c.valor })
      ]));
    });
  }

  function lerPlano() {
    function v(id) { return Math.max(0, +document.getElementById(id).value || 0); }
    return {
      postsOrganicos: v("s-org"), postsPatrocinados: v("s-pat"),
      valorPorPatrocinado: v("s-valor"), custoPorOrganico: 0
    };
  }

  function forte(texto) {
    return el("strong", { text: texto });
  }

  function fraseDoMes(p) {
    var v = p.metricas.views, it = p.metricas.interacoes;
    return el("p", { class: "texto-resultado" }, [
      txt("Com " + posts(p.postsOrganicos) + " sem pagar e " + num(p.postsPatrocinados) +
        " posts pagos, você deve alcançar "),
      forte("cerca de " + aprox(v.total) + " visualizações"),
      txt(" no mês. Você também deve receber "),
      forte("cerca de " + aprox(it.total) + " interações"),
      txt(". O investimento será de "),
      forte(moeda(p.investimentoTotal)),
      txt(".")
    ]);
  }

  /* "Se todos fossem sem pagar": o total do plano menos o ganho do patrocinio. */
  function semPagar(metrica) {
    var g = metrica.ganho;
    return metrica.total - (isFinite(g.valor) ? g.valor : 0);
  }

  function tabelaComparativa(p) {
    var v = p.metricas.views, it = p.metricas.interacoes;
    var linhas = [
      { nome: "Posts no mês", plano: num(p.postsTotal), org: num(p.postsTotal) },
      {
        nome: termo("Visualizações", "alcance"),
        plano: aprox(v.total), org: aprox(semPagar(v))
      },
      { nome: "Interações", plano: aprox(it.total), org: aprox(semPagar(it)) },
      { nome: "Investimento", plano: moeda(p.investimentoTotal), org: moeda(0) }
    ];
    return tabela([
      { rotulo: "", valor: function (l) { return l.nome; } },
      { rotulo: "Seu plano", num: true, valor: function (l) { return l.plano; } },
      { rotulo: "Se todos fossem sem pagar", num: true, valor: function (l) { return l.org; } }
    ], linhas, "comparativo");
  }

  function conclusaoDoMes(p) {
    var it = p.metricas.interacoes, g = it.ganho;
    var semGanho = !isFinite(g.valor) || g.valor <= 0 || g.incluiZero;
    var cor = tipoSeloPat(it.vereditoPatrocinio);
    if (semGanho) {
      return el("div", { class: "conclusao", "data-cor": cor }, [
        el("p", {}, [
          txt("Pagar os " + posts(p.postsPatrocinados) + " custa "),
          forte(moeda(p.investimentoPatrocinio)),
          txt(" e traz praticamente o mesmo resultado que publicá-los sem pagar. "),
          forte("Você economizaria " + moeda(p.investimentoPatrocinio) + " no mês.")
        ])
      ]);
    }
    var porInteracao = p.custoPorInteracaoAdicional;
    return el("div", { class: "conclusao", "data-cor": "funciona" }, [
      el("p", {}, [
        txt("Os " + posts(p.postsPatrocinados) + " pagos trazem cerca de " +
          aprox(g.valor) + " interações a mais" +
          (porInteracao != null ? ", o que dá cerca de " : ".")),
        porInteracao != null ? forte(moeda(porInteracao) + " por interação extra") : null,
        porInteracao != null ? txt(".") : null
      ])
    ]);
  }

  function renderResPlano() {
    var caixa = document.getElementById("res-plano");
    caixa.textContent = "";
    caixa.className = "fade";
    var p = estado.plano;

    if (!p) {
      caixa.className = "";
      caixa.appendChild(el("p", {
        class: "vazio",
        text: "Diga quantos posts você vai publicar e clique em \"Calcular resultado do mês\"."
      }));
      return;
    }
    caixa.appendChild(el("h2", { text: "O seu mês" }));
    if (p.vazio) {
      caixa.appendChild(el("p", {
        class: "vazio",
        text: "Nenhum post neste período. Escolha um período maior ou marque mais redes sociais."
      }));
      return;
    }

    caixa.appendChild(fraseDoMes(p));
    caixa.appendChild(tabelaComparativa(p));
    if (p.postsPatrocinados > 0) caixa.appendChild(conclusaoDoMes(p));
    caixa.appendChild(el("p", {
      class: "nota",
      text: "Este cálculo supõe que postar mais não diminui o resultado de cada post. " +
        "Se for aumentar muito o número de posts, faça isso aos poucos e acompanhe."
    }));
  }

  function calcularPlano() {
    estado.plano = ENG.simular(estado.base, opcoesAtuais(), lerPlano());
    renderResPlano();
  }

  function montarPlanejar() {
    montarExemplos();
    montarCamposIdeia();
    montarCamposPlano();
    conferirIdeia();
    document.getElementById("btn-ideia").addEventListener("click", avaliarIdeia);
    document.getElementById("btn-simular").addEventListener("click", calcularPlano);
    renderResIdeia();
    renderResPlano();
  }

  // ---------------------------------------------------------------- filtros

  function janela() {
    if (estado.periodo === "tudo") return { de: null, ate: null };
    if (estado.periodo === "custom") {
      return {
        de: estado.de ? ENG.parseData(estado.de) : null,
        ate: estado.ate ? ENG.parseData(estado.ate) + (ENG.DIA_MS - 1) : null
      };
    }
    return ENG.janelaUltimosDias(estado.base, +estado.periodo);
  }

  function opcoesAtuais() {
    var j = janela();
    return { de: j.de, ate: j.ate, plataformas: estado.plataformas, margem: estado.margem };
  }

  function recalcular(avisar) {
    estado.resultado = ENG.analisar(estado.base, opcoesAtuais());
    estado.expandido = {};
    // a ideia e o plano valiam para o período anterior
    estado.ideia = null;
    estado.plano = null;
    renderDiagnostico();
    renderResIdeia();
    renderResPlano();
    atualizarInfoDados();
    if (avisar) aviso("Recalculado para " + posts(estado.resultado.n));
  }

  var timerAviso = null;

  function limparAviso() {
    clearTimeout(timerAviso);
    var a = document.getElementById("aviso");
    a.removeAttribute("data-visivel");
    a.textContent = "";
  }

  function aviso(texto) {
    var a = document.getElementById("aviso");
    a.textContent = texto;
    a.setAttribute("data-visivel", "sim");
    clearTimeout(timerAviso);
    timerAviso = setTimeout(function () { a.removeAttribute("data-visivel"); }, 2200);
  }

  function atualizarInfoDados() {
    var r = estado.resultado;
    document.getElementById("dados-info").textContent =
      "Dados: " + estado.nomeDados + " · " + posts(r && !r.vazio ? r.n : 0) +
      (r && !r.vazio ? " · " + dataBR(r.dataMin) + " a " + dataBR(r.dataMax) : "");
  }

  // ---------------------------------------------------------------- barra superior

  var menus = [];

  function fecharMenus(exceto) {
    menus.forEach(function (m) {
      if (m.painel === exceto) return;
      m.painel.setAttribute("data-aberto", "nao");
      m.botao.setAttribute("aria-expanded", "false");
    });
  }

  function ligarMenu(idBotao, idPainel) {
    var botao = document.getElementById(idBotao);
    var painel = document.getElementById(idPainel);
    menus.push({ botao: botao, painel: painel });
    botao.addEventListener("click", function (ev) {
      ev.stopPropagation();
      var aberto = painel.getAttribute("data-aberto") === "sim";
      fecharMenus(aberto ? null : painel);
      painel.setAttribute("data-aberto", aberto ? "nao" : "sim");
      botao.setAttribute("aria-expanded", aberto ? "false" : "true");
    });
    painel.addEventListener("click", function (ev) { ev.stopPropagation(); });
  }

  function montarFiltroRedes() {
    var painel = document.getElementById("painel-redes");
    painel.textContent = "";
    painel.appendChild(el("span", { class: "titulo-menu", text: "Mostrar posts destas redes" }));
    estado.base.platRotulos.forEach(function (p) {
      var cb = el("input", { type: "checkbox", value: p, checked: true });
      cb.addEventListener("change", function () {
        var marcadas = [].slice.call(painel.querySelectorAll("input:checked"))
          .map(function (i) { return i.value; });
        if (!marcadas.length) { cb.checked = true; return; }
        estado.plataformas = marcadas;
        rotuloRedes();
        recalcular(true);
      });
      painel.appendChild(el("label", {}, [cb, el("span", { text: p })]));
    });
    rotuloRedes();
  }

  function rotuloRedes() {
    var total = estado.base.platRotulos.length, n = estado.plataformas.length;
    document.getElementById("f-redes").textContent =
      n === total ? "Todas" : (n === 1 ? estado.plataformas[0] : n + " escolhidas");
  }

  function montarAjustes() {
    var sel = document.getElementById("f-margem");
    sel.textContent = "";
    for (var p = 5; p <= 30; p += 5) {
      sel.appendChild(el("option", { value: p / 100, text: p + "%", selected: p === 10 }));
    }
    sel.addEventListener("change", function () {
      estado.margem = +sel.value;
      recalcular(true);
    });
  }

  function montarFiltroPeriodo() {
    var sel = document.getElementById("f-periodo");
    var cDe = document.getElementById("campo-de"), cAte = document.getElementById("campo-ate");
    var iDe = document.getElementById("f-de"), iAte = document.getElementById("f-ate");
    sel.addEventListener("change", function () {
      estado.periodo = sel.value;
      var custom = estado.periodo === "custom";
      cDe.hidden = !custom; cAte.hidden = !custom;
      if (custom) {
        iDe.min = iAte.min = dataISO(estado.base.dataMin);
        iDe.max = iAte.max = dataISO(estado.base.dataMax);
        if (!iDe.value) iDe.value = dataISO(estado.base.dataMin);
        if (!iAte.value) iAte.value = dataISO(estado.base.dataMax);
        estado.de = iDe.value; estado.ate = iAte.value;
      }
      recalcular(true);
    });
    [iDe, iAte].forEach(function (i) {
      i.addEventListener("change", function () {
        estado.de = iDe.value; estado.ate = iAte.value;
        recalcular(true);
      });
    });
  }

  // ---------------------------------------------------------------- tema

  var CHAVE_TEMA = "decisor-tema";

  function lerTemaSalvo() {
    try {
      return localStorage.getItem(CHAVE_TEMA);
    } catch (e) {
      return null;   // sem localStorage a ferramenta segue funcionando
    }
  }

  function salvarTema(valor) {
    try {
      localStorage.setItem(CHAVE_TEMA, valor);
    } catch (e) { /* sem localStorage a escolha vale só nesta visita */ }
  }

  function aplicarTema(valor) {
    estado.tema = valor;
    if (valor === "automatico") document.documentElement.removeAttribute("data-tema");
    else document.documentElement.setAttribute("data-tema", valor);
  }

  function montarTema() {
    var salvo = lerTemaSalvo();
    var inicial = salvo === "claro" || salvo === "escuro" ? salvo : "automatico";
    aplicarTema(inicial);
    [].slice.call(document.querySelectorAll("input[name=tema]")).forEach(function (r) {
      r.checked = r.value === inicial;
      r.addEventListener("change", function () {
        if (!r.checked) return;
        aplicarTema(r.value);
        salvarTema(r.value);
        fecharMenus(null);
      });
    });
  }

  // ---------------------------------------------------------------- abas

  function montarAbas() {
    var pares = [["aba-como", "painel-como"], ["aba-diag", "painel-diag"],
      ["aba-plan", "painel-plan"]];
    pares.forEach(function (par) {
      document.getElementById(par[0]).addEventListener("click", function () {
        fecharBaloes();
        pares.forEach(function (p) {
          var ativo = p[0] === par[0];
          document.getElementById(p[0]).setAttribute("aria-selected", ativo ? "true" : "false");
          document.getElementById(p[1]).hidden = !ativo;
        });
      });
    });
  }

  // ---------------------------------------------------------------- arquivo

  function mostrarErro(msg) {
    limparAviso();
    var painel = document.getElementById("painel-diag");
    var caixa = el("div", { class: "erro", text: msg + " Os dados anteriores continuam na tela." });
    painel.insertBefore(caixa, painel.firstChild);
    caixa.scrollIntoView({ block: "nearest" });
  }

  function processarArquivo(file) {
    if (!file) return;
    aviso("Lendo " + file.name + "…");
    Papa.parse(file, {
      header: true, dynamicTyping: false, skipEmptyLines: true,
      complete: function (res) {
        aviso("Analisando " + posts(res.data.length) + "…");
        setTimeout(function () { aplicarCSV(file.name, res.data); }, 0);
      },
      error: function (err) { mostrarErro("Não foi possível ler o arquivo: " + err.message); }
    });
  }

  function aplicarCSV(nome, linhas) {
    var nova = ENG.carregarLinhas(linhas);
    if (nova.erro === "colunas") {
      mostrarErro("O arquivo não tem as colunas: " + nova.faltando.join(", ") +
        ". Baixe o modelo de planilha na aba Como usar.");
      return;
    }
    if (nova.erro === "vazio") {
      mostrarErro("O arquivo não tem nenhuma linha utilizável. Confira as colunas de " +
        "data, visualizações, curtidas, compartilhamentos e comentários.");
      return;
    }
    estado.base = nova;
    estado.nomeDados = nome;
    estado.plataformas = nova.platRotulos.slice();
    estado.periodo = "tudo";
    document.getElementById("f-periodo").value = "tudo";
    document.getElementById("campo-de").hidden = true;
    document.getElementById("campo-ate").hidden = true;
    montarFiltroRedes();
    montarExemplos();
    montarCamposIdeia();
    conferirIdeia();
    recalcular(false);
    aviso("Carregado: " + posts(nova.n) +
      (nova.descartadas ? " (" + num(nova.descartadas) + " linhas descartadas)" : ""));
  }

  function montarArquivo() {
    var input = document.getElementById("arquivo");
    document.getElementById("btn-carregar").addEventListener("click", function () {
      input.click();
    });
    input.addEventListener("change", function () {
      processarArquivo(input.files[0]);
      input.value = "";
    });

    ["dragenter", "dragover"].forEach(function (ev) {
      document.addEventListener(ev, function (e) {
        e.preventDefault();
        document.body.setAttribute("data-arrastando", "sim");
      });
    });
    ["dragleave", "drop"].forEach(function (ev) {
      document.addEventListener(ev, function (e) {
        e.preventDefault();
        if (ev === "drop" && e.dataTransfer && e.dataTransfer.files.length) {
          processarArquivo(e.dataTransfer.files[0]);
        }
        document.body.removeAttribute("data-arrastando");
      });
    });
  }

  // ---------------------------------------------------------------- início

  function iniciar() {
    var compacto = JSON.parse(document.getElementById("dados-embutidos").textContent);
    estado.base = ENG.montarBase(compacto);
    // "base do desafio" vem do build_tool.py; na tela, sem jargão
    estado.nomeDados = compacto.nome === "base do desafio"
      ? "exemplo do desafio" : (compacto.nome || "exemplo do desafio");
    estado.plataformas = estado.base.platRotulos.slice();

    montarTema();
    montarAbas();
    montarFiltroPeriodo();
    ligarMenu("f-redes", "painel-redes");
    ligarMenu("f-ajustes", "painel-ajustes");
    ligarMenu("f-tema", "painel-tema");
    montarFiltroRedes();
    montarAjustes();
    montarArquivo();
    montarComoUsar();
    montarPlanejar();
    recalcular(false);

    document.addEventListener("click", function () {
      fecharMenus(null);
      fecharBaloes();
    });
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape") { fecharMenus(null); fecharBaloes(); }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciar);
  } else {
    iniciar();
  }
})();
