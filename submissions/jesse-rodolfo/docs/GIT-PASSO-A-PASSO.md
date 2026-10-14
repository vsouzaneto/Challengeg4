# Git: do fork ao PR

1. No GitHub, abrir https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge e clicar em Fork.
2. Clonar o seu fork:
   git clone https://github.com/jesserodolfo/ai-master-challenge.git
   cd ai-master-challenge
3. Criar a branch:
   git checkout -b submission/jesse-rodolfo
4. Copiar o conteúdo deste kit para submissions/jesse-rodolfo/
5. Abrir o Claude Code DENTRO da pasta submissions/jesse-rodolfo/ (é lá que está o CLAUDE.md):
   cd submissions/jesse-rodolfo
   claude
6. Commit por bloco (mensagens na tabela do CLAUDE.md).
   ATENÇÃO: o .gitignore da raiz do repositório do G4 ignora a pasta submissions/ inteira.
   Não edite o .gitignore deles (é arquivo fora da sua pasta). E o -f sozinho forçaria também os CSVs brutos.
   Por isso use SEMPRE o script da pasta, que força a adição mas exclui raw/, .venv e caches, e trava se algo errado entrar:
   bash submissions/jesse-rodolfo/commit.sh "bloco0: leitura do problema e hipoteses"
   Depois: git push
7. Push:
   git push -u origin submission/jesse-rodolfo
8. No GitHub, abrir Pull Request do seu fork para a main do repositório original.
   Título, no formato exigido por eles (copiar igual, inclusive o traço):
   [Submission] Jessé Rodolfo Machado — Challenge 002
9. Antes de abrir o PR, conferir: git diff main --stat só mostra arquivos dentro de submissions/jesse-rodolfo/

Checklist do CONTRIBUTING.md:
- [ ] Li o README do challenge 002 completo
- [ ] Solução está em submissions/jesse-rodolfo/
- [ ] Process log com evidências incluído
- [ ] README da submissão segue o template
- [ ] Instruções de setup do protótipo incluídas
- [ ] Nenhum arquivo fora da minha pasta foi modificado
