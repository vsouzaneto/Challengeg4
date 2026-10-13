/* Decisor de Campanha - motor estatistico.
   Funcoes puras: nao usa window nem document. Roda igual no navegador e no Node. */
var ENGINE = (function () {
  "use strict";

  var COLS_OBRIGATORIAS = ["post_date", "platform", "content_type", "content_category",
    "follower_count", "is_sponsored", "views", "likes", "shares", "comments_count"];
  var COLS_PUBLICO = ["audience_age_distribution", "audience_gender_distribution", "audience_location"];
  // opcionais da OS-09 parte 1; cada uma entra se estiver no arquivo
  var COLS_EXTRA = ["clicks", "conversions", "cost"];

  var FAIXA_LIMITES = [50000, 100000, 500000, 1000000, Infinity];
  var FAIXA_LABELS = ["até 50K", "50–100K", "100–500K", "500K–1M", "acima de 1M"];

  var METRICAS = ["taxa", "interacoes", "views"];
  var MIN_N_SEGMENTO = 100;   // regra 1 do veredito
  var MIN_N_PAR = 100;        // pares so entram no bloco com n >= 100
  var MIN_ESTRATO = 30;       // patrocinados e organicos por estrato
  var MIN_AB = 30;            // piso de posts por versao num teste A/B
  var Z_EQUIV = 1.645;        // IC de equivalencia, 90%, sem correcao
  var DIA_MS = 86400000;

  // ---------------------------------------------------------------- numerico

  /* Quantil da normal padrao (Acklam). Erro < 1.15e-9. */
  function qnorm(p) {
    var a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
      1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00];
    var b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
      6.680131188771972e+01, -1.328068155288572e+01];
    var c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
      -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00];
    var d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
      3.754408661907416e+00];
    var pl = 0.02425, q, r, x;
    if (p <= 0) return -Infinity;
    if (p >= 1) return Infinity;
    if (p < pl) {
      q = Math.sqrt(-2 * Math.log(p));
      return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) /
        ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1);
    }
    if (p > 1 - pl) {
      q = Math.sqrt(-2 * Math.log(1 - p));
      return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) /
        ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1);
    }
    q = p - 0.5;
    r = q * q;
    x = (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q /
      (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1);
    return x;
  }

  function mediaDe(vals, pos) {
    var s = 0, i;
    for (i = 0; i < pos.length; i++) s += vals[pos[i]];
    return s / pos.length;
  }

  /* Desvio padrao amostral (n-1). */
  function dpDe(vals, pos, media) {
    var n = pos.length, s = 0, i, dv;
    if (n < 2) return 0;
    for (i = 0; i < n; i++) { dv = vals[pos[i]] - media; s += dv * dv; }
    return Math.sqrt(s / (n - 1));
  }

  function correlacao(x, y) {
    var n = x.length, i, sx = 0, sy = 0, mx, my, cxy = 0, cxx = 0, cyy = 0, dx, dy;
    for (i = 0; i < n; i++) { sx += x[i]; sy += y[i]; }
    mx = sx / n; my = sy / n;
    for (i = 0; i < n; i++) {
      dx = x[i] - mx; dy = y[i] - my;
      cxy += dx * dy; cxx += dx * dx; cyy += dy * dy;
    }
    if (cxx === 0 || cyy === 0) return 0;
    return cxy / Math.sqrt(cxx * cyy);
  }

  function mediana(arr) {
    var a = Array.prototype.slice.call(arr).sort(function (p, q) { return p - q; });
    var n = a.length, h = n >> 1;
    if (n === 0) return NaN;
    return n % 2 ? a[h] : (a[h - 1] + a[h]) / 2;
  }

  // ---------------------------------------------------------------- leitura

  function normalizaBool(v) {
    var s = String(v == null ? "" : v).trim().toLowerCase();
    if (s === "true" || s === "1" || s === "sim" || s === "yes") return 1;
    if (s === "false" || s === "0" || s === "nao" || s === "não" || s === "no") return 0;
    return null;
  }

  /* Aceita M/D/AA HH:MM AM/PM (formato da base) e AAAA-MM-DD, com ou sem hora. */
  function parseData(v) {
    if (v == null) return NaN;
    var s = String(v).trim(), mm;
    mm = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{2}|\d{4})(?:[ ,]+(\d{1,2}):(\d{2})(?::(\d{2}))?\s*([AaPp])\.?[Mm]\.?)?$/);
    if (mm) {
      var ano = +mm[3];
      if (ano < 100) ano += ano < 70 ? 2000 : 1900;
      var hora = mm[4] ? +mm[4] : 0;
      if (mm[7]) {
        var pm = mm[7].toLowerCase() === "p";
        if (hora === 12) hora = pm ? 12 : 0; else if (pm) hora += 12;
      }
      return Date.UTC(ano, +mm[1] - 1, +mm[2], hora, mm[5] ? +mm[5] : 0, mm[6] ? +mm[6] : 0);
    }
    mm = s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})(?:[T ](\d{1,2}):(\d{2})(?::(\d{2}))?)?/);
    if (mm) {
      return Date.UTC(+mm[1], +mm[2] - 1, +mm[3], mm[4] ? +mm[4] : 0,
        mm[5] ? +mm[5] : 0, mm[6] ? +mm[6] : 0);
    }
    return NaN;
  }

  function faixaDe(seguidores) {
    for (var i = 0; i < FAIXA_LIMITES.length; i++) {
      if (seguidores <= FAIXA_LIMITES[i]) return i;
    }
    return FAIXA_LIMITES.length - 1;
  }

  /* Transforma um vetor de strings em codigos inteiros + rotulos ordenados. */
  function codificar(valores) {
    var rotulos = [], mapa = Object.create(null), i, v;
    for (i = 0; i < valores.length; i++) {
      v = String(valores[i] == null ? "" : valores[i]).trim();
      if (!(v in mapa)) { mapa[v] = 1; rotulos.push(v); }
    }
    rotulos.sort();
    var ordem = Object.create(null);
    for (i = 0; i < rotulos.length; i++) ordem[rotulos[i]] = i;
    var cod = new Int32Array(valores.length);
    for (i = 0; i < valores.length; i++) {
      cod[i] = ordem[String(valores[i] == null ? "" : valores[i]).trim()];
    }
    return { cod: cod, rotulos: rotulos };
  }

  /* Monta a base a partir de linhas de objeto (upload via PapaParse). */
  function carregarLinhas(linhas) {
    var presentes = linhas.length ? Object.keys(linhas[0]) : [];
    var faltando = COLS_OBRIGATORIAS.filter(function (c) { return presentes.indexOf(c) < 0; });
    if (faltando.length) return { erro: "colunas", faltando: faltando };

    var temPublico = COLS_PUBLICO.every(function (c) { return presentes.indexOf(c) >= 0; });
    var brutas = { platform: [], content_type: [], content_category: [] };
    if (temPublico) COLS_PUBLICO.forEach(function (c) { brutas[c] = []; });

    var extras = Object.create(null), temExtra = [];
    COLS_EXTRA.forEach(function (c) {
      if (presentes.indexOf(c) >= 0) { temExtra.push(c); extras[c] = []; }
    });

    var n = 0, i, L, dt, sp, descartadas = 0;
    var data = [], seg = [], pat = [], views = [], likes = [], shares = [], coment = [];
    for (i = 0; i < linhas.length; i++) {
      L = linhas[i];
      dt = parseData(L.post_date);
      sp = normalizaBool(L.is_sponsored);
      var vw = Number(L.views), lk = Number(L.likes), sh = Number(L.shares),
        cm = Number(L.comments_count), fc = Number(L.follower_count);
      if (!isFinite(dt) || sp === null || !isFinite(vw) || vw <= 0 ||
        !isFinite(lk) || !isFinite(sh) || !isFinite(cm) || !isFinite(fc)) {
        descartadas++;
        continue;
      }
      data.push(dt); seg.push(fc); pat.push(sp);
      views.push(vw); likes.push(lk); shares.push(sh); coment.push(cm);
      brutas.platform.push(L.platform);
      brutas.content_type.push(L.content_type);
      brutas.content_category.push(L.content_category);
      if (temPublico) COLS_PUBLICO.forEach(function (c) { brutas[c].push(L[c]); });
      // coluna opcional em branco conta como zero
      for (var e = 0; e < temExtra.length; e++) {
        var xv = Number(L[temExtra[e]]);
        extras[temExtra[e]].push(isFinite(xv) ? xv : 0);
      }
      n++;
    }
    if (!n) return { erro: "vazio" };

    var compacto = {
      n: n,
      data: data, seg: seg, pat: pat,
      views: views, likes: likes, shares: shares, coment: coment,
      plat: codificar(brutas.platform),
      tipo: codificar(brutas.content_type),
      cat: codificar(brutas.content_category)
    };
    if (temPublico) {
      compacto.idade = codificar(brutas.audience_age_distribution);
      compacto.genero = codificar(brutas.audience_gender_distribution);
      compacto.pais = codificar(brutas.audience_location);
    }
    temExtra.forEach(function (c) { compacto[c] = extras[c]; });
    var base = montarBase(compacto);
    base.descartadas = descartadas;
    return base;
  }

  /* Monta a base a partir do formato compacto (dados embutidos pelo build_tool.py
     ou o resultado de carregarLinhas). */
  function montarBase(c) {
    var n = c.n, i;
    var base = {
      n: n,
      data: Float64Array.from(c.data),
      seg: Float64Array.from(c.seg),
      pat: Uint8Array.from(c.pat),
      views: Float64Array.from(c.views),
      likes: Float64Array.from(c.likes),
      shares: Float64Array.from(c.shares),
      coment: Float64Array.from(c.coment),
      interacoes: new Float64Array(n),
      taxa: new Float64Array(n),
      faixa: new Int32Array(n),
      faixaRotulos: FAIXA_LABELS,
      plat: Int32Array.from(c.plat.cod),
      platRotulos: c.plat.rotulos,
      tipo: Int32Array.from(c.tipo.cod),
      tipoRotulos: c.tipo.rotulos,
      cat: Int32Array.from(c.cat.cod),
      catRotulos: c.cat.rotulos,
      temPublico: !!c.idade
    };
    if (base.temPublico) {
      base.idade = Int32Array.from(c.idade.cod); base.idadeRotulos = c.idade.rotulos;
      base.genero = Int32Array.from(c.genero.cod); base.generoRotulos = c.genero.rotulos;
      base.pais = Int32Array.from(c.pais.cod); base.paisRotulos = c.pais.rotulos;
    }
    var dmin = Infinity, dmax = -Infinity;
    for (i = 0; i < n; i++) {
      base.interacoes[i] = base.likes[i] + base.shares[i] + base.coment[i];
      base.taxa[i] = base.interacoes[i] / base.views[i];
      base.faixa[i] = faixaDe(base.seg[i]);
      if (base.data[i] < dmin) dmin = base.data[i];
      if (base.data[i] > dmax) dmax = base.data[i];
    }
    base.dataMin = dmin;
    base.dataMax = dmax;
    anexarExtras(base, c);
    return base;
  }

  /* OS-09 parte 1: clicks, conversions e cost, se o arquivo tiver.
     conversions traz a metrica taxaConv = conversions / views, avaliada pelo
     mesmo motor das outras. Coluna toda zerada nao da para avaliar. */
  function anexarExtras(base, c) {
    var n = base.n, i, soma = 0;
    base.temClicks = !!c.clicks;
    base.temConversoes = !!c.conversions;
    base.temCusto = !!c.cost;
    if (base.temClicks) base.clicks = Float64Array.from(c.clicks);
    if (base.temCusto) base.cost = Float64Array.from(c.cost);
    if (base.temConversoes) {
      base.conversions = Float64Array.from(c.conversions);
      base.taxaConv = new Float64Array(n);
      for (i = 0; i < n; i++) {
        base.taxaConv[i] = base.conversions[i] / base.views[i];
        soma += base.conversions[i];
      }
      if (!(soma > 0)) base.temConversoes = false;
    }
    base.metricas = base.temConversoes ? METRICAS.concat(["taxaConv"]) : METRICAS.slice();
    return base;
  }

  // ---------------------------------------------------------------- veredito

  /* Regra do veredito, na ordem da OS. Recebe o erro padrao ja calculado (OS-09 0.1).
     dpRecorte = desvio padrao do indice no recorte, usado so no "faltam posts". */
  function veredito(lift, ep, n, m, k, dpRecorte) {
    var z = qnorm(1 - 0.05 / (2 * k));
    var dp = dpRecorte == null ? NaN : dpRecorte;
    var r = {
      lift: lift, dp: dp, n: n, ep: ep, z: z, k: k,
      decLo: lift - z * ep, decHi: lift + z * ep,
      eqLo: lift - Z_EQUIV * ep, eqHi: lift + Z_EQUIV * ep
    };
    if (n < MIN_N_SEGMENTO) {
      r.tipo = "inconclusivo"; r.motivo = "poucos posts"; r.faltam = null;
      return r;
    }
    if (r.decLo > 1 && lift >= 1 + m) { r.tipo = "funciona"; return r; }
    if (r.decHi < 1 && lift <= 1 - m) { r.tipo = "nao_funciona"; return r; }
    if (r.eqLo >= 1 - m && r.eqHi <= 1 + m) { r.tipo = "sem_efeito"; return r; }
    r.tipo = "inconclusivo";
    r.motivo = "faltam posts";
    var nNec = 2 * Math.pow((1.96 + 0.84) * dp / m, 2);
    r.faltam = Math.max(0, Math.ceil(nNec - n));
    r.nNecessario = nNec;
    return r;
  }

  // ---------------------------------------------------------------- analise

  function filtrar(base, opt) {
    var i, pos = [], de = opt.de, ate = opt.ate, plats = opt.plataformas;
    var usaPlat = plats && plats.length !== base.platRotulos.length;
    var ok = null;
    if (usaPlat) {
      ok = new Uint8Array(base.platRotulos.length);
      for (i = 0; i < plats.length; i++) {
        var j = base.platRotulos.indexOf(plats[i]);
        if (j >= 0) ok[j] = 1;
      }
    }
    for (i = 0; i < base.n; i++) {
      if (de != null && base.data[i] < de) continue;
      if (ate != null && base.data[i] > ate) continue;
      if (ok && !ok[base.plat[i]]) continue;
      pos.push(i);
    }
    return Int32Array.from(pos);
  }

  /* Janela dos "ultimos X dias", contada a partir da data mais recente da base. */
  function janelaUltimosDias(base, dias) {
    var fim = base.dataMax;
    return { de: fim - (dias - 1) * DIA_MS, ate: fim };
  }

  /* Indices por post, calculados sobre os dados ja filtrados.
     normal: valor / media da metrica na plataforma do post.
     geral: valor / media geral do recorte (usado para avaliar a propria plataforma). */
  function montarIndices(base, pos, metricas) {
    var mets = metricas || base.metricas || METRICAS;
    var n = pos.length, nPlat = base.platRotulos.length, i, p, mi, met;
    var out = { normal: {}, geral: {}, mediaPlat: {}, mediaGeral: {}, metricas: mets };
    for (mi = 0; mi < mets.length; mi++) {
      met = mets[mi];
      var vals = base[met];
      var soma = new Float64Array(nPlat), cont = new Float64Array(nPlat), total = 0;
      for (i = 0; i < n; i++) { p = base.plat[pos[i]]; soma[p] += vals[pos[i]]; cont[p]++; total += vals[pos[i]]; }
      var mediaP = new Float64Array(nPlat);
      for (p = 0; p < nPlat; p++) mediaP[p] = cont[p] ? soma[p] / cont[p] : NaN;
      var mg = total / n;
      var idxN = new Float64Array(n), idxG = new Float64Array(n);
      for (i = 0; i < n; i++) {
        // plataforma sem nenhum valor na metrica cai na media geral do recorte
        var mp = mediaP[base.plat[pos[i]]];
        idxN[i] = mp > 0 ? vals[pos[i]] / mp : (mg > 0 ? vals[pos[i]] / mg : 0);
        idxG[i] = mg > 0 ? vals[pos[i]] / mg : 0;
      }
      out.normal[met] = idxN;
      out.geral[met] = idxG;
      out.mediaPlat[met] = mediaP;
      out.mediaGeral[met] = mg;
    }
    return out;
  }

  /* Lista de variaveis de um bloco, com os codigos ja reindexados para o recorte. */
  function varsDoBloco(base, pos, nomes) {
    return nomes.map(function (nome) {
      var cod = base[nome.campo], n = pos.length, i;
      var local = new Int32Array(n);
      for (i = 0; i < n; i++) local[i] = cod[pos[i]];
      return { id: nome.id, campo: nome.campo, rotulos: base[nome.rotulos], cod: local };
    });
  }

  function agrupar(cod, k) {
    var grupos = [], i;
    for (i = 0; i < k; i++) grupos.push([]);
    for (i = 0; i < cod.length; i++) grupos[cod[i]].push(i);
    return grupos;
  }

  /* Enumera os segmentos de um bloco: cada valor de cada variavel + os pares entre elas. */
  function segmentosDoBloco(vars) {
    var segs = [], a, b, i, j, g, grupos;
    for (a = 0; a < vars.length; a++) {
      grupos = agrupar(vars[a].cod, vars[a].rotulos.length);
      for (g = 0; g < grupos.length; g++) {
        if (!grupos[g].length) continue;
        segs.push({
          vars: [vars[a].id], valores: [vars[a].rotulos[g]],
          pos: Int32Array.from(grupos[g])
        });
      }
    }
    for (a = 0; a < vars.length; a++) {
      for (b = a + 1; b < vars.length; b++) {
        var kb = vars[b].rotulos.length;
        var mapa = Object.create(null);
        for (i = 0; i < vars[a].cod.length; i++) {
          var key = vars[a].cod[i] * kb + vars[b].cod[i];
          if (!mapa[key]) mapa[key] = [];
          mapa[key].push(i);
        }
        var chaves = Object.keys(mapa).map(Number).sort(function (p, q) { return p - q; });
        for (j = 0; j < chaves.length; j++) {
          var lista = mapa[chaves[j]];
          if (lista.length < MIN_N_PAR) continue;
          segs.push({
            vars: [vars[a].id, vars[b].id],
            valores: [vars[a].rotulos[Math.floor(chaves[j] / kb)], vars[b].rotulos[chaves[j] % kb]],
            pos: Int32Array.from(lista)
          });
        }
      }
    }
    return segs;
  }

  /* Media, dp e somas de um vetor de indices do recorte inteiro. */
  function totaisIndice(vals) {
    var n = vals.length, i, soma = 0, soma2 = 0, media, acc = 0, dv;
    for (i = 0; i < n; i++) { soma += vals[i]; soma2 += vals[i] * vals[i]; }
    media = soma / n;
    for (i = 0; i < n; i++) { dv = vals[i] - media; acc += dv * dv; }
    return {
      n: n, soma: soma, soma2: soma2, media: media,
      dp: n > 1 ? Math.sqrt(acc / (n - 1)) : 0
    };
  }

  /* OS-09 0.1: compara o segmento com o resto do recorte, nao com a media geral.
     d = media em S - media fora de S; lift = 1 + d; ep = sqrt(dpS²/nS + dpR²/nR).
     As somas do resto saem dos totais do recorte, sem varrer o complemento. */
  function liftContraResto(vals, pos, tot) {
    var n = pos.length, i, v, soma = 0, soma2 = 0, media, acc = 0, dv;
    for (i = 0; i < n; i++) { v = vals[pos[i]]; soma += v; soma2 += v * v; }
    media = soma / n;
    for (i = 0; i < n; i++) { dv = vals[pos[i]] - media; acc += dv * dv; }
    var dp = n > 1 ? Math.sqrt(acc / (n - 1)) : 0;
    var nR = tot.n - n;
    if (nR < 1) {
      return {
        n: n, media: media, dp: dp, nResto: nR, mediaResto: NaN, dpResto: NaN,
        d: NaN, lift: NaN, ep: NaN, semResto: true
      };
    }
    var mediaR = (tot.soma - soma) / nR;
    var ssR = (tot.soma2 - soma2) - nR * mediaR * mediaR;
    var dpR = nR > 1 ? Math.sqrt(Math.max(0, ssR) / (nR - 1)) : 0;
    var d = media - mediaR;
    return {
      n: n, media: media, dp: dp, nResto: nR, mediaResto: mediaR, dpResto: dpR,
      d: d, lift: 1 + d, ep: Math.sqrt(dp * dp / n + dpR * dpR / nR), semResto: false
    };
  }

  /* Veredito de um segmento contra o resto do recorte. */
  function vereditoSegmento(vals, pos, tot, m, k) {
    var c = liftContraResto(vals, pos, tot);
    if (c.semResto) {
      return {
        tipo: "inconclusivo", motivo: "sem comparação", lift: NaN, ep: NaN,
        n: c.n, dp: tot.dp, faltam: null, comparacao: c
      };
    }
    var v = veredito(c.lift, c.ep, c.n, m, k, tot.dp);
    v.comparacao = c;
    return v;
  }

  /* Indice usado para um segmento: a propria plataforma vai contra a media geral. */
  function indiceDoSegmento(idx, met, seg) {
    var usaGeral = seg.vars.length === 1 && seg.vars[0] === "plataforma";
    return usaGeral ? { vals: idx.geral[met], geral: true } : { vals: idx.normal[met], geral: false };
  }

  /* Avalia um bloco: k = total de segmentos do bloco (correcao de Bonferroni). */
  function avaliarBloco(segs, idx, m, metricas) {
    var mets = metricas || METRICAS;
    var k = Math.max(1, segs.length), i, mi, met, s, out = [];
    var tot = { normal: {}, geral: {} };
    for (mi = 0; mi < mets.length; mi++) {
      met = mets[mi];
      tot.normal[met] = totaisIndice(idx.normal[met]);
      tot.geral[met] = totaisIndice(idx.geral[met]);
    }
    for (i = 0; i < segs.length; i++) {
      s = segs[i];
      var linha = { vars: s.vars, valores: s.valores, n: s.pos.length, metricas: {} };
      for (mi = 0; mi < mets.length; mi++) {
        met = mets[mi];
        var alvo = indiceDoSegmento(idx, met, s);
        var t = alvo.geral ? tot.geral[met] : tot.normal[met];
        linha.metricas[met] = vereditoSegmento(alvo.vals, s.pos, t, m, k);
      }
      out.push(linha);
    }
    return { k: k, segmentos: out, totais: tot };
  }

  /* Patrocinio: comparacao estratificada (platform x categoria x formato x faixa). */
  function avaliarPatrocinio(base, pos, idx, m, metricas) {
    var mets = metricas || METRICAS;
    var i, mapa = Object.create(null), nCat = base.catRotulos.length,
      nTipo = base.tipoRotulos.length, nFx = FAIXA_LABELS.length;
    for (i = 0; i < pos.length; i++) {
      var r = pos[i];
      var key = ((base.plat[r] * nCat + base.cat[r]) * nTipo + base.tipo[r]) * nFx + base.faixa[r];
      var e = mapa[key];
      if (!e) { e = mapa[key] = { p: [], o: [] }; }
      (base.pat[r] ? e.p : e.o).push(i);
    }
    var chaves = Object.keys(mapa);
    var estratos = [], existentes = chaves.length;
    for (i = 0; i < chaves.length; i++) {
      var est = mapa[chaves[i]];
      if (est.p.length >= MIN_ESTRATO && est.o.length >= MIN_ESTRATO) {
        estratos.push({ p: Int32Array.from(est.p), o: Int32Array.from(est.o) });
      }
    }
    var res = {
      estratosExistentes: existentes, estratosUsados: estratos.length,
      postsUsados: 0, nPatrocinado: 0, nOrganico: 0, metricas: {}
    };
    if (!estratos.length) {
      mets.forEach(function (met) {
        res.metricas[met] = { tipo: "inconclusivo", motivo: "poucos posts", lift: NaN, n: 0, efeito: NaN };
      });
      return res;
    }
    var totalUsado = 0;
    for (i = 0; i < estratos.length; i++) totalUsado += estratos[i].p.length + estratos[i].o.length;
    res.postsUsados = totalUsado;
    for (i = 0; i < estratos.length; i++) {
      res.nPatrocinado += estratos[i].p.length;
      res.nOrganico += estratos[i].o.length;
    }

    mets.forEach(function (met) {
      var vals = idx.normal[met], somaD = 0, somaVar = 0, j;
      for (j = 0; j < estratos.length; j++) {
        var E = estratos[j];
        var w = (E.p.length + E.o.length) / totalUsado;
        var mp = mediaDe(vals, E.p), mo = mediaDe(vals, E.o);
        var dpp = dpDe(vals, E.p, mp), dpo = dpDe(vals, E.o, mo);
        somaD += w * (mp - mo);
        somaVar += w * w * (dpp * dpp / E.p.length + dpo * dpo / E.o.length);
      }
      var efeito = 1 + somaD;
      var ep = Math.sqrt(somaVar);
      // mesma regra de veredito, sem correcao (k = 1)
      var v = veredito(efeito, ep, totalUsado, m, 1, totaisIndice(vals).dp);
      v.efeito = efeito;
      res.metricas[met] = v;
    });
    return res;
  }

  /* Saude da base: 5 testes. */
  function saudeDaBase(base, pos) {
    var n = pos.length, i;
    var lf = new Float64Array(n), lv = new Float64Array(n),
      lk = new Float64Array(n), vw = new Float64Array(n), it = new Float64Array(n);
    for (i = 0; i < n; i++) {
      lf[i] = Math.log(base.seg[pos[i]]);
      lv[i] = Math.log(base.views[pos[i]]);
      lk[i] = base.likes[pos[i]];
      vw[i] = base.views[pos[i]];
      it[i] = base.interacoes[pos[i]];
    }
    var corrSegView = n > 1 ? correlacao(lf, lv) : NaN;
    var corrLikeView = n > 1 ? correlacao(lk, vw) : NaN;
    var mediaV = 0;
    for (i = 0; i < n; i++) mediaV += vw[i];
    mediaV /= n;
    var varV = 0;
    for (i = 0; i < n; i++) { var d = vw[i] - mediaV; varV += d * d; }
    varV = n > 1 ? varV / (n - 1) : 0;
    var dispersao = mediaV ? varV / mediaV : 0;
    var medIt = mediana(it), fracos = 0;
    for (i = 0; i < n; i++) if (it[i] < 0.1 * medIt) fracos++;
    var pctFracos = 100 * fracos / n;

    var testes = [
      {
        id: "alcance_seguidores", nome: "Alcance acompanha seguidores",
        valor: corrSegView, alerta: !(corrSegView >= 0.3),
        texto: "Quem tem mais seguidores deveria ter mais alcance."
      },
      {
        id: "likes_alcance", nome: "Likes acompanham alcance",
        valor: corrLikeView, alerta: !(corrLikeView >= 0.3),
        texto: "Posts com mais alcance deveriam receber mais likes."
      },
      {
        id: "virais", nome: "Existem posts virais e fracassos",
        valor: dispersao, alerta: !(dispersao >= 10),
        texto: "O alcance varia pouco de um post para outro."
      },
      {
        id: "fracassos", nome: "Existem posts fracassados",
        valor: pctFracos, alerta: !(pctFracos >= 1),
        texto: "Quase nenhum post teve desempenho muito abaixo do normal."
      },
      {
        id: "volume", nome: "Volume mínimo", valor: n, alerta: n < 500,
        texto: "O recorte tem poucos posts para concluir algo."
      }
    ];
    return { testes: testes, alertas: testes.filter(function (t) { return t.alerta; }).length };
  }

  /* Numero de posts por versao num teste A/B para detectar um efeito de tamanho m.
     Piso de 30 posts por versao (OS-09 0.3). */
  function postsPorVersao(idxTaxa, m) {
    var n = idxTaxa.length, i, s = 0, media, dv, v = 0;
    for (i = 0; i < n; i++) s += idxTaxa[i];
    media = s / n;
    for (i = 0; i < n; i++) { dv = idxTaxa[i] - media; v += dv * dv; }
    var dp = n > 1 ? Math.sqrt(v / (n - 1)) : 0;
    var calculado = Math.ceil(Math.pow((1.96 + 0.84) * dp / m, 2));
    return { dp: dp, calculado: calculado, posts: Math.max(MIN_AB, calculado) };
  }

  // ------------------------------------------------- OS-09: colunas novas

  /* Metricas avaliaveis neste recorte: taxaConv sai se nao houver conversao nele. */
  function metricasDoRecorte(base, pos) {
    var mets = base.metricas || METRICAS;
    if (mets.indexOf("taxaConv") < 0) return mets;
    var soma = 0, i;
    for (i = 0; i < pos.length; i++) soma += base.conversions[pos[i]];
    return soma > 0 ? mets : METRICAS.slice();
  }

  /* Quantil por interpolacao linear, sobre um vetor ja ordenado. */
  function quantil(ordenado, q) {
    var n = ordenado.length;
    if (!n) return NaN;
    var h = (n - 1) * q, lo = Math.floor(h), hi = Math.ceil(h);
    return ordenado[lo] + (h - lo) * (ordenado[hi] - ordenado[lo]);
  }

  function resumoQuantis(vals) {
    var a = vals.slice().sort(function (p, q) { return p - q; });
    return { n: a.length, mediana: quantil(a, 0.5), p10: quantil(a, 0.10), p90: quantil(a, 0.90) };
  }

  /* OS-09 parte 1: custo por interacao e por conversao nos patrocinados.
     Mediana e faixa p10-p90, sem veredito. */
  function custosPatrocinio(base, pos) {
    if (!base.temCusto) return null;
    var porInteracao = [], porConversao = [], i, r, nPat = 0, somaCusto = 0;
    for (i = 0; i < pos.length; i++) {
      r = pos[i];
      if (!base.pat[r]) continue;
      nPat++;
      somaCusto += base.cost[r];
      if (base.interacoes[r] > 0) porInteracao.push(base.cost[r] / base.interacoes[r]);
      if (base.temConversoes && base.conversions[r] > 0) {
        porConversao.push(base.cost[r] / base.conversions[r]);
      }
    }
    return {
      nPatrocinado: nPat, custoTotal: somaCusto,
      porInteracao: porInteracao.length ? resumoQuantis(porInteracao) : null,
      porConversao: porConversao.length ? resumoQuantis(porConversao) : null
    };
  }

  // ------------------------------------------------- OS-09 3a: testar uma ideia

  var CAMPOS_IDEIA = [
    { id: "plataforma", campo: "plat", rotulos: "platRotulos" },
    { id: "formato", campo: "tipo", rotulos: "tipoRotulos" },
    { id: "categoria", campo: "cat", rotulos: "catRotulos" },
    { id: "faixa", campo: "faixa", rotulos: "faixaRotulos" },
    { id: "idade", campo: "idade", rotulos: "idadeRotulos" },
    { id: "genero", campo: "genero", rotulos: "generoRotulos" },
    { id: "pais", campo: "pais", rotulos: "paisRotulos" }
  ];

  /* Traduz a ideia (rotulos escolhidos na tela) em codigos da base. */
  function codigosDaIdeia(base, ideia) {
    var out = [], i, c, v;
    for (i = 0; i < CAMPOS_IDEIA.length; i++) {
      c = CAMPOS_IDEIA[i];
      v = ideia[c.id];
      if (v == null || v === "") continue;
      if (!base[c.rotulos]) continue;
      var cod = base[c.rotulos].indexOf(v);
      if (cod < 0) continue;
      out.push({ campo: c.campo, cod: cod });
    }
    return out;
  }

  function combinaIdeia(base, r, criterios, patrocinado) {
    var i;
    for (i = 0; i < criterios.length; i++) {
      if (base[criterios[i].campo][r] !== criterios[i].cod) return false;
    }
    if (patrocinado === "sim" && !base.pat[r]) return false;
    if (patrocinado === "nao" && base.pat[r]) return false;
    return true;
  }

  /* OS-09 3a: os posts que combinam com a ideia contra o resto do recorte, k = 1.
     A ideia que so escolhe plataforma usa o indice geral, como no bloco de
     desempenho; qualquer outra combinacao usa o indice por plataforma. */
  function avaliarIdeia(base, opcoes, ideia) {
    var opt = opcoes || {};
    var m = opt.margem == null ? 0.10 : opt.margem;
    var pos = filtrar(base, opt);
    if (!pos.length) return { vazio: true, n: 0 };

    var mets = metricasDoRecorte(base, pos);
    var idx = montarIndices(base, pos, mets);
    var criterios = codigosDaIdeia(base, ideia);
    var patrocinado = ideia.patrocinado === "sim" || ideia.patrocinado === "nao"
      ? ideia.patrocinado : "";
    var dentro = [], i;
    for (i = 0; i < pos.length; i++) {
      if (combinaIdeia(base, pos[i], criterios, patrocinado)) dentro.push(i);
    }
    var soPlataforma = criterios.length === 1 && criterios[0].campo === "plat" && !patrocinado;

    var res = {
      n: dentro.length, nRecorte: pos.length, metricas: {}, metricasUsadas: mets,
      criterios: criterios.length + (patrocinado ? 1 : 0), patrocinada: patrocinado === "sim"
    };
    if (!dentro.length || dentro.length === pos.length) {
      res.semComparacao = true;
      return res;
    }
    var posDentro = Int32Array.from(dentro);
    // semanas do recorte, para transformar posts em prazo
    var dias = (maximo(base.data, pos) - minimo(base.data, pos)) / DIA_MS + 1;
    var semanas = Math.max(1, dias / 7);
    res.mediaSemanal = dentro.length / semanas;

    mets.forEach(function (met) {
      var vals = soPlataforma ? idx.geral[met] : idx.normal[met];
      var tot = totaisIndice(vals);
      var v = vereditoSegmento(vals, posDentro, tot, m, 1);
      v.ab = postsPorVersao(vals, m);
      v.semanas = res.mediaSemanal > 0 ? v.ab.posts / res.mediaSemanal : Infinity;
      res.metricas[met] = v;
    });
    return res;
  }

  // ------------------------------------------------- OS-09 3b: simulador

  /* Media por post e IC 95% da media, no recorte filtrado. */
  function mediaIC(vals, pos) {
    var n = pos.length, media = mediaDe(vals, pos), dp = dpDe(vals, pos, media);
    var ep = n ? dp / Math.sqrt(n) : NaN;
    return { n: n, media: media, ep: ep, lo: media - 1.96 * ep, hi: media + 1.96 * ep };
  }

  /* OS-09 3b: alcance, interacoes, investimento e ganho do patrocinio no mes.
     ent: { postsOrganicos, postsPatrocinados, valorPorPatrocinado, custoPorOrganico }. */
  function simular(base, opcoes, ent) {
    var opt = opcoes || {};
    var m = opt.margem == null ? 0.10 : opt.margem;
    var pos = filtrar(base, opt);
    if (!pos.length) return { vazio: true };
    var mets = ["views", "interacoes"];
    var idx = montarIndices(base, pos, mets);
    var pat = avaliarPatrocinio(base, pos, idx, m, mets);

    var org = Math.max(0, ent.postsOrganicos || 0);
    var spo = Math.max(0, ent.postsPatrocinados || 0);
    var total = org + spo;
    var posOrg = [], i;
    for (i = 0; i < pos.length; i++) if (!base.pat[pos[i]]) posOrg.push(pos[i]);
    posOrg = Int32Array.from(posOrg);

    var res = {
      n: pos.length, postsOrganicos: org, postsPatrocinados: spo, postsTotal: total,
      investimentoPatrocinio: spo * (ent.valorPorPatrocinado || 0),
      investimentoOrganico: org * (ent.custoPorOrganico || 0),
      metricas: {}
    };
    res.investimentoTotal = res.investimentoPatrocinio + res.investimentoOrganico;

    mets.forEach(function (met) {
      var mi = mediaIC(base[met], pos);
      var mo = posOrg.length ? mediaDe(base[met], posOrg) : NaN;
      var vp = pat.metricas[met];
      var efeito = vp.efeito, ep = vp.ep;
      var dz = 1.96;
      var g = { valor: NaN, lo: NaN, hi: NaN, incluiZero: true };
      if (isFinite(efeito) && isFinite(ep) && isFinite(mo)) {
        g.valor = (efeito - 1) * mo * spo;
        g.lo = (efeito - 1 - dz * ep) * mo * spo;
        g.hi = (efeito - 1 + dz * ep) * mo * spo;
        if (g.lo > g.hi) { var t = g.lo; g.lo = g.hi; g.hi = t; }
        g.incluiZero = !(g.lo > 0 || g.hi < 0) || g.valor === 0;
      }
      res.metricas[met] = {
        mediaPorPost: mi, mediaOrganica: mo,
        total: total * mi.media, totalLo: total * mi.lo, totalHi: total * mi.hi,
        efeitoPatrocinio: efeito, epPatrocinio: ep, vereditoPatrocinio: vp.tipo, ganho: g
      };
    });

    var gi = res.metricas.interacoes.ganho;
    res.custoPorInteracaoAdicional = (isFinite(gi.valor) && gi.valor > 0 && !gi.incluiZero)
      ? res.investimentoPatrocinio / gi.valor : null;
    res.patrocinio = pat;
    return res;
  }

  var VARS_DESEMPENHO = [
    { id: "plataforma", campo: "plat", rotulos: "platRotulos" },
    { id: "formato", campo: "tipo", rotulos: "tipoRotulos" },
    { id: "categoria", campo: "cat", rotulos: "catRotulos" },
    { id: "faixa", campo: "faixa", rotulos: "faixaRotulos" }
  ];
  var VARS_PUBLICO = [
    { id: "idade", campo: "idade", rotulos: "idadeRotulos" },
    { id: "genero", campo: "genero", rotulos: "generoRotulos" },
    { id: "pais", campo: "pais", rotulos: "paisRotulos" }
  ];

  function analisar(base, opcoes) {
    var opt = opcoes || {};
    var m = opt.margem == null ? 0.10 : opt.margem;
    var pos = filtrar(base, opt);
    if (!pos.length) return { n: 0, margem: m, vazio: true };

    var mets = metricasDoRecorte(base, pos);
    var idx = montarIndices(base, pos, mets);
    var blocoDesempenho = avaliarBloco(segmentosDoBloco(varsDoBloco(base, pos, VARS_DESEMPENHO)), idx, m, mets);
    var blocoPublico = base.temPublico
      ? avaliarBloco(segmentosDoBloco(varsDoBloco(base, pos, VARS_PUBLICO)), idx, m, mets)
      : null;
    var patrocinio = avaliarPatrocinio(base, pos, idx, m, mets);

    return {
      n: pos.length,
      margem: m,
      metricas: mets,
      custos: custosPatrocinio(base, pos),
      dataMin: minimo(base.data, pos),
      dataMax: maximo(base.data, pos),
      desempenho: blocoDesempenho,
      publico: blocoPublico,
      patrocinio: patrocinio,
      saude: saudeDaBase(base, pos),
      ab: postsPorVersao(idx.normal.taxa, 0.20),
      indices: idx
    };
  }

  function minimo(vals, pos) {
    var r = Infinity, i;
    for (i = 0; i < pos.length; i++) if (vals[pos[i]] < r) r = vals[pos[i]];
    return r;
  }

  function maximo(vals, pos) {
    var r = -Infinity, i;
    for (i = 0; i < pos.length; i++) if (vals[pos[i]] > r) r = vals[pos[i]];
    return r;
  }

  return {
    COLS_OBRIGATORIAS: COLS_OBRIGATORIAS,
    COLS_PUBLICO: COLS_PUBLICO,
    COLS_EXTRA: COLS_EXTRA,
    FAIXA_LABELS: FAIXA_LABELS,
    METRICAS: METRICAS,
    DIA_MS: DIA_MS,
    qnorm: qnorm,
    parseData: parseData,
    normalizaBool: normalizaBool,
    faixaDe: faixaDe,
    codificar: codificar,
    carregarLinhas: carregarLinhas,
    montarBase: montarBase,
    veredito: veredito,
    filtrar: filtrar,
    janelaUltimosDias: janelaUltimosDias,
    montarIndices: montarIndices,
    totaisIndice: totaisIndice,
    liftContraResto: liftContraResto,
    vereditoSegmento: vereditoSegmento,
    segmentosDoBloco: segmentosDoBloco,
    varsDoBloco: varsDoBloco,
    avaliarBloco: avaliarBloco,
    avaliarPatrocinio: avaliarPatrocinio,
    saudeDaBase: saudeDaBase,
    postsPorVersao: postsPorVersao,
    metricasDoRecorte: metricasDoRecorte,
    quantil: quantil,
    custosPatrocinio: custosPatrocinio,
    avaliarIdeia: avaliarIdeia,
    mediaIC: mediaIC,
    simular: simular,
    analisar: analisar
  };
})();

if (typeof module !== "undefined" && module.exports) module.exports = ENGINE;
