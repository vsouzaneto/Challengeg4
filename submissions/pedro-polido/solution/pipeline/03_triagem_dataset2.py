"""Dataset 2 (IT Service Tickets, ~48 mil textos reais): onde a triagem perde tempo, classificador e política de automação.

Saídas (solution/app/data/):
  model.json      modelo exportado para rodar no navegador (vocabulário, idf, pesos) + regras da política
  simulador.json  predições do conjunto de teste, consumidas pelo simulador de automação
  operacao.json   diagnóstico operacional (volume, cadeias de e-mail, pedidos vazios, acerto por tipo de ticket)
  exemplos.json   tickets de teste para os botões de exemplo da triagem ao vivo
e process-log/auditoria-rotulos/candidatos.csv: divergências de alta confiança para revisão humana.

Uso: python 03_triagem_dataset2.py
"""
import re

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split

from common import IT_TICKETS_CSV, SEED, SUBMISSION, save_json

TARGET_AUTO = 0.97    # acerto mínimo exigido para rotear sem humano (decisão de negócio, ajustável no simulador)
TARGET_ASSIST = 0.90  # acerto mínimo das 2 sugestões mostradas ao atendente na faixa assistida
C = 5.0

DAYS = "monday|tuesday|wednesday|thursday|friday|saturday|sunday"
MONTHS = "january|february|march|april|may|june|july|august|september|october|november|december"
# Regras compartilhadas com o navegador (app/js/model.js lê daqui): uma única fonte de verdade.
POLICY = {
    # Cabeçalho "Sent: Tuesday, ..." preservado no pré-processamento: cada ocorrência = uma mensagem anterior na cadeia.
    "thread": rf"\bsent (?:{DAYS})\b",
    # Saúde, remuneração e desligamento. 'discipline' ficou de fora: no dataset é cargo ("discipline lead"), 2 mil vezes.
    "sensitive": r"\b(?:sick|illness|medical|hospital|surgery|doctor|maternity|paternity|pregnant|pregnancy|bereavement"
                 r"|funeral|death|died|accident|salary|salaries|payroll|termination|terminated|resignation|resigned"
                 r"|dismissal)\b",
    "urgent": r"\bimportance high\b|\burgent\w*|\basap\b|\bimmediately\b|\boutage\b|\bis down\b|\bnot working\b",
    "self_service": r"\bpassword\w*|\blocked\b|\bunlock\w*",
    # Palavras que não dizem nada sobre o pedido: saudação, cortesia, datas, assinatura.
    "generic_words": sorted(set(
        f"hi hello dear please pls thank thanks thx you regards kind best help possible sent re fw fwd am pm "
        f"ok okay good morning afternoon evening team colleagues hey greetings sincerely cheers wishes great day "
        f"can could would need needed want like let know us me my our we get also ext extension "
        f"engineer developer analyst lead senior junior manager officer specialist tester assistant consultant "
        f"head director coordinator administrator architect intern {DAYS.replace('|', ' ')} {MONTHS.replace('|', ' ')}"
        .split())),
    "min_content_words": 3,
    # Texto fora do padrão de treino (outro idioma, assunto novo): a confiança do modelo não vale nada ali. Um ticket
    # em português com 3 de 14 palavras conhecidas saiu com 100% de confiança antes desta regra. Nos tickets reais a
    # cobertura mediana é 100% e o percentil 1 é 88%; em português/espanhol fica entre 8% e 30%.
    "stopwords": sorted(ENGLISH_STOP_WORDS),
    "min_coverage": 0.5,
    "min_coverage_tokens": 3,
}
FLAG_BITS = {"sensitive": 1, "info_poor": 2, "thread": 4, "urgent": 8, "self_service": 16, "ood": 32}

# Descrição de cada fila em linguagem de atendente, escrita a partir dos termos de maior peso do modelo.
QUEUE_INFO = {
    "Access": "Contas, senhas, licenças e acesso a ferramentas (Confluence, Git, cartões de acesso)",
    "Administrative rights": "Instalar ou atualizar software que exige direito de administrador (Outlook, Windows)",
    "HR Support": "Entrada e saída de colaboradores, férias, licenças e apontamento de horas (Oracle)",
    "Hardware": "Notebook, monitor, telefone, salas de reunião, cabos e periféricos",
    "Internal Project": "Códigos de projeto, pipelines e configuração de projetos internos",
    "Miscellaneous": "Aprovações, grupos, troca de responsável (owner) e contratos",
    "Purchase": "Pedidos de compra (PO), recebimento e alocação de equipamentos",
    "Storage": "Pastas, mailboxes, cotas de armazenamento e permissões de compartilhamento",
}

generic = set(POLICY["generic_words"])


def add_flags(frame):
    """Sinais da política por ticket (espelhados em TriageModel.flags() no navegador)."""
    text = frame["Document"].str.lower()
    tokens = text.str.findall(r"\b\w\w+\b")
    frame = frame.assign(words=tokens.str.len(),
                         content_words=tokens.apply(lambda ts: sum(t not in generic and not t.isdigit() for t in ts)),
                         msgs=1 + text.str.count(POLICY["thread"]))
    for flag in ["sensitive", "urgent", "self_service"]:
        frame[flag] = text.str.contains(POLICY[flag], regex=True)
    frame["thread"] = frame["msgs"] >= 2
    frame["info_poor"] = frame["content_words"] < POLICY["min_content_words"]
    return frame


df = add_flags(pd.read_csv(IT_TICKETS_CSV))

# ---------------------------------------------------------------- classificador
train, test = train_test_split(df, test_size=0.2, stratify=df["Topic_group"], random_state=SEED)
vec = TfidfVectorizer(min_df=2, sublinear_tf=True)  # unigramas, token_pattern padrão \b\w\w+\b
Xtr = vec.fit_transform(train["Document"])
Xte = vec.transform(test["Document"])
clf = LogisticRegression(C=C, max_iter=3000)

skip = generic | set(POLICY["stopwords"])


def is_ood(doc):
    """Texto fora do padrão: menos de min_coverage das palavras de conteúdo estão no vocabulário do modelo."""
    content = [t for t in re.findall(r"\b\w\w+\b", doc.lower()) if t not in skip and not t.isdigit()]
    if len(content) < POLICY["min_coverage_tokens"]:
        return False
    known = sum(t in vec.vocabulary_ for t in content)
    return known / len(content) < POLICY["min_coverage"]


test = test.assign(ood=test["Document"].map(is_ood))

# Limiares escolhidos com previsões fora-da-dobra do TREINO; o teste só é usado para reportar.
cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
oof = cross_val_predict(clf, Xtr, train["Topic_group"], cv=cv, method="predict_proba")
clf.fit(Xtr, train["Topic_group"])
classes = list(clf.classes_)
y_tr = train["Topic_group"].map(classes.index).values


def expected_calibration_error(conf, ok, bins=10):
    """Distância média entre a confiança declarada e o acerto real, em 10 faixas: 0 = calibração perfeita."""
    idx = np.minimum((conf * bins).astype(int), bins - 1)
    return sum((idx == b).mean() * abs(conf[idx == b].mean() - ok[idx == b].mean()) for b in range(bins) if (idx == b).any())


def lanes_curve(proba, y):
    conf = proba.max(1)
    order = np.argsort(-proba, 1)
    ok1 = order[:, 0] == y
    ok2 = ok1 | (order[:, 1] == y)
    return conf, ok1, ok2


conf_oof, ok1_oof, ok2_oof = lanes_curve(oof, y_tr)
grid = np.round(np.arange(0.20, 0.996, 0.005), 3)
tau_auto = next(t for t in grid if ok1_oof[conf_oof >= t].mean() >= TARGET_AUTO)
# Faixa assistida: critério LOCAL (tickets com confiança em [t, t + 0,1)), não cumulativo. O cumulativo esconde a cauda:
# a média da faixa inteira passa de 90% mesmo quando os tickets perto de 0,3 têm só ~78% de top-2.
tau_assist = next(t for t in grid if t < tau_auto and ok2_oof[(conf_oof >= t) & (conf_oof < t + 0.1)].mean() >= TARGET_ASSIST)
print(f"Limiares (fora-da-dobra no treino): automático >= {tau_auto} | assistido >= {tau_assist}")

proba = clf.predict_proba(Xte)
y_te = test["Topic_group"].map(classes.index).values
conf, ok1, ok2 = lanes_curve(proba, y_te)
pred = proba.argmax(1)
second = np.argsort(-proba, 1)[:, 1]
print(f"Teste: acerto {ok1.mean():.3f} | top-2 {ok2.mean():.3f}")



def decide_lane(conf, info_poor, ood, sensitive):
    """Política completa, na mesma ordem de TriageModel.lane() no navegador."""
    if info_poor:
        return "detalhes"
    if ood or sensitive:
        return "humano"
    if conf >= tau_auto:
        return "auto"
    return "assistido" if conf >= tau_assist else "humano"


lane = np.array([decide_lane(*a) for a in zip(conf, test["info_poor"], test["ood"], test["sensitive"])])
print(f"  fora do padrão (cobertura < {POLICY['min_coverage']:.0%}): {test['ood'].sum()} ticket(s) de teste")
for name in ["auto", "assistido", "humano", "detalhes"]:
    m = lane == name
    print(f"  {name:10s} {m.mean():6.1%} dos tickets | acerto top-1 {ok1[m].mean():.1%} | top-2 {ok2[m].mean():.1%}")

local = []
for lo in np.round(np.arange(0.2, 1.0, 0.1), 1):
    m = (conf >= lo) & (conf < lo + 0.1)
    local.append({"faixa": f"{lo:.1f}–{lo + 0.1:.1f}", "n": int(m.sum()), "top1": ok1[m].mean(), "top2": ok2[m].mean()})
curve = []
for t in np.round(np.arange(0.40, 0.996, 0.01), 2):
    m = conf >= t
    curve.append({"limiar": t, "cobertura": m.mean(), "acerto": ok1[m].mean() if m.any() else None})

# ---------------------------------------------------------------- diagnóstico operacional


test_eval = test.assign(ok=ok1, conf=conf)
bucket_msgs = pd.cut(test_eval["msgs"], [0, 1, 2, 99], labels=["1 mensagem", "2 mensagens", "3 ou mais"])
bucket_len = pd.cut(test_eval["words"], [0, 15, 30, 60, 10_000], labels=["até 15 palavras", "16 a 30", "31 a 60", "mais de 60"])
acc_by = {
    "mensagens": test_eval.groupby(bucket_msgs, observed=True)["ok"].agg(["mean", "size"]).reset_index().to_dict("records"),
    "tamanho": test_eval.groupby(bucket_len, observed=True)["ok"].agg(["mean", "size"]).reset_index().to_dict("records"),
    "pedido_vazio": test_eval.groupby("info_poor")["ok"].agg(["mean", "size"]).reset_index().to_dict("records"),
    "sensivel": test_eval.groupby("sensitive")["ok"].agg(["mean", "size"]).reset_index().to_dict("records"),
}
for k, v in acc_by.items():
    print(f"  acerto por {k}: " + " | ".join(f"{list(r.values())[0]}: {r['mean']:.1%} (n={r['size']})" for r in v))

prec, rec, f1, sup = precision_recall_fscore_support(y_te, pred, labels=range(len(classes)))
vocab = np.array(vec.get_feature_names_out())
top_terms = {c: vocab[np.argsort(clf.coef_[i])[::-1][:12]].tolist() for i, c in enumerate(classes)}

extra_msgs = int((df["msgs"] - 1).sum())
operacao = {
    "total": len(df),
    "filas": [{"fila": c, "descricao": QUEUE_INFO[c], "volume": int((df["Topic_group"] == c).sum()),
               "precisao": prec[i], "recall": rec[i], "f1": f1[i], "termos": top_terms[c],
               "cadeia": df.loc[df["Topic_group"] == c, "thread"].mean(),
               "vazio": df.loc[df["Topic_group"] == c, "info_poor"].mean(),
               "sensivel": df.loc[df["Topic_group"] == c, "sensitive"].mean()} for i, c in enumerate(classes)],
    "cadeia_total": df["thread"].mean(), "mensagens_extras_por_100": 100 * extra_msgs / len(df),
    "vazio_total": df["info_poor"].mean(), "sensivel_total": df["sensitive"].mean(),
    "vazio_rotulos": df.loc[df["info_poor"], "Topic_group"].value_counts().to_dict(),
    "vazio_exemplos": df.loc[df["info_poor"], "Document"].sample(4, random_state=SEED).tolist(),
    "urgente_total": df["urgent"].mean(), "autoatendimento_total": df["self_service"].mean(),
    "autoatendimento_access": df.loc[df["Topic_group"] == "Access", "self_service"].mean(),
    "acerto_por": acc_by,
    "confusao": confusion_matrix(y_te, pred, labels=range(len(classes))),
    "curva": curve, "acerto_local": local,
    "teste": {"n": len(test), "acerto": ok1.mean(), "top2": ok2.mean(), "ece": expected_calibration_error(conf, ok1)},
}
print(f"Cadeias de e-mail: {df['thread'].mean():.1%} | pedidos vazios: {df['info_poor'].mean():.1%} | "
      f"sensíveis: {df['sensitive'].mean():.1%} | urgentes: {df['urgent'].mean():.1%} | "
      f"autoatendimento (senha/bloqueio): {df['self_service'].mean():.1%}")
save_json("operacao.json", operacao)

# ---------------------------------------------------------------- exportações para o navegador
flags = sum(test[f].values.astype(int) * bit for f, bit in FLAG_BITS.items())
save_json("simulador.json", {
    "classes": classes, "limiar_auto": tau_auto, "limiar_assistido": tau_assist,
    "meta_auto": TARGET_AUTO, "meta_assistido": TARGET_ASSIST, "flag_bits": FLAG_BITS,
    "y": y_te, "pred": pred, "second": second, "conf": np.round(conf * 1000).astype(int), "flags": flags,
})

save_json("model.json", {
    "classes": classes, "queue_info": QUEUE_INFO,
    "vocab": vocab.tolist(), "idf": np.round(vec.idf_, 4),
    "coef": np.round(clf.coef_, 4), "intercept": np.round(clf.intercept_, 4),
    "tokenizer": {"pattern": r"[\p{L}\p{N}_]{2,}", "lowercase": True, "sublinear_tf": True, "norm": "l2"},
    "policy": POLICY, "limiar_auto": tau_auto, "limiar_assistido": tau_assist,
    "treino": {"n": len(train), "C": C, "min_df": 2},
})

# Paridade Python x navegador (checada por tests/parity.mjs): 300 tickets de teste + frases escritas à mão em inglês
# natural, português e espanhol, para exercitar a regra de cobertura. Compara probabilidades E a faixa de decisão.
extra = pd.DataFrame({"Document": [
    "my laptop screen is flickering and the docking station does not detect the external monitor",
    "Hi team, I cannot log into Confluence since this morning, my account seems locked. Can you help?",
    "Please create a new purchase order for two monitors and a keyboard for the new hire starting Monday",
    "I will be on maternity leave from next month, who should I talk to about my payroll?",
    "Olá, não consigo acessar minha conta do Outlook, a senha expirou e preciso de ajuda urgente",
    "Meu notebook está muito lento e a tela pisca quando conecto o monitor externo",
    "No puedo acceder a mi correo, la contraseña no funciona",
    "hello please help thank you",
]})
parity = pd.concat([test.sample(300, random_state=SEED)[["Document"]], extra], ignore_index=True)
parity = add_flags(parity).assign(ood=lambda d: d["Document"].map(is_ood))
parity_proba = clf.predict_proba(vec.transform(parity["Document"]))
save_json("paridade.json", {
    "docs": parity["Document"].tolist(), "proba": np.round(parity_proba, 6),
    "faixas": [decide_lane(*a) for a in zip(parity_proba.max(1), parity["info_poor"], parity["ood"], parity["sensitive"])],
})

# Exemplos para a triagem ao vivo: escolhidos por critério (inclui um erro de propósito), textos curtos
rng = np.random.default_rng(SEED)
short = test_eval["words"].between(8, 60).values
criteria = {
    # Os três primeiros mostram o caso típico: acerto, alta confiança, texto curto. O último mostra o oposto.
    "Senha bloqueada": short & test["self_service"].values & (y_te == classes.index("Access")) & ok1 & (conf >= tau_auto),
    "Equipamento": short & (y_te == classes.index("Hardware")) & ok1 & (conf >= tau_auto) & ~test["thread"].values,
    "Pedido de compra": short & (y_te == classes.index("Purchase")) & ok1 & (conf >= tau_auto),
    "Cadeia de e-mails": test_eval["msgs"].between(3, 4).values & test_eval["words"].between(40, 110).values,
    "Pedido vazio": test["info_poor"].values & test_eval["words"].between(4, 20).values,
    "Assunto sensível": short & test["sensitive"].values & (test["Topic_group"] == "HR Support").values,
    "Ambíguo": short & (conf >= 0.35) & (conf < tau_assist),
    "Modelo x rótulo": short & (conf >= 0.9) & ~ok1,
}
examples = []
for label, mask in criteria.items():
    assert mask.any(), f"nenhum ticket para o exemplo '{label}'"
    i = rng.choice(np.flatnonzero(mask))
    examples.append({"titulo": label, "texto": test["Document"].iloc[i], "rotulo": test["Topic_group"].iloc[i]})
save_json("exemplos.json", examples)

# Auditoria de rótulos: divergências em que o modelo tinha >= 90% de confiança
disagree = test_eval[(conf >= 0.9) & ~ok1].assign(modelo=[classes[p] for p in pred[(conf >= 0.9) & ~ok1]])
print(f"Divergências com confiança >= 0,9 no teste: {len(disagree)} ({len(disagree) / (conf >= 0.9).sum():.1%} da faixa)")
audit_file = SUBMISSION / "process-log" / "auditoria-rotulos" / "candidatos.csv"
if audit_file.exists():
    # O arquivo guarda os vereditos da IA, do Gemini e do Pedro: nunca sobrescrever numa nova rodada.
    print(f"   {audit_file.name} já existe, com vereditos: mantido como está")
else:
    audit_file.parent.mkdir(parents=True, exist_ok=True)
    (disagree.sample(40, random_state=SEED)
     .assign(conf=lambda d: d["conf"].round(3), veredito_ia="", justificativa_ia="", veredito_pedro="")
     .rename(columns={"Document": "texto", "Topic_group": "rotulo"})
     [["texto", "rotulo", "modelo", "conf", "veredito_ia", "justificativa_ia", "veredito_pedro"]]
     .to_csv(audit_file, index_label="id", encoding="utf-8-sig"))
    print(f"-> process-log/auditoria-rotulos/candidatos.csv (40 de {len(disagree)})")
