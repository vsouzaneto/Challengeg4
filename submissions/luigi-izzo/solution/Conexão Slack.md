### Passo a Passo de Setup do Slack Webhook:

1. Acesse https://api.slack.com/apps e clique em **Create New App**.
2. Selecione **From scratch**, dê o nome de `Lead Scorer Bot` e escolha o seu Workspace do Slack.
3. No menu lateral, clique em **Incoming Webhooks** e ative a chave para **On**.
4. Clique no botão **Add New Webhook to Workspace** ao final da página.
5. Selecione o canal onde as notificações serão enviadas (ex: `#vendas-prioridades` ou um canal por regional) e clique em **Allow**.
6. Copie a **Webhook URL** gerada (formato: `https://hooks.slack.com/services/T000/B000/XXXX`).
7. No Databricks, você pode salvar essa URL como um Secret do Databricks CLI ou colar diretamente na variável `SLACK_WEBHOOK_URL` no script abaixo.