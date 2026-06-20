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

## Pendências
1. ~~Trazer o roteiro detalhado Dias 1–5 para o Mac.~~ ✅ **FEITO em 2026-06-20** (no PC): os dias 2–5 detalhados foram mesclados no SEED do `const roteiro` em `index.html`. O `roteiroRepair` (chamado pelo `cloudApply`) re-injeta esses `stops` por cima do roteiro simples do Supabase — sem tocar no Supabase. Arquivo `roteiro-detalhado-dias-1-5.js` removido (já mesclado).
2. (Opcional) Reaplicar as correções de bug listadas acima no código do Mac, se as mesmas funções existirem lá.

## Log de handoff (a sessão mais recente escreve no topo)
- **2026-06-20 — PC da Empresa (cont. 3):** Mesclei os dias 2–5 detalhados do roteiro no SEED do `index.html` (substituindo os dias simples). O `roteiroRepair` (via `cloudApply`) re-injeta por cima do roteiro simples do Supabase → roteiro detalhado aparece **sem mexer no Supabase**. Removi o `roteiro-detalhado-dias-1-5.js`. Commit + push. **No Mac: `git pull` antes de editar.**
- **2026-06-20 — PC da Empresa (cont. 2):** Bug na versão do Mac: o `#config-menu` (menu da engrenagem) estava com `style="display: block"` fixo no HTML → abria sozinho a cada refresh. Troquei para `display: none`. Commit + push. **No Mac: `git pull` antes de editar o index.html.**
- **2026-06-20 — PC da Empresa (cont.):** Editei o `index.html` (versão do Mac) **a partir do PC**: reapliquei o filtro de erros de extensão no handler global de erro (`window.addEventListener('error'…` ignora `-extension://` e "Script error."). Isso tinha se perdido no alinhamento. Commit + push feitos → Pages atualiza e o banner "ERRO DETECTADO" (causado pela extensão Dashlane) some. **No Mac: dar `git pull` antes de editar o index.html** pra pegar essa mudança.
- **2026-06-20 — PC da Empresa:** Alinhei o PC ao Mac (git init + reset para `origin/main`). Criei este CLAUDE.md e o `roteiro-detalhado-dias-1-5.js`. Backup da versão paralela salvo localmente no PC. **Próximo passo (no Mac):** mesclar os dias 1–5 detalhados no `index.html` e dar push.
