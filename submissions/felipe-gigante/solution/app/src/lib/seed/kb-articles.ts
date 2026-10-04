// Knowledge Base inicial. Cobre os 16 assuntos do Dataset 1 e as categorias de TI do Dataset 2.
// Lacunas são INTENCIONAIS (ex.: endereço de cobrança após nota emitida) para demonstrar Knowledge Gap.
export type SeedArticle = { title: string; topic: string; tags: string; questions: string[]; body: string; body_en: string };

export const KB_ARTICLES: SeedArticle[] = [
  {
    title: "Redefinir senha e recuperar acesso à conta",
    topic: "Account access",
    tags: "password reset login access account senha acesso conta",
    questions: [
      "I can't access my account after resetting my password",
      "I forgot my password",
      "How do I reset my password?",
      "Esqueci minha senha",
      "Não consigo acessar minha conta depois de redefinir a senha",
      "Onde altero minha senha?",
      "Não consigo trocar minha password",
    ],
    body: `1. Acesse a tela de login e clique em "Esqueci minha senha".
2. Informe o e-mail cadastrado — o link chega em até 5 minutos (confira também spam/lixo eletrônico).
3. O link expira em 30 minutos; se expirou, solicite um novo.
4. Após redefinir, aguarde 2 minutos e faça login em uma janela anônima — sessões antigas em cache causam o erro "senha inválida".
5. Se usa autenticação em 2 fatores, confirme que o relógio do celular está no horário automático.`,
    body_en: `1. On the login screen, click "Forgot password".
2. Enter your registered e-mail — the link arrives within 5 minutes (check spam too).
3. The link expires in 30 minutes; request a new one if needed.
4. After resetting, wait 2 minutes and log in from a private window — cached sessions cause "invalid password" errors.
5. If you use 2-factor authentication, make sure your phone clock is set to automatic time.`,
  },
  {
    title: "Conta bloqueada por tentativas de login",
    topic: "Account access",
    tags: "locked account blocked attempts login bloqueada tentativas",
    questions: ["My account is locked", "Account locked after too many attempts", "Minha conta foi bloqueada", "Conta bloqueada por tentativas"],
    body: `Após 5 tentativas incorretas a conta fica bloqueada por 15 minutos, por segurança.
1. Aguarde 15 minutos sem tentar novamente (novas tentativas reiniciam o contador).
2. Use "Esqueci minha senha" para garantir a senha correta.
3. Se você NÃO fez essas tentativas, responda "não fui eu" — um especialista de segurança assume o caso.`,
    body_en: `After 5 wrong attempts the account is locked for 15 minutes for security.
1. Wait 15 minutes without retrying (new attempts reset the timer).
2. Use "Forgot password" to make sure you have the right password.
3. If you did NOT make those attempts, reply "it wasn't me" — a security specialist will take over.`,
  },
  {
    title: "Configuração inicial do produto",
    topic: "Product setup",
    tags: "setup configure pair first time configuração parear",
    questions: ["How do I set up my new device?", "I'm having trouble with product setup", "Como configuro meu produto novo?", "Não consigo parear o dispositivo"],
    body: `1. Carregue o dispositivo por pelo menos 30 minutos antes da primeira configuração.
2. Instale o app oficial e mantenha Bluetooth e localização ativos no celular.
3. No app, toque em "Adicionar dispositivo" e siga o assistente.
4. Se o pareamento falhar, reinicie o dispositivo (segure o botão de energia por 10s) e tente novamente a menos de 1 metro do celular.`,
    body_en: `1. Charge the device for at least 30 minutes before first setup.
2. Install the official app and keep Bluetooth and location enabled on your phone.
3. In the app, tap "Add device" and follow the wizard.
4. If pairing fails, restart the device (hold power for 10s) and try again within 1 meter of the phone.`,
  },
  {
    title: "Instalação de software, drivers e atualizações",
    topic: "Installation support",
    tags: "install installation driver software update instalar driver",
    questions: ["How do I install the software?", "Installation failed", "Driver installation error", "Como instalar o driver?", "A instalação deu erro"],
    body: `1. Baixe o instalador apenas do site oficial (versões antigas causam erro de assinatura).
2. Feche outros programas e execute como administrador.
3. Se aparecer erro, desinstale a versão anterior, reinicie o computador e instale novamente.
4. Em computadores corporativos sem permissão de administrador, solicite a instalação pelo time de TI.`,
    body_en: `1. Download the installer only from the official website (old versions cause signature errors).
2. Close other programs and run as administrator.
3. If an error appears, uninstall the previous version, restart and install again.
4. On corporate computers without admin rights, ask IT to install it.`,
  },
  {
    title: "Bateria descarregando rápido",
    topic: "Battery life",
    tags: "battery drain charging life bateria descarrega carregar",
    questions: ["My battery drains quickly", "Battery life is very short", "The battery doesn't last", "A bateria está descarregando muito rápido", "Bateria não dura"],
    body: `1. Atualize o firmware para a versão mais recente (corrige consumo em segundo plano).
2. Desative recursos que não usa: GPS contínuo, brilho máximo, sincronização automática.
3. Use o carregador original — carregadores genéricos podem não completar a carga.
4. Faça um ciclo completo: descarregue até 5% e carregue até 100% sem interrupção.
Se a autonomia continuar abaixo de 50% do informado, pode ser defeito coberto pela garantia.`,
    body_en: `1. Update the firmware to the latest version (fixes background drain).
2. Turn off unused features: continuous GPS, max brightness, auto-sync.
3. Use the original charger — generic chargers may not fully charge.
4. Do a full cycle: discharge to 5% and charge to 100% without interruption.
If battery life stays below 50% of spec, it may be a warranty defect.`,
  },
  {
    title: "Problemas de rede, Wi-Fi e Bluetooth",
    topic: "Network problem",
    tags: "wifi network internet connection bluetooth vpn rede conexão headphones fone earbuds phone celular pair disconnect",
    questions: ["My device won't connect to wifi", "Network problem", "Bluetooth keeps disconnecting", "Não conecta no wifi", "Problema de conexão com a internet", "Cannot connect to VPN"],
    body: `1. Reinicie o roteador e o dispositivo.
2. Esqueça a rede e conecte novamente digitando a senha.
3. Prefira a rede 2.4 GHz para dispositivos de casa inteligente.
4. Para VPN corporativa: após trocar a senha, atualize também a senha salva no cliente VPN.
5. Se o problema persistir em outras redes, pode ser hardware — responda aqui para abrirmos um chamado técnico.`,
    body_en: `1. Restart the router and the device.
2. Forget the network and reconnect typing the password.
3. Prefer the 2.4 GHz network for smart-home devices.
4. For corporate VPN: after changing your password, update the password saved in the VPN client.
5. If it persists on other networks, it may be hardware — reply here and we'll open a technical case.`,
  },
  {
    title: "Tela piscando, manchas ou sem imagem",
    topic: "Display issue",
    tags: "screen display flicker pixel monitor tela piscando imagem",
    questions: ["The screen is flickering", "Display issue", "My screen has dead pixels", "A tela está piscando", "Monitor sem imagem"],
    body: `1. Teste outro cabo/porta (HDMI ou USB-C) — cabos com defeito causam a maioria dos casos.
2. Atualize o driver de vídeo ou o firmware da TV/monitor.
3. Desative o brilho automático e modos de economia.
4. Se houver manchas, linhas ou pixels mortos visíveis em todas as fontes, é defeito físico: responda aqui com uma foto para abrirmos a garantia.`,
    body_en: `1. Try another cable/port (HDMI or USB-C) — faulty cables cause most cases.
2. Update the graphics driver or TV/monitor firmware.
3. Disable auto-brightness and power-saving modes.
4. Lines, stains or dead pixels on every source mean a physical defect: reply with a photo so we can open a warranty case.`,
  },
  {
    title: "Aplicativo travando ou bug após atualização",
    topic: "Software bug",
    tags: "crash bug freeze app update error travando atualização erro",
    questions: ["The app keeps crashing", "Software bug after update", "The application crashes when I try", "O aplicativo fecha sozinho", "Está travando depois da atualização"],
    body: `1. Atualize o app e o sistema operacional para a versão mais recente.
2. Limpe o cache do app (Configurações > Apps > Armazenamento > Limpar cache).
3. Reinstale o aplicativo.
4. Se continuar, responda com: modelo do aparelho, versão do app e o que você fazia quando travou — isso vai direto para o time de produto.`,
    body_en: `1. Update the app and operating system to the latest version.
2. Clear the app cache (Settings > Apps > Storage > Clear cache).
3. Reinstall the app.
4. If it persists, reply with: device model, app version and what you were doing — it goes straight to the product team.`,
  },
  {
    title: "Compatibilidade de produtos e acessórios",
    topic: "Product compatibility",
    tags: "compatible compatibility works with accessory peripheral compatível acessório peripheral compatibility",
    questions: ["Is this compatible with my phone?", "Does it work with Mac?", "Peripheral compatibility issue", "É compatível com meu celular?", "Funciona com iPhone?"],
    body: `Todos os produtos funcionam com Android 10+ e iOS 15+. Para computadores: Windows 10+ e macOS 12+.
Acessórios Bluetooth exigem Bluetooth 5.0. Adaptadores USB-C → HDMI precisam suportar DisplayPort Alt Mode.
Se o seu modelo não estiver nessa lista, responda com o modelo exato que confirmamos para você.`,
    body_en: `All products work with Android 10+ and iOS 15+. Computers: Windows 10+ and macOS 12+.
Bluetooth accessories require Bluetooth 5.0. USB-C → HDMI adapters must support DisplayPort Alt Mode.
If your model isn't listed, reply with the exact model and we'll confirm.`,
  },
  {
    title: "Recomendação de produto",
    topic: "Product recommendation",
    tags: "recommend best model which buy recomendação melhor modelo",
    questions: ["Which model should I buy?", "Can you recommend a product?", "Qual modelo você recomenda?", "Qual o melhor para mim?"],
    body: `Para indicar o modelo certo, considere:
1. Uso principal (trabalho, esportes, casa inteligente, entretenimento).
2. Ecossistema que você já usa (Android, iOS, Alexa, Google).
3. Orçamento.
Responda com essas 3 informações que um consultor envia a recomendação personalizada.`,
    body_en: `To recommend the right model, tell us:
1. Main use (work, sports, smart home, entertainment).
2. Ecosystem you already use (Android, iOS, Alexa, Google).
3. Budget.
Reply with these 3 details and a consultant will send a personalized recommendation.`,
  },
  {
    title: "Status de entrega e rastreio do pedido",
    topic: "Delivery problem",
    tags: "delivery shipping tracking order late entrega rastreio pedido atraso",
    questions: ["Where is my order?", "My delivery is late", "Tracking number not working", "Meu pedido não chegou", "Cadê minha entrega?", "Entrega atrasada"],
    body: `1. O código de rastreio é enviado por e-mail em até 48h após a confirmação do pagamento.
2. O prazo de entrega conta em dias úteis a partir do envio, não da compra.
3. Se o rastreio está parado há mais de 5 dias úteis, um especialista abre a investigação com a transportadora.
Para pedidos com status "entregue" que não chegaram, responda aqui — esse caso é tratado por um humano.`,
    body_en: `1. The tracking code is e-mailed within 48h after payment confirmation.
2. Delivery time counts in business days from shipping, not purchase.
3. If tracking has been stuck for 5+ business days, a specialist opens an investigation with the carrier.
For orders marked "delivered" that never arrived, reply here — a human handles that case.`,
  },
  {
    title: "Política de reembolso e devolução",
    topic: "Refund request",
    tags: "refund return money back reembolso devolução estorno",
    questions: ["I want a refund", "How do I return the product?", "Quero meu dinheiro de volta", "Como faço a devolução?"],
    body: `- Arrependimento: até 7 dias corridos após o recebimento (CDC art. 49), produto sem uso e na embalagem.
- Defeito: até 90 dias, após análise técnica.
- O reembolso é feito no mesmo meio de pagamento e depende de aprovação de um especialista.
A IA não aprova reembolsos: o caso é sempre encaminhado para um humano.`,
    body_en: `- Change of mind: up to 7 days after delivery, unused product in original packaging.
- Defect: up to 90 days, after technical review.
- Refunds go back to the original payment method and require specialist approval.
The AI never approves refunds: the case is always routed to a human.`,
  },
  {
    title: "Cancelamento de assinatura",
    topic: "Cancellation request",
    tags: "cancel subscription cancellation cancelar assinatura",
    questions: ["I want to cancel my subscription", "How do I cancel?", "Quero cancelar minha assinatura", "Como cancelo?"],
    body: `O cancelamento pode ser feito a qualquer momento e o acesso continua até o fim do período já pago.
Um especialista entra em contato para confirmar o cancelamento e entender o motivo — às vezes conseguimos resolver o problema que levou a ele.`,
    body_en: `You can cancel at any time and keep access until the end of the paid period.
A specialist will contact you to confirm the cancellation and understand the reason — sometimes we can fix what caused it.`,
  },
  {
    title: "Formas de pagamento e segunda via de fatura",
    topic: "Payment issue",
    tags: "payment invoice billing card boleto pix pagamento fatura segunda via",
    questions: ["How can I get a copy of my invoice?", "Payment methods accepted", "My card was declined", "Como emito a segunda via da fatura?", "Quais formas de pagamento?", "Meu cartão foi recusado"],
    body: `- Aceitamos cartão de crédito (até 12x), Pix e boleto.
- A segunda via da fatura fica em Minha Conta > Faturas.
- Cartão recusado: confirme limite, validade e se compras online estão habilitadas no app do banco; depois tente novamente.
Cobranças em duplicidade ou valores que você não reconhece são analisados por um especialista.`,
    body_en: `- We accept credit card (up to 12 installments), Pix and boleto.
- Invoice copies are in My Account > Invoices.
- Card declined: check limit, expiry and that online purchases are enabled in your bank app, then retry.
Duplicate or unrecognized charges are reviewed by a specialist.`,
  },
  {
    title: "Defeito de hardware e garantia",
    topic: "Hardware issue",
    tags: "hardware broken defect warranty not turning on garantia defeito quebrado não liga",
    questions: ["My device won't turn on", "Hardware issue", "The product is broken", "Meu aparelho não liga", "Produto com defeito", "There seems to be a hardware problem"],
    body: `1. Carregue por 1 hora com o carregador original e tente ligar segurando o botão por 15 segundos.
2. Verifique danos visíveis (líquido, quedas) — eles não são cobertos pela garantia.
3. A garantia é de 12 meses. Para abrir, responda com o número do pedido e uma foto/vídeo do problema; um especialista avalia e envia a etiqueta de postagem.`,
    body_en: `1. Charge for 1 hour with the original charger and hold the power button for 15 seconds.
2. Check for visible damage (liquid, drops) — not covered by warranty.
3. Warranty is 12 months. Reply with your order number and a photo/video; a specialist reviews it and sends a shipping label.`,
  },
  {
    title: "Backup e recuperação de dados",
    topic: "Data loss",
    tags: "backup restore data loss recover files backup recuperar dados arquivos",
    questions: ["How do I back up my data?", "How do I restore a backup?", "Como faço backup?", "Como restaurar meus arquivos?"],
    body: `- Backup automático: Configurações > Conta > Backup (diário, via Wi-Fi).
- Restaurar: ao configurar o aparelho, escolha "Restaurar de backup" e entre na mesma conta.
Se você PERDEU dados, pare de usar o dispositivo imediatamente (evita sobrescrita) — um especialista assume o caso.`,
    body_en: `- Automatic backup: Settings > Account > Backup (daily, over Wi-Fi).
- Restore: during device setup choose "Restore from backup" and sign in with the same account.
If you LOST data, stop using the device immediately (prevents overwriting) — a specialist will take over.`,
  },
  {
    title: "Solicitar direitos de administrador",
    topic: "Administrative rights",
    tags: "admin administrator rights permission local admin direitos administrador permissão",
    questions: ["I need admin rights to install software", "Request administrator access", "Preciso de permissão de administrador", "Need local admin rights on my laptop"],
    body: `Direitos de administrador são concedidos por tempo limitado (24h) com aprovação do gestor.
1. Abra a solicitação informando o software e a justificativa.
2. O gestor aprova pelo e-mail.
3. O acesso é liberado automaticamente após a aprovação.`,
    body_en: `Admin rights are granted for a limited time (24h) with manager approval.
1. Open a request with the software name and justification.
2. Your manager approves by e-mail.
3. Access is granted automatically after approval.`,
  },
  {
    title: "Aumentar espaço de armazenamento e pastas compartilhadas",
    topic: "Storage",
    tags: "storage quota disk space shared folder drive armazenamento espaço pasta compartilhada",
    questions: ["My mailbox is full", "I need more storage space", "Access to shared folder", "Preciso de mais espaço", "Acesso à pasta compartilhada", "Caixa de e-mail cheia"],
    body: `1. Caixa cheia: esvazie a lixeira e arquive e-mails com mais de 1 ano.
2. Aumento de cota: solicite indicando o volume necessário; aumentos até 50 GB são aprovados automaticamente.
3. Pasta compartilhada: peça ao dono da pasta para adicionar seu e-mail, ou solicite informando o caminho da pasta.`,
    body_en: `1. Full mailbox: empty the trash and archive e-mails older than 1 year.
2. Quota increase: request it with the needed size; up to 50 GB is auto-approved.
3. Shared folder: ask the folder owner to add your e-mail, or request it with the folder path.`,
  },
  {
    title: "Solicitar compra de equipamento ou licença",
    topic: "Purchase",
    tags: "purchase order quote license buy equipment compra cotação licença equipamento",
    questions: ["I need to purchase a new laptop", "Request a software license", "How do I request a quote?", "Preciso comprar uma licença", "Como peço cotação de equipamento?"],
    body: `1. Abra a solicitação com item, quantidade e centro de custo.
2. Compras até R$ 5.000 seguem com aprovação do gestor; acima disso, também de Financeiro.
3. O time de compras envia a cotação em até 3 dias úteis.`,
    body_en: `1. Open a request with item, quantity and cost center.
2. Purchases up to R$ 5,000 need manager approval; above that, Finance too.
3. Procurement sends the quote within 3 business days.`,
  },
];
