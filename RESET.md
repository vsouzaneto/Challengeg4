# RESET.md

git clone git@github.com:adrianoaguiar/ai-master-challenge.git ai-master-challenge && cd ai-master-challenge

git remote set-url origin git@github.com:adrianoaguiar/ai-master-challenge.git
git remote add remote_site git@github.com:Gestao-Quatro-Ponto-Zero/ai-master-challenge.git
git remote -v

for remote in `git branch -r`; do git branch --track ${remote#remote_site/} $remote; done && \
git fetch --all --tags

--- se WINDOWS:

git branch -r | ForEach-Object { $r = $_.Trim(); $b = $r -replace '^origin/'; if ($b -notmatch '->') { git branch --track $b $r } } ; git fetch --all --tags

---

git fetch -u remote_site +refs/heads/*:refs/heads/*
git fetch -u remote_site +refs/tags/*:refs/tags/*

git push origin --mirror

--- RESET HISTÓRICO DE COMMITS E SERÁ NECESSÁRIO FAZER UMA LIMPEZA GRADATIVA NAS ESTRUTURAS DE MÓDULOS EXISTENTES:

git remote -v

git log --oneline

git add -A

git reset --soft $(git rev-list --max-parents=0 HEAD)

git commit -n -m "Initial commit AI MASTER CHALLENGE"

git push --force origin master

https://github.com/adrianoaguiar/ai-master-challenge.git