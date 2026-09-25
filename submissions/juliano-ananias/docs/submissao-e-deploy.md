# Guia Rápido: Deploy na Vercel & Submissão no GitHub

## 1. Deploy na Vercel (Produção com Domínio Próprio)

Como sua aplicação foi desenvolvida em **Next.js 16**, o deploy na Vercel leva menos de 2 minutos:

1. Acesse **[vercel.com](https://vercel.com)** e faça login com seu GitHub.
2. Clique em **"Add New..." > "Project"**.
3. Selecione o repositório da sua solução.
   - **Root Directory:** escolha a pasta `g4-lead-scorer-app` (ou a pasta do projeto onde está o `package.json`).
4. Em **Environment Variables**, adicione:
   - `GEMINI_API_KEY`: sua chave de API do Gemini
   - `NEXT_PUBLIC_DEMO_PASSWORD`: `g4master2026`
5. Clique em **Deploy**.
6. Para configurar seu domínio próprio:
   - Vá na aba **Settings > Domains**.
   - Digite seu domínio ou subdomínio (ex: `leads.seudominio.com.br`) e aponte a entrada CNAME para `cname.vercel-dns.com`.

---

## 2. Passo a Passo do Pull Request Oficial no G4

O desafio exige que a entrega seja feita via **Pull Request** para o repositório oficial:
`https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge`

### Se você usa o GitHub Desktop ou a interface web do GitHub:
1. Acesse o repositório original: [Gestao-Quatro-Ponto-Zero/ai-master-challenge](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge)
2. Clique no botão **Fork** (canto superior direito) para criar uma cópia na sua conta.
3. No seu fork, crie uma branch chamada:
   `submission/juliano-ananias`
4. Suba a pasta inteira `submissions/juliano-ananias/` com todo o seu conteúdo.
5. Abra um **Pull Request** do seu fork para a branch `main` do G4:
   - **Título do PR:** `[Submission] Juliano Ananias — Challenge 003`
   - **Descrição do PR:**
     - *Desafio Escolhido:* 003 — Lead Scorer (Vendas / RevOps)
     - *URL do App no ar:* `https://seu-dominio-ou-vercel.app` (e `http://localhost:3005` para teste local)
     - *Resumo da Abordagem:* Sistema em Next.js com design vítrico minimalista, condução em telas primárias ("Por onde começaremos a prospectar hoje?"), 4 filas de ação RevOps, explicabilidade algorítmica e copiloto Gemini 2.5 Flash com DeepResearch™.
     - *Tempo Investido:* ~5 horas.
