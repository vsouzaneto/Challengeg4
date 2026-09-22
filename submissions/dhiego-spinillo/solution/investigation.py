"""Próximo passo derivado de conferências declaradas pelo atendente.

Não consulta sistemas externos e não detecta incidentes automaticamente.
"""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Check = Literal['pending', 'checked', 'unavailable']
RULE_VERSION = 'investigation-1'


class Checks(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    other_tickets: Check = 'pending'
    system: Check = 'pending'
    internal_notes: Check = 'pending'


class Investigation(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    checks: Checks = Field(default_factory=Checks)
    system_outcome: Literal['unknown', 'resolved', 'unresolved'] = 'unknown'
    incident_reported: bool = False
    incident_quote: str = Field(default='', max_length=2000)

    @model_validator(mode='after')
    def consistent_evidence(self):
        if self.system_outcome != 'unknown' and self.checks.system != 'checked':
            raise ValueError('Confirme a consulta ao sistema antes de registrar seu resultado.')
        if self.incident_reported and not self.incident_quote.strip():
            raise ValueError('Inclua o trecho original que motivou a investigação de incidente.')
        if not self.incident_reported and self.incident_quote:
            raise ValueError('Trecho de incidente informado sem marcar o relato.')
        return self


def prepare_next_step(context: Investigation, original: str):
    if context.incident_reported and context.incident_quote not in original:
        raise ValueError('O trecho do relato precisa existir literalmente neste ticket.')
    checks = context.checks.model_dump()
    missing = [name for name, value in checks.items() if value == 'pending']
    unavailable = [name for name, value in checks.items() if value == 'unavailable']
    reply_draft = None
    if context.incident_reported:
        code, title = 'investigate_incident', 'Investigar o relato de possível incidente'
        steps = [
            'Compreender com o cliente como concluiu que há um problema e quais evidências já possui.',
            'Solicitar evidências pertinentes sem repetir o que já consta no atendimento.',
            'Acionar Segurança ou Engenharia conforme o procedimento da operação para avaliar o relato e a necessidade de consultar logs.',
            'Distinguir interpretação, falha técnica e erro de preenchimento antes de atribuir causa. A categoria do assunto é preservada.',
        ]
        reply_draft = ('Para entendermos o relato, pode descrever o que observou e o que levou a essa conclusão? '
                       'Se tiver uma captura de tela ou outra evidência, envie apenas o trecho necessário para a investigação. '
                       'Com essas informações, poderemos direcionar a análise à equipe responsável.')
    elif missing:
        code, title = 'check_context', 'Conferir o contexto antes de novo contato'
        steps = [
            'Consultar outros tickets abertos, o estado atual no sistema e as notas internas disponíveis.',
            'Registrar o que foi possível verificar. Se uma fonte estiver indisponível, indicar essa limitação.',
            'Usar o contexto já registrado para evitar perguntas repetidas; não presumir resolução ou pendência.',
        ]
    elif context.system_outcome == 'resolved':
        code, title = 'confirm_remaining_need', 'Confirmar se resta alguma necessidade'
        steps = [
            'Revisar o resultado conferido no sistema junto aos demais registros disponíveis.',
            'Informar ao cliente apenas o resultado efetivamente verificado e perguntar se precisa de ajuda com outra solicitação.',
            'Não solicitar novamente detalhes do problema resolvido sem uma necessidade concreta. Não encerrar automaticamente.',
        ]
        reply_draft = ('Verifiquei o registro da sua solicitação e ela consta como atendida. '
                       'Ainda há alguma pendência nesse atendimento ou outra solicitação em que posso ajudar?')
    elif context.system_outcome == 'unresolved':
        code, title = 'update_diagnosis', 'Atualizar o diagnóstico para preparar o encaminhamento'
        steps = [
            'Verificar nos registros quais tentativas e evidências já foram informadas.',
            'Perguntar se houve nova tentativa, se o erro persiste e em qual etapa ocorre, aproveitando respostas já disponíveis.',
            'Solicitar evidências que ainda faltam, como print de tela, e reunir contexto para o time técnico.',
        ]
        reply_draft = ('Você chegou a realizar uma nova tentativa? Se o erro ainda acontece, em qual etapa ele aparece? '
                       'Se possível, envie uma captura da mensagem de erro ou outra evidência para complementar '
                       'as informações que já temos e direcionar a análise técnica.')
    else:
        code, title = 'recover_context', 'Recuperar o contexto que falta'
        steps = [
            'O estado atual continua desconhecido. Recuperar o registro ou consultar a equipe responsável.',
            'Indisponibilidade da informação não demonstra que a solicitação foi atendida nem que permanece pendente.',
            'Contatar o cliente somente para informações ou confirmações necessárias que não puderem ser obtidas internamente.',
        ]
    return {'rule_version': RULE_VERSION, 'code': code, 'title': title, 'steps': steps,
            'reply_draft': reply_draft, 'reply_source': 'Modelo de texto por regra; não gerado por LLM.',
            'pending_checks': missing, 'unavailable_checks': unavailable,
            'basis': 'Conferências e relato registrados pelo atendente; sem consulta automática a sistemas.',
            'requires_human_confirmation': True, 'external_action_executed': False}
