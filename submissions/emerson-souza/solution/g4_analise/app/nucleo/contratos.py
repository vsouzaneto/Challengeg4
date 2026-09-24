"""
Contratos de dados: os campos que cada modulo entende (PLANEJAMENTO.md, secoes 4 e 6).

Qualquer base entra ligando as colunas dela a estes campos (De/Para).
Para os dados do desafio, o De/Para ja vem pronto (coluna_desafio).
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Campo:
    nome: str                 # nome interno (padrao do sistema)
    rotulo: str               # o que aparece na tela
    obrigatorio: bool = False
    coluna_desafio: str | None = None   # nome da coluna no dataset do desafio
    sinonimos: tuple = ()     # outros nomes comuns, para a sugestao automatica


@dataclass(frozen=True)
class Tabela:
    nome: str
    rotulo: str
    obrigatoria: bool
    arquivo_desafio: str      # caminho relativo dentro da pasta de dados do desafio
    campos: tuple = field(default_factory=tuple)

    def obrigatorios(self):
        return [c for c in self.campos if c.obrigatorio]


@dataclass(frozen=True)
class Modulo:
    chave: str
    nome: str
    desafio: str
    descricao: str
    tabelas: tuple

    def tabela(self, nome):
        return next(t for t in self.tabelas if t.nome == nome)


C = Campo

CHURN = Modulo(
    chave="churn", nome="Churn", desafio="001",
    descricao="Causa raiz dos cancelamentos, segmentos e contas em risco, ações priorizadas com impacto.",
    tabelas=(
        Tabela("clientes", "Clientes (contas)", True, "001-churn/ravenstack_accounts.csv", (
            C("id_cliente", "ID do cliente", True, "account_id", ("customer_id", "client_id", "id_conta")),
            C("nome_cliente", "Nome do cliente", False, "account_name", ("name", "company")),
            C("segmento", "Segmento / indústria", False, "industry", ("sector", "setor", "vertical")),
            C("pais", "País", False, "country", ("location", "pais")),
            C("data_entrada", "Data de entrada", False, "signup_date", ("created_at", "start_date")),
            C("canal_aquisicao", "Canal de aquisição", False, "referral_source", ("source", "channel", "origem")),
            C("plano", "Plano", False, "plan_tier", ("plan", "tier")),
            C("assentos", "Assentos / licenças", False, "seats", ("licenses", "users")),
            C("em_teste", "Em período de teste", False, "is_trial", ("trial",)),
            C("produto", "Produto", False, None, ("product",)),
            C("idade", "Idade do cliente", False, None, ("age",)),
            C("genero", "Gênero do cliente", False, None, ("gender",)),
            C("cancelou", "Cancelou (sim/não)", True, "churn_flag", ("churned", "is_churned", "cancelado")),
        )),
        Tabela("contratos", "Contratos / assinaturas (sem esta tabela, os valores viram contagem de clientes)", False, "001-churn/ravenstack_subscriptions.csv", (
            C("id_contrato", "ID do contrato", True, "subscription_id", ("contract_id",)),
            C("id_cliente", "ID do cliente", True, "account_id", ("customer_id",)),
            C("receita_mensal", "Receita mensal (MRR)", True, "mrr_amount", ("mrr", "monthly_revenue")),
            C("inicio", "Início", False, "start_date", ()),
            C("fim", "Fim", False, "end_date", ()),
            C("plano", "Plano", False, "plan_tier", ("plan",)),
            C("assentos", "Assentos", False, "seats", ()),
            C("upgrade", "Teve upgrade", False, "upgrade_flag", ()),
            C("downgrade", "Teve downgrade", False, "downgrade_flag", ()),
            C("cobranca", "Frequência de cobrança", False, "billing_frequency", ()),
        )),
        Tabela("uso", "Uso do produto", False, "001-churn/ravenstack_feature_usage.csv", (
            C("id_contrato", "ID do contrato", True, "subscription_id", ()),
            C("data", "Data do uso", True, "usage_date", ("date",)),
            C("quantidade", "Quantidade de uso", True, "usage_count", ("count",)),
            C("funcionalidade", "Funcionalidade", False, "feature_name", ("feature",)),
            C("erros", "Erros", False, "error_count", ("errors",)),
            C("e_beta", "Funcionalidade beta", False, "is_beta_feature", ("beta",)),
        )),
        Tabela("chamados", "Chamados de suporte", False, "001-churn/ravenstack_support_tickets.csv", (
            C("id_chamado", "ID do chamado", True, "ticket_id", ()),
            C("id_cliente", "ID do cliente", True, "account_id", ()),
            C("abertura", "Abertura", False, "submitted_at", ("created_at",)),
            C("prioridade", "Prioridade", False, "priority", ()),
            C("primeira_resposta_min", "1ª resposta (minutos)", False, "first_response_time_minutes", ()),
            C("resolucao_h", "Resolução (horas)", False, "resolution_time_hours", ()),
            C("satisfacao", "Satisfação", False, "satisfaction_score", ("csat",)),
            C("escalado", "Escalado", False, "escalation_flag", ()),
        )),
        Tabela("cancelamentos", "Eventos de cancelamento", False, "001-churn/ravenstack_churn_events.csv", (
            C("id_cliente", "ID do cliente", True, "account_id", ()),
            C("data", "Data do cancelamento", True, "churn_date", ()),
            C("motivo", "Motivo", True, "reason_code", ("reason",)),
            C("reembolso", "Reembolso", False, "refund_amount_usd", ()),
            C("reativacao", "É reativação", False, "is_reactivation", ()),
            C("comentario", "Comentário do cliente", False, "feedback_text", ()),
        )),
    ),
)

SUPORTE = Modulo(
    chave="suporte", nome="Suporte", desafio="002",
    descricao="Gargalos, satisfação, desperdício, o que automatizar e o que NÃO automatizar, classificador de tickets.",
    tabelas=(
        Tabela("chamados", "Chamados (métricas + texto)", True, "002-suporte/customer_support_tickets.csv", (
            C("id_chamado", "ID do chamado", True, "Ticket ID", ("ticket_id",)),
            C("id_cliente", "Cliente (e-mail/ID)", False, "Customer Email", ("customer_id", "email")),
            C("idade", "Idade do cliente", False, "Customer Age", ("age",)),
            C("genero", "Gênero do cliente", False, "Customer Gender", ("gender",)),
            C("produto", "Produto", False, "Product Purchased", ("product",)),
            C("tipo", "Tipo do chamado", False, "Ticket Type", ("type",)),
            C("assunto", "Assunto", False, "Ticket Subject", ("subject",)),
            C("texto", "Texto do chamado", False, "Ticket Description", ("description", "document")),
            C("status", "Status", False, "Ticket Status", ("status",)),
            C("resolucao_texto", "Texto da resolução", False, "Resolution", ()),
            C("prioridade", "Prioridade", False, "Ticket Priority", ("priority",)),
            C("canal", "Canal", False, "Ticket Channel", ("channel",)),
            C("primeira_resposta", "Data/hora da 1ª resposta", False, "First Response Time", ()),
            C("resolucao", "Data/hora da resolução", False, "Time to Resolution", ()),
            C("satisfacao", "Satisfação", False, "Customer Satisfaction Rating", ("csat", "satisfaction")),
            # Alternativa as datas/horas: bases que ja trazem a duracao pronta (ex.: tickets da RavenStack)
            C("tempo_resposta_h", "Tempo até a 1ª resposta (horas)", False, None, ("first_response_hours",)),
            C("tempo_resolucao_h", "Tempo de resolução (horas)", False, None, ("resolution_time_hours", "resolution_hours")),
            C("escalado", "Escalado", False, None, ("escalation_flag", "escalated")),
        )),
        Tabela("treino", "Textos classificados (treino do classificador)", False,
               "002-suporte/all_tickets_processed_improved_v3.csv", (
            C("texto", "Texto", True, "Document", ("text", "description")),
            C("categoria", "Categoria", True, "Topic_group", ("category", "label", "topic")),
        )),
    ),
)

LEADS = Modulo(
    chave="leads", nome="Leads", desafio="003",
    descricao="Score explicável de oportunidades abertas, com o porquê de cada score e filtros por vendedor/manager/região.",
    tabelas=(
        Tabela("oportunidades", "Oportunidades (pipeline)", True, "003-lead-scorer/sales_pipeline.csv", (
            C("id_oportunidade", "ID da oportunidade", True, "opportunity_id", ("deal_id", "id")),
            C("vendedor", "Vendedor", True, "sales_agent", ("seller", "owner")),
            C("produto", "Produto", True, "product", ()),
            C("conta", "Conta", False, "account", ("company",)),
            C("estagio", "Estágio", True, "deal_stage", ("stage",)),
            C("data_inicio", "Data de início", False, "engage_date", ("created_at",)),
            C("data_fechamento", "Data de fechamento", False, "close_date", ()),
            C("valor_fechado", "Valor fechado", False, "close_value", ("amount", "value")),
            C("valor", "Valor do deal (se já conhecido)", False, None, ("deal_value", "valor_deal")),
        )),
        Tabela("vendedores", "Time de vendas", False, "003-lead-scorer/sales_teams.csv", (
            C("vendedor", "Vendedor", True, "sales_agent", ()),
            C("gestor", "Gestor (manager)", False, "manager", ()),
            C("regiao", "Região", False, "regional_office", ("region",)),
        )),
        Tabela("produtos", "Produtos", False, "003-lead-scorer/products.csv", (
            C("produto", "Produto", True, "product", ()),
            C("serie", "Série", False, "series", ()),
            C("preco", "Preço", False, "sales_price", ("price",)),
        )),
        Tabela("contas", "Contas", False, "003-lead-scorer/accounts.csv", (
            C("conta", "Conta", True, "account", ()),
            C("setor", "Setor", False, "sector", ("industry",)),
            C("receita", "Receita anual", False, "revenue", ()),
            C("funcionarios", "Funcionários", False, "employees", ()),
            C("local", "Localização", False, "office_location", ("country",)),
            C("matriz", "Empresa-mãe", False, "subsidiary_of", ()),
        )),
    ),
)

MIDIA = Modulo(
    chave="midia", nome="Mídia", desafio="004",
    descricao="O que gera engajamento, se patrocínio funciona (comparação justa), audiência e estratégia priorizada.",
    tabelas=(
        Tabela("posts", "Posts", True, "004-social/social_media_dataset.csv", (
            C("id_post", "ID do post", True, "content_id", ("post_id", "id")),
            C("plataforma", "Plataforma", True, "platform", ()),
            C("data", "Data do post", True, "post_date", ("date",)),
            C("views", "Visualizações (alcance)", True, "views", ("impressions", "reach")),
            C("curtidas", "Curtidas", False, "likes", ()),
            C("compartilhamentos", "Compartilhamentos", False, "shares", ()),
            C("comentarios", "Comentários", False, "comments_count", ("comments",)),
            C("tipo", "Tipo de conteúdo", False, "content_type", ()),
            C("categoria", "Categoria", False, "content_category", ("category",)),
            C("tamanho", "Tamanho/duração", False, "content_length", ("duration",)),
            C("hashtags", "Hashtags", False, "hashtags", ()),
            C("idioma", "Idioma", False, "language", ()),
            C("id_criador", "ID do criador", False, "creator_id", ()),
            C("seguidores", "Seguidores do criador", False, "follower_count", ("followers",)),
            C("patrocinado", "Patrocinado", False, "is_sponsored", ("sponsored",)),
            C("patrocinador", "Patrocinador", False, "sponsor_name", ()),
            C("categoria_patrocinador", "Categoria do patrocinador", False, "sponsor_category", ()),
            C("divulgacao", "Tipo de divulgação", False, "disclosure_type", ()),
            C("audiencia_idade", "Audiência: idade", False, "audience_age_distribution", ()),
            C("audiencia_genero", "Audiência: gênero", False, "audience_gender_distribution", ()),
            C("audiencia_local", "Audiência: local", False, "audience_location", ()),
        )),
    ),
)

MODULOS = {m.chave: m for m in (CHURN, SUPORTE, LEADS, MIDIA)}


def mapeamento_desafio(modulo):
    """De/Para pronto para os dados do desafio: {tabela: {campo: coluna}}."""
    return {t.nome: {c.nome: c.coluna_desafio for c in t.campos if c.coluna_desafio}
            for t in modulo.tabelas}
