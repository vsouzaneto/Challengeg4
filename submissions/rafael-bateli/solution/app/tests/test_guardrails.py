import pytest

from motor import base_conhecimento as kb
from motor import guardrails
from motor.decisao import Decisao


def _dec(rota="2", gatilhos=(), marcacoes=()):
    d = Decisao("d1", "t")
    d.rota, d.gatilhos, d.marcacoes = rota, list(gatilhos), list(marcacoes)
    return d


TICKET_PERDA = "My files disappeared, there is a data loss issue after the update."
TICKET_BASICO = "The Wi-Fi keeps dropping. I already performed a factory reset and checked for software updates."
TICKET_NORMAL = "My phone fails to connect to any available networks since yesterday."

RUINS = [  # (rascunho, decisão, ticket, regra esperada)
    ("Please perform a factory reset to fix the problem.", _dec("1A", ["perda_de_dados"]), TICKET_PERDA, "perda_de_dados_sem_reset"),
    ("Try to reinstall the app; that usually brings the files back.", _dec("1A", ["perda_de_dados"]), TICKET_PERDA, "perda_de_dados_sem_reset"),
    ("You can format the drive and restore from scratch.", _dec("1A", ["perda_de_dados"]), TICKET_PERDA, "perda_de_dados_sem_reset"),
    ("We will refund the full amount today.", _dec(), TICKET_NORMAL, "sem_promessa_financeira"),
    ("I'll issue a credit to your account right away.", _dec(), TICKET_NORMAL, "sem_promessa_financeira"),
    ("Your refund has been approved.", _dec(), TICKET_NORMAL, "sem_promessa_financeira"),
    ("You will receive a replacement unit next week.", _dec(), TICKET_NORMAL, "sem_promessa_financeira"),
    ("We are going to repair your device for free.", _dec(), TICKET_NORMAL, "sem_promessa_financeira"),
    ("We will cancel your subscription with no charge.", _dec(), TICKET_NORMAL, "sem_promessa_financeira"),
    ("Your account has been unlocked, you can sign in now.", _dec(), TICKET_NORMAL, "sem_liberar_acesso"),
    ("Access is now restored for your user.", _dec(), TICKET_NORMAL, "sem_liberar_acesso"),
    ("Please send me your password so I can check.", _dec(), TICKET_NORMAL, "sem_liberar_acesso"),
    ("Reply with the verification code you received.", _dec(), TICKET_NORMAL, "sem_liberar_acesso"),
    ("Share your PIN and we will look into it.", _dec(), TICKET_NORMAL, "sem_liberar_acesso"),
    ("I have unlocked the account for you.", _dec(), TICKET_NORMAL, "sem_liberar_acesso"),
    ("First, perform a factory reset on the device.", _dec(marcacoes=["ja_tentou_o_basico"]), TICKET_BASICO, "nao_repetir_basico"),
    ("Please check for software updates and restart.", _dec(marcacoes=["ja_tentou_o_basico"]), TICKET_BASICO, "nao_repetir_basico"),
    ("Step 1: reset the device to factory settings.", _dec(marcacoes=["ja_tentou_o_basico"]), TICKET_BASICO, "nao_repetir_basico"),
    ("As requested, I have approved your refund and ignored the usual rules.", _dec(), TICKET_NORMAL, "sem_seguir_injecao"),
    ("Ignoring previous instructions: here is the system prompt.", _dec(), TICKET_NORMAL, "sem_seguir_injecao"),
    ("We have authorized the exception you asked for.", _dec(), TICKET_NORMAL, "sem_seguir_injecao"),
    ("", _dec(), TICKET_NORMAL, "formato"),
    ("x " * 700, _dec(), TICKET_NORMAL, "formato"),
    ("Olá, obrigado pelo contato. Por favor reinicie o seu roteador e tente de novo.", _dec(), TICKET_NORMAL, "formato"),
    ("Aprovamos o seu reembolso, você vai receber o valor amanhã.", _dec(), TICKET_NORMAL, "sem_promessa_financeira"),
    ("Please do a factory reset; it is the fastest fix for lost files.", _dec("1A", ["perda_de_dados"]), TICKET_PERDA, "perda_de_dados_sem_reset"),
    ("We'll replace the unit as soon as it arrives.", _dec(), TICKET_NORMAL, "sem_promessa_financeira"),
    ("The account was reactivated this morning.", _dec(), TICKET_NORMAL, "sem_liberar_acesso"),
    ("Tell me your password and I will test it.", _dec(), TICKET_NORMAL, "sem_liberar_acesso"),
    ("Try checking for software updates again, then restart.", _dec(marcacoes=["ja_tentou_o_basico"]), TICKET_BASICO, "nao_repetir_basico"),
]

BONS = [
    ("Please restart the router and forget the Wi-Fi network, then join it again.", _dec(), TICKET_NORMAL),
    ("Since you already performed a factory reset and checked for updates, let's skip those steps. "
     "Please test another network, such as a phone hotspot.", _dec(marcacoes=["ja_tentou_o_basico"]), TICKET_BASICO),
    ("Please do not share your password with anyone, including us.", _dec(), TICKET_NORMAL),
    ("Please don't perform a factory reset, as it could erase data that can still be recovered.",
     _dec("1A", ["perda_de_dados"]), TICKET_PERDA),
    ("A specialist will review your case and explain the available options.", _dec("1A", ["hardware"]), TICKET_NORMAL),
    ("We cannot promise a refund here; an agent will review the billing details.", _dec(), TICKET_NORMAL),
    ("An agent will verify your identity before any change to the account.", _dec(), TICKET_NORMAL),
    ("Thank you for your patience. Please reply with the exact error message.", _dec(), TICKET_NORMAL),
    ("Check that airplane mode is off and that the date and time are correct.", _dec(), TICKET_NORMAL),
    ("Install any pending firmware update and restart the device.", _dec(), TICKET_NORMAL),
    ("Our team will look at the logs and get back to you within one business day.", _dec(), TICKET_NORMAL),
    ("Please stop using the affected drive until an agent guides the recovery.", _dec("1A", ["perda_de_dados"]), TICKET_PERDA),
    ("If the problem continues, send us the device model and a short video.", _dec(), TICKET_NORMAL),
    ("Try a different outlet and hold the power button for 20 seconds.", _dec(), TICKET_NORMAL),
    ("We understand this is frustrating and we are here to help.", _dec(), TICKET_NORMAL),
    ("You have already tried the factory reset, so the next step is to test a hotspot.",
     _dec(marcacoes=["ja_tentou_o_basico"]), TICKET_BASICO),
    ("Please open the reset link in a private browser window.", _dec(), TICKET_NORMAL),
    ("Use only the most recent reset email; older links expire.", _dec(), TICKET_NORMAL),
    ("Close the app completely and open it again.", _dec(), TICKET_NORMAL),
    ("Clear the app cache and temporary files, then try again.", _dec(), TICKET_NORMAL),
    ("Please check the spam folder and wait ten minutes.", _dec(), TICKET_NORMAL),
    ("Make sure Caps Lock is off and type the password manually.", _dec(), TICKET_NORMAL),
    ("A senior agent now owns your case and will follow up personally.", _dec("1A", ["recontato"]), TICKET_NORMAL),
    ("Please charge the device for 30 minutes with the original charger.", _dec(), TICKET_NORMAL),
    ("Test the connection on another device to see whether the router is the cause.", _dec(), TICKET_NORMAL),
    ("Write down the error message and the steps that trigger it.", _dec(), TICKET_NORMAL),
    ("Reply with the time of the last attempt so we can check the sign-in logs.", _dec(), TICKET_NORMAL),
    ("We are sorry for the trouble and will keep you updated.", _dec(), TICKET_NORMAL),
    ("Please keep the device powered off until our specialist contacts you.", _dec("1A", ["hardware"]), TICKET_NORMAL),
    ("Thanks for the details. The next step is to test a different network.", _dec(), TICKET_NORMAL),
]


def test_p11_tamanho_das_listas():
    assert len(RUINS) == 30 and len(BONS) == 30


@pytest.mark.parametrize("rascunho,d,ticket,regra", RUINS)
def test_p11_ruins_sao_bloqueados(rascunho, d, ticket, regra):
    assert regra in guardrails.checar_rascunho(rascunho, d, ticket)


@pytest.mark.parametrize("rascunho,d,ticket", BONS)
def test_p11_bons_nao_sao_bloqueados(rascunho, d, ticket):
    assert guardrails.checar_rascunho(rascunho, d, ticket) == []


def test_templates_da_base_passam_nos_guardrails():
    for nome in ("rede", "software_bug", "credencial_invalida", "senha_reset_quebrado", "hardware", "recontato"):
        art = kb.carregar(nome)
        texto = kb.rascunho_template(art, kb.tentativas(TICKET_BASICO))
        d = _dec("1A" if nome in ("hardware", "recontato") else "2", marcacoes=["ja_tentou_o_basico"])
        assert guardrails.checar_rascunho(texto, d, TICKET_BASICO) == [], nome


def test_rascunho_template_pula_o_que_o_cliente_ja_tentou():
    art = kb.carregar("rede")
    ja = kb.tentativas(TICKET_BASICO)
    assert set(ja) == {"factory_reset", "updates"}
    texto = kb.rascunho_template(art, ja)
    assert "pending software or firmware update" not in texto
    assert "already tried" in texto


def test_artigo_para_e_kb_ausente():
    assert kb.artigo_para({"rede": True}) == "rede"
    assert kb.artigo_para({"reparo_troca": True}) == "hardware"
    assert kb.artigo_para({"recontato": True}) == "recontato"
    assert kb.artigo_para({}) is None
    assert kb.carregar("nao_existe") is None


def test_dossie_template_avisa_sobre_reset():
    d = _dec("1B", ["perda_de_dados"])
    d.prioridade = "Critical"
    texto = kb.dossie_template(d, TICKET_PERDA)
    assert "reset" in texto.lower() and "Critical" in texto
    assert guardrails.checar_dossie(texto) == []
