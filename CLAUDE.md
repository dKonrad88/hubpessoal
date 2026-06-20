# HUB Pessoal — memória compartilhada entre máquinas (Claude Code)

> As sessões do Claude Code do **Mac (casa)** e do **PC da Empresa** NÃO compartilham histórico de chat.
> A única coisa compartilhada é **este repositório git**. Por isso este arquivo é a memória comum.
> **No início de cada sessão:** dê `git pull` e leia este arquivo. **No fim:** atualize o "Log de handoff" e dê `git add -A && git commit && git push`.

## Projeto
- App pessoal **single-file**: `index.html` (HTML/CSS/JS, minificado em linhas longas).
- Publicado no **GitHub Pages**: https://dkonrad88.github.io/hubpessoal/
- Repo: `github.com/dkonrad88/hubpessoal` — branch **`main`**.
- Áreas: Viagem Orlando (roteiro, checklists, gastos, documentos), Casamento (gastos, convidados, tarefas), Hábitos, Metas, etc.

## Onde vivem os dados (NÃO PERDER)
- **Código/layout** → `index.html` (versionado no git). Mudanças de layout vão pelo git/Codespace.
- **Dados do usuário** (checklists, convidados, gastos de viagem e casamento, hábitos…) → **Supabase** (sync na nuvem, dentro do app). **NÃO** ficam no git.
- ⚠️ **Regra de ouro:** nunca deixar o app subir um estado vazio/parcial por cima do Supabase. Antes de importar dados, garantir que o app já puxou a nuvem (senão um push sobrescreve a nuvem).

## Fluxo entre as duas máquinas
O usuário avisa onde está; o Claude Code cuida do git:
- Usuário diz **"tô no PC da Empresa"** ou **"tô no Mac"**.
- **Ao começar:** `git pull` + ler este CLAUDE.md.
- **Ao terminar:** atualizar o "Log de handoff" abaixo, `git add -A`, `git commit -m "..."`, `git push`.
- **Mac (casa)** = máquina canônica de desenvolvimento (Codespace). **PC da Empresa** = alinhado e conectado, uso ocasional.
- `git pull` funciona nas duas (repo público). `git push` no PC precisa de login do GitHub configurado (token) — resolver na 1ª vez.

## Estado atual (2026-06-20, sessão do PC da Empresa)
- O PC foi **alinhado ao Mac** hoje: `index.html` do PC = `origin/main` (versão "grafite neutro", ~831 KB).
- Antes, o PC tinha uma versão paralela (~401 KB) com coisas que o Mac **não tem**:
  - **Roteiro detalhado Dias 1–5** (Vineland Premium Outlets, Keke's, Ford's Garage… timeline rica com `stops`).
  - Tema "Copa/Brasil" → **descartado** (o Mac seguiu pra "grafite neutro").
  - Correções de bug: restaurar **previsão** da lixeira (faltava em `LIX_TIPOS`); `htStreak` alinhado ao `htDone`; `cloudApply` chamando `ajustarCounters`; checklist `clAutoGrow` (textarea com altura 0 quando a aba está oculta); handler global de erro ignorando erros de extensão do navegador.
- Backup da versão paralela do PC: `index.BACKUP-pre-git-20260620-1020.html` (local no PC, **não** versionado).

## Pendências (fazer no Mac)
1. **Trazer o roteiro detalhado Dias 1–5 para o Mac.** O conteúdo (JS verbatim) está em **`roteiro-detalhado-dias-1-5.js`** (versionado, chega no Mac via git). No `index.html` do Mac, no array `const roteiro=[ ... ]`, substituir os objetos dos dias 1 a 5 por esses. Fazer no **código** (não importar como dado) pra não conflitar com o sync do Supabase. Depois apagar o arquivo `.js`.
2. (Opcional) Reaplicar as correções de bug listadas acima no código do Mac, se as mesmas funções existirem lá.

## Log de handoff (a sessão mais recente escreve no topo)
- **2026-06-20 — PC da Empresa:** Alinhei o PC ao Mac (git init + reset para `origin/main`). Criei este CLAUDE.md e o `roteiro-detalhado-dias-1-5.js`. Backup da versão paralela salvo localmente no PC. **Próximo passo (no Mac):** mesclar os dias 1–5 detalhados no `index.html` e dar push.
