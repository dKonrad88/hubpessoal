-- Gastos do Hub Pessoal
-- Projeto Supabase "Pessoal" (ref jlouesrrmqeauzlgvrpw).
-- Cada pessoa (Diego, Débora) entra com o próprio login e vê só as próprias linhas.
-- RLS: auth.uid() = user_id em todas as tabelas. Não há lista_id.
-- O app usa somente a chave anon/publishable. service_role fica fora do HTML;
-- a Edge Function gastos-gravador-ping (ainda não existe) é quem vai usá-la no servidor.
--
-- Contrato do Gravador (igual ao apto, sem lista):
--   1. O navegador sobe o áudio para o bucket privado gastos-audio em <user_id>/<id>.<ext>
--   2. Insere uma linha em gastos_gravador (tipo, duracao, audio_path, status pendente)
--   3. Faz POST em /functions/v1/gastos-gravador-ping com o Bearer do usuário
--   4. A função (quando existir) transcreve, interpreta e insere em gastos_propostas
--      com status pendente. Sem forma_pagamento e categoria_id o app não deixa aprovar.
--   5. Aprovar no app grava a linha em gastos_lancamentos (origem = gravador).
-- Enquanto a função não existir, a gravação fica salva e o ping só registra a falha.

-- ---------- categorias ----------
create table if not exists public.gastos_categorias (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
  nome text not null,
  cor text not null default '#8E8E93',
  palavras_chave text[] not null default '{}',
  ordem int not null default 0,
  unique (user_id, nome)
);

-- ---------- faturas (o PDF não é guardado; só o hash e o resumo) ----------
create table if not exists public.gastos_faturas (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
  banco text not null,
  cartao_final text not null,
  ano int not null check (ano between 2000 and 2100),
  mes int not null check (mes between 1 and 12),
  vencimento date,
  total numeric(14,2) not null,
  pdf_hash text not null,
  nome_arquivo text,
  importado_em timestamptz not null default now(),
  unique (user_id, banco, cartao_final, ano, mes),
  unique (user_id, pdf_hash)
);

-- ---------- gravador ----------
create table if not exists public.gastos_gravador (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
  autor_nome text,
  tipo text not null default 'auto',
  audio_path text,
  duracao numeric,
  status text not null default 'pendente',
  transcricao text,
  resposta text,
  processado boolean not null default false,
  processado_em timestamptz,
  created_at timestamptz not null default now()
);

-- ---------- propostas (o assistente grava; a pessoa aprova ou recusa) ----------
create table if not exists public.gastos_propostas (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
  gravacao_id uuid references public.gastos_gravador (id) on delete set null,
  tipo text not null default 'gasto',
  titulo text,
  descricao text,
  valor numeric(14,2),
  data date,
  forma_pagamento text,
  categoria_id uuid references public.gastos_categorias (id) on delete set null,
  transcricao text,
  extra jsonb not null default '{}'::jsonb,
  status text not null default 'pendente' check (status in ('pendente', 'aprovado', 'recusado')),
  ref text,
  decidido_em timestamptz,
  created_at timestamptz not null default now(),
  constraint gastos_propostas_forma check (
    forma_pagamento is null or forma_pagamento in ('cartao', 'pix', 'dinheiro')
  ),
  constraint gastos_propostas_aprovar check (
    status <> 'aprovado'
    or (forma_pagamento is not null and categoria_id is not null and valor is not null and valor > 0)
  )
);

-- ---------- lançamentos (PDF ou Gravador; não há inclusão manual) ----------
create table if not exists public.gastos_lancamentos (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
  fatura_id uuid references public.gastos_faturas (id) on delete cascade,
  proposta_id uuid references public.gastos_propostas (id) on delete set null,
  ano int not null check (ano between 2000 and 2100),
  mes int not null check (mes between 1 and 12),
  data date,
  hora text,
  cidade text,
  modalidade text,
  descricao text not null,
  parcela_n int,
  parcela_total int,
  valor_usd numeric(14,2),
  cotacao numeric(14,6),
  valor_brl numeric(14,2) not null,
  categoria_id uuid references public.gastos_categorias (id) on delete set null,
  forma_pagamento text not null check (forma_pagamento in ('cartao', 'pix', 'dinheiro')),
  origem text not null check (origem in ('pdf', 'gravador')),
  cartao text,
  recorrente boolean not null default false,
  created_at timestamptz not null default now()
);

create unique index if not exists gastos_lancamentos_proposta_uk
  on public.gastos_lancamentos (proposta_id) where proposta_id is not null;

-- ---------- metas (um teto mensal por categoria) ----------
create table if not exists public.gastos_metas (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
  categoria_id uuid not null references public.gastos_categorias (id) on delete cascade,
  valor_mensal numeric(14,2) not null check (valor_mensal > 0),
  vigente_desde date not null default current_date,
  unique (user_id, categoria_id)
);

-- ---------- índices ----------
create index if not exists gastos_lancamentos_periodo_idx on public.gastos_lancamentos (user_id, ano, mes);
create index if not exists gastos_lancamentos_cat_idx on public.gastos_lancamentos (user_id, categoria_id);
create index if not exists gastos_lancamentos_fatura_idx on public.gastos_lancamentos (fatura_id);
create index if not exists gastos_faturas_periodo_idx on public.gastos_faturas (user_id, ano, mes);
create index if not exists gastos_propostas_status_idx on public.gastos_propostas (user_id, status);
create index if not exists gastos_gravador_quando_idx on public.gastos_gravador (user_id, created_at desc);
create index if not exists gastos_metas_user_idx on public.gastos_metas (user_id);

-- ---------- RLS ----------
alter table public.gastos_categorias enable row level security;
alter table public.gastos_faturas enable row level security;
alter table public.gastos_lancamentos enable row level security;
alter table public.gastos_metas enable row level security;
alter table public.gastos_gravador enable row level security;
alter table public.gastos_propostas enable row level security;

-- Um policy por comando, só authenticated, sempre a própria linha.
do $$
declare
  t text;
begin
  foreach t in array array[
    'gastos_categorias', 'gastos_faturas', 'gastos_lancamentos',
    'gastos_metas', 'gastos_gravador', 'gastos_propostas'
  ]
  loop
    execute format('drop policy if exists %I_select on public.%I', t, t);
    execute format('drop policy if exists %I_insert on public.%I', t, t);
    execute format('drop policy if exists %I_update on public.%I', t, t);
    execute format('drop policy if exists %I_delete on public.%I', t, t);
    execute format('create policy %I_select on public.%I for select to authenticated using (user_id = auth.uid())', t, t);
    execute format('create policy %I_insert on public.%I for insert to authenticated with check (user_id = auth.uid())', t, t);
    execute format('create policy %I_update on public.%I for update to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid())', t, t);
    execute format('create policy %I_delete on public.%I for delete to authenticated using (user_id = auth.uid())', t, t);
  end loop;
end $$;

-- anon não lê nem escreve. authenticated e service_role sim (a função do gravador usa service_role no servidor).
do $$
declare
  t text;
begin
  foreach t in array array[
    'gastos_categorias', 'gastos_faturas', 'gastos_lancamentos',
    'gastos_metas', 'gastos_gravador', 'gastos_propostas'
  ]
  loop
    execute format('revoke all on public.%I from anon', t);
    execute format('revoke truncate, references, trigger on public.%I from authenticated', t);
    execute format('grant select, insert, update, delete on public.%I to authenticated', t);
    execute format('grant select, insert, update, delete on public.%I to service_role', t);
  end loop;
end $$;

-- ---------- áudio privado, uma pasta por usuário ----------
insert into storage.buckets (id, name, public)
values ('gastos-audio', 'gastos-audio', false)
on conflict (id) do update set public = false;

drop policy if exists gastos_audio_select on storage.objects;
drop policy if exists gastos_audio_insert on storage.objects;
drop policy if exists gastos_audio_update on storage.objects;
drop policy if exists gastos_audio_delete on storage.objects;

create policy gastos_audio_select on storage.objects
  for select to authenticated
  using (
    bucket_id = 'gastos-audio'
    and (storage.foldername(name))[1] = auth.uid()::text
  );

create policy gastos_audio_insert on storage.objects
  for insert to authenticated
  with check (
    bucket_id = 'gastos-audio'
    and (storage.foldername(name))[1] = auth.uid()::text
  );

create policy gastos_audio_update on storage.objects
  for update to authenticated
  using (
    bucket_id = 'gastos-audio'
    and (storage.foldername(name))[1] = auth.uid()::text
  )
  with check (
    bucket_id = 'gastos-audio'
    and (storage.foldername(name))[1] = auth.uid()::text
  );

create policy gastos_audio_delete on storage.objects
  for delete to authenticated
  using (
    bucket_id = 'gastos-audio'
    and (storage.foldername(name))[1] = auth.uid()::text
  );

-- ---------- realtime: a tela Aprovar atualiza quando a proposta chegar ----------
alter table public.gastos_gravador replica identity full;
alter table public.gastos_propostas replica identity full;

do $$
begin
  if not exists (
    select 1 from pg_publication_tables
    where pubname = 'supabase_realtime' and schemaname = 'public' and tablename = 'gastos_gravador'
  ) then
    alter publication supabase_realtime add table public.gastos_gravador;
  end if;
  if not exists (
    select 1 from pg_publication_tables
    where pubname = 'supabase_realtime' and schemaname = 'public' and tablename = 'gastos_propostas'
  ) then
    alter publication supabase_realtime add table public.gastos_propostas;
  end if;
end $$;
