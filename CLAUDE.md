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
2. Reaplicar correções de bug que se perderam no alinhamento PC→Mac:
   - ~~Restaurar **previsão** da lixeira (`LIX_TIPOS`).~~ ✅ **FEITO em 2026-06-20 (Mac)** — chave `previsao` adicionada.
   - ~~`cloudApply` chamar `ajustarCounters`.~~ ✅ **FEITO em 2026-06-20 (Mac)** — `try{ajustarCounters();}catch(e){}` adicionado no fim do `cloudApply`.
   - ~~`htStreak` usar `htDone`.~~ ✅ **FEITO em 2026-06-20 (Mac)** — investigado: era bug real só p/ hábitos `metrica:'soma'` (log com valor 0 inflava a sequência). `htStreak` agora gateia em `htDone(h,log)`.
3. **(ALTO, em aberto) Robustez do sync com o Supabase** — last-write-wins sem trava pode sobrescrever dados mais novos da nuvem. Ver detalhe no handoff de 2026-06-20 (cont. 2). Desenhar antes de implementar: no boot, `cloudPull` + comparar `updated_at` antes de empurrar; guarda anti-estado-vazio no `cloudPush`; flush do push no `beforeunload`.

## Log de handoff (a sessão mais recente escreve no topo)
- **2026-06-20 — Mac (casa) (cont. 2):** Varredura de bugs no `index.html`. Portei a correção **#2** (`htStreak`): agora busca o hábito e só conta o dia na sequência quando `htDone(h,log)` é true (gateia a meta `'soma'` — antes qualquer log, mesmo valor 0, inflava o streak; booleanos não mudam). Guarda `if(!h)return 0` evita erro com log órfão. **Achado ALTO ainda em aberto (não mexido):** sync é last-write-wins sem trava — no boot `cloudInit` faz `if(isDirty())cloudPush()` (empurra sem puxar/comparar), `cloudPush` não compara `updated_at` nem barra estado vazio, e `beforeunload` só faz `saveAllFlush` (não faz flush do push debounced 1800ms). Risco de uma máquina sobrescrever dados mais novos da nuvem. Decidir desenho antes de mexer (pull-first + comparar `updated_at` / guarda anti-vazio). Commit + push.
- **2026-06-20 — Mac (casa) (cont.):** Portei a correção **#3**: `cloudApply` agora chama `try{ajustarCounters();}catch(e){}` no fim (junto dos repairs), após aplicar os dados do Supabase. Antes só o `loadAll` chamava — então, após um sync da nuvem com IDs de Casamento mais altos que o `casCounter`, o próximo item de Casamento podia colidir/sobrescrever. `ajustarCounters` só eleva `casCounter` (max id +1), idempotente, não toca em dados. Resta só a #2 (`htStreak`/`htDone`, não portar às cegas). Commit + push.
- **2026-06-20 — Mac (casa):** Alinhei o Mac ao `origin/main` (fast-forward, 12 commits do PC). Antes disso, nesta sessão do Mac: tema escuro migrado de azul-marinho para **grafite neutro/quente** (só o bloco `body.dark`; header Copa/bandeira mantido). Depois do pull, portei a correção **#1 da pendência**: a lixeira não tinha a chave `previsao` em `LIX_TIPOS` → o restore já funcionava (o `case 'previsao'` existe no `lixRestaurar`), mas o rótulo aparecia como "previsao" cru e a tela não atualizava ao restaurar. Adicionei `previsao:{nome:'Previsão',render:renderPrevisao}`. **Ainda pendentes (não portadas):** #2 `htStreak` usar `htDone` (NÃO portar às cegas — o `htStreak` atual calcula via `htLogs`; investigar o bug real antes) e #3 `cloudApply` chamar `ajustarCounters` (confirmado ausente; baixo risco, candidato a portar). Commit + push.
- **2026-06-20 — PC da Empresa (cont. 10):** Checklist: seções começam **todas recolhidas** a cada load. Nova `clCollapseAll()` (fecha todas as seções de `clData`) chamada no boot após `loadAll` e no fim do `cloudApply`. Toggle segue normal na sessão. Commit + push.
- **2026-06-20 — PC da Empresa (cont. 9):** Reapliquei a correção do **checklist em branco** (itens só apareciam após recolher/expandir): `clAutoGrow` não zera altura quando oculto + `setCLTab`/`setTab2` re-renderizam o painel ao ficar visível. ⚠️ Essa correção (e a do filtro de erro de extensão) tinham se PERDIDO no alinhamento PC→Mac. **Possíveis outras correções do PC ainda NÃO portadas pro Mac** (reaplicar se aparecerem): restaurar previsão da lixeira (`LIX_TIPOS`), `htStreak` usar `htDone`, `cloudApply` chamar `ajustarCounters`. Commit + push.
- **2026-06-20 — PC da Empresa (cont. 8):** Roteiro: clicar no dia agora abre um **modal central** (`#modalDiaView`) com a timeline pra ver/editar, em vez de expandir inline. Novos `openDiaView()`/`renderDiaView()`/`diaViewIdx`; reusa `roteiroStop`; footer com "Editar dia" e "Adicionar parada" (abrem `modalDia`/`modalStop` por cima). `saveStop`/`delStop`/`saveDia` chamam `renderDiaView()` pra atualizar o modal aberto. (`toggleDia` ficou sem uso, mantido inofensivo.) Commit + push.
- **2026-06-20 — PC da Empresa (cont. 7):** Estado inicial no refresh: (1) 5 grupos da sidebar começam recolhidos (`sb-group collapsed` estático + `sbGroupsOpen=false` + ícone `ti-fold-up`); (2) nada selecionado (removido `active` de `page-casamento` e `nav-cas-convidados`); (3) nova `#page-welcome` (ativa) com `.coming-soon` "Selecione uma área no menu…". Init ajustado pra limpar seleção e cair na welcome. Commit + push.
- **2026-06-20 — PC da Empresa (cont. 6):** Roteiro: (1) lista em **2 colunas** (`.roteiro-list` virou grid 1fr 1fr, com fallback 1 coluna em ≤760px); (2) bug corrigido — `roteiroDiaRico` tinha `dia-chevron open`/`dia-body open` fixos → dias nasciam expandidos no refresh. Removido (agora começam recolhidos). Commit + push.
- **2026-06-20 — PC da Empresa (cont. 5):** Cards do Roteiro mais compactos (`.dia-header` padding .85→.5rem, `.dia-header-rico` 1rem→.55rem, `.dia-num` 28→24px, `.dia-num-rico` 34→26px). Commit + push.
- **2026-06-20 — PC da Empresa (cont. 4):** Itens menores no `index.html`: botão "Exportar HTML" no menu de config estava só com ícone → adicionei o texto e alinhei ao estilo do menu. Commit + push.
- **2026-06-20 — PC da Empresa (cont. 3):** Mesclei os dias 2–5 detalhados do roteiro no SEED do `index.html` (substituindo os dias simples). O `roteiroRepair` (via `cloudApply`) re-injeta por cima do roteiro simples do Supabase → roteiro detalhado aparece **sem mexer no Supabase**. Removi o `roteiro-detalhado-dias-1-5.js`. Commit + push. **No Mac: `git pull` antes de editar.**
- **2026-06-20 — PC da Empresa (cont. 2):** Bug na versão do Mac: o `#config-menu` (menu da engrenagem) estava com `style="display: block"` fixo no HTML → abria sozinho a cada refresh. Troquei para `display: none`. Commit + push. **No Mac: `git pull` antes de editar o index.html.**
- **2026-06-20 — PC da Empresa (cont.):** Editei o `index.html` (versão do Mac) **a partir do PC**: reapliquei o filtro de erros de extensão no handler global de erro (`window.addEventListener('error'…` ignora `-extension://` e "Script error."). Isso tinha se perdido no alinhamento. Commit + push feitos → Pages atualiza e o banner "ERRO DETECTADO" (causado pela extensão Dashlane) some. **No Mac: dar `git pull` antes de editar o index.html** pra pegar essa mudança.
- **2026-06-20 — PC da Empresa:** Alinhei o PC ao Mac (git init + reset para `origin/main`). Criei este CLAUDE.md e o `roteiro-detalhado-dias-1-5.js`. Backup da versão paralela salvo localmente no PC. **Próximo passo (no Mac):** mesclar os dias 1–5 detalhados no `index.html` e dar push.
