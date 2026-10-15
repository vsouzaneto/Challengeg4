"""Teste automatizado do app (Streamlit AppTest): confere os números-chave do painel e as interações.
Uso: cd solution/03-prototipo && python teste_app.py. Não chama a API do Gemini."""
import os, sys, time
os.environ.pop("GEMINI_API_KEY", None)
sys.stdout.reconfigure(encoding="utf-8")
import pandas, streamlit
from streamlit.testing.v1 import AppTest
print("pandas", pandas.__version__, "| streamlit", streamlit.__version__)
t = time.time()
at = AppTest.from_file(os.path.abspath("app.py"), default_timeout=900).run()
print("1ª execução:", round(time.time() - t, 1), "s")
assert not at.exception, [e.message for e in at.exception]
print("abas:", [tb.label for tb in at.tabs])
md = " ".join(m.value for m in at.markdown)
for esperado in ["Resposta ao Diretor de Operações", "49%", "65,5%", "96,4%", "9.568", "1.218 h", "552", "2.106",
                 "R$ 46.563", "7,6 h", "8,1 h", "1.365 de 2.769", "91,0%", "34,1% → 10,8%", "23,4%", "23,3%", "11,2%",
                 "9,7%", "O que preciso de você", "Escalado para Segurança", "Triagem humana", "0,7%", "3,5%", "10,4%", "76,0%", "101 h/mês", "175 h/mês", "81%",
                 "R$ 21.105", "R$ 80.508", "0 de\n21", "27 horas", "0,2 ponto"]:
    assert esperado in md, f"faltou no painel: {esperado!r}"
for esperado in ["2 opções ao agente: Miscellaneous", "travas de domínio", "Billing", "94,0% a 96,2%"]:
    assert esperado in md + " ".join(c.value for c in at.caption), f"faltou no painel: {esperado!r}"
print("painel: todos os números-chave presentes")
ta = at.text_area[0]
assert ta.value.startswith("Hi, my laptop"), "triagem ao vivo deveria abrir já preenchida"
assert "Fila: Hardware" in md and "Automático" in md
# interação 1: phishing digitado
at.text_area[0].input("URGENT: I received a suspicious email asking for my password and I clicked the link.").run()
assert not at.exception, [e.message for e in at.exception]
md = " ".join(m.value for m in at.markdown)
assert "Fila: Segurança da Informação" in md and any("Escalar agora" in e.value for e in at.error)
print("interação phishing: escalado para Segurança OK")
# interação 2: texto vazio
at.text_area[0].input("   ").run()
assert not at.exception
assert any("Cole o texto" in i.value for i in at.info)
print("interação texto vazio: mensagem orientadora OK")
# interação 3: exemplo fora do domínio via selectbox
at.selectbox[0].select("Fora do domínio (em português)").run()
assert not at.exception
md = " ".join(m.value for m in at.markdown)
assert "Fila: Triagem humana" in md
print("interação selectbox (português): Triagem humana OK")
# interação 4: ticket real aleatório + sortear outro
at.selectbox[0].select("Ticket real aleatório do conjunto de teste").run()
assert not at.exception
at.button[0].click().run()
assert not at.exception
print("interação ticket aleatório + sortear: OK")
# fila real: amostra menor
at.slider[0].set_value(1000).run()
assert not at.exception
print("fila real com 1.000 tickets: OK")
# calculadora de ROI: mudar o volume não pode alterar o painel (CENARIOS é compartilhado entre sessões)
next(n for n in at.number_input if n.label == "Tickets por ano").set_value(60000).run()
at.run()  # o painel roda antes da calculadora: o efeito apareceria no rerun seguinte
assert not at.exception
md = " ".join(m.value for m in at.markdown)
assert "1.218 h" in md and "552" in md, "a calculadora alterou os cenários do painel"
print("calculadora com 60.000 tickets: painel inalterado OK")
print("métricas:", [(x.label, x.value) for x in at.metric][:7])
print("TUDO OK em", round(time.time() - t, 1), "s")
