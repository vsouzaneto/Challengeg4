# CODE — Boas práticas (Clean Code)

- Nomes que revelam intenção; funções pequenas, uma responsabilidade.
- Encapsule: carga de dados, features, análise, modelo e app em módulos separados.
- Sem duplicação; sem código morto; sem números mágicos (use constantes).
- Funções puras sempre que possível; I/O nas bordas.
- Cada arquivo começa com comentário breve (1–2 linhas) dizendo o que faz.
- Comentários explicam o *porquê*, não o *o quê*.
- Testes automatizados (`pytest`) para transformações, métricas e modelo; rodar antes de cada commit.
- Reprodutível: `requirements.txt` com versões fixas, seeds fixas, um comando para rodar tudo.
- Estatística honesta: reportar tamanho de efeito + IC/p-valor; comparar com controles (plataforma, faixa de creator, categoria).
- Commits pequenos e descritivos (o git history é evidência de processo).
