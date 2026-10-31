#!/usr/bin/env python3
"""Gera casamento/data.json a partir da planilha Google Sheets "Casamento".
Abas: Gastos, Pagamentos, Cronograma, Resumo (cabeçalhos localizados pelo NOME da coluna, em qualquer linha/ordem).
Entrada: JSON do read_range (4 ranges nessa ordem) ou 4 CSVs:
  python3 build_data.py raw.json > data.json
  python3 build_data.py --csv Gastos.csv Pagamentos.csv Cronograma.csv Resumo.csv [--exemplo] > data.json
Totais por categoria/fornecedor e meta x projeção são calculados AQUI (o Resumo da planilha só fornece
ORÇAMENTO por categoria + META e DATA DO CASAMENTO)."""
import sys,json,csv,io,re,datetime,unicodedata
def load(a):
  if a[1]=='--csv': return [open(p,encoding='utf-8').read() for p in a[2:6]]
  s=open(a[1],encoding='utf-8').read(); s=s[s.index('{'):s.rindex('}')+1]
  return [r['content'] for r in json.loads(s)['ranges']]
def norm(s): return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower()).strip()
def rows(t): return list(csv.reader(io.StringIO(t.strip('\n'))))
def num(x):
  if x in (None,'','-'): return 0.0
  try: return float(x)
  except: return float(re.sub(r'[^\d,.-]','',x).replace('.','').replace(',','.') or 0)
def dt(x):
  if x in (None,'','-'): return None
  try: return (datetime.date(1899,12,30)+datetime.timedelta(days=int(float(x)))).isoformat()
  except:
    m=re.match(r'(\d+)/(\d+)/(\d+)',x)
    if m: d,mo,y=map(int,m.groups()); y+=2000 if y<100 else 0; return f'{y:04d}-{mo:02d}-{d:02d}'
    m=re.match(r'(\d{4})-(\d\d)-(\d\d)',x); return m.group(0) if m else None
def table(t,need):
  """Acha a linha de cabeçalho que contém a coluna `need`; devolve lista de dicts com chaves normalizadas."""
  g=rows(t)
  for i,r in enumerate(g):
    h=[norm(c) for c in r]
    if norm(need) in h:
      out=[]
      for x in g[i+1:]:
        if not any(c.strip() for c in x): continue
        x=x+['']*(len(h)-len(x)); out.append({h[j]:x[j].strip() for j in range(len(h)) if h[j]})
      return out
  return []
def col(r,*names):
  for n in names:
    v=r.get(norm(n))
    if v not in (None,''): return v
  return ''
FECHADO={'Contratado','Em andamento','Finalizado'}
G,P,C,R=load(sys.argv)
gastos=[]
for r in table(G,'FORNECEDOR'):
  if not col(r,'FORNECEDOR','DESCRIÇÃO'): continue
  st=col(r,'STATUS') or 'Não iniciado'; orc=num(col(r,'ORÇADO')); fe=num(col(r,'VALOR FECHADO')); pg=num(col(r,'PAGO'))
  tipo='cancelado' if st=='Cancelado' else ('fechado' if st in FECHADO else 'planejado')
  gastos.append(dict(data=dt(col(r,'DATA')),fornecedor=col(r,'FORNECEDOR'),desc=col(r,'DESCRIÇÃO'),cat=col(r,'CATEGORIA') or 'Outros/Imprevistos',
    status=st,tipo=tipo,orcado=orc,fechado=fe,pago=pg,restante=round((fe-pg) if tipo=='fechado' else 0,2),
    parcelas=col(r,'Nº PARCELAS'),proxVenc=dt(col(r,'PRÓX. VENCIMENTO','PROX VENCIMENTO')),evento=dt(col(r,'DATA EVENTO/ENTREGA')),
    contato=col(r,'CONTATO'),obs=col(r,'OBSERVAÇÃO')))
mov=[]
for r in table(P,'PARCELA'):
  s=norm(col(r,'STATUS')); d=dt(col(r,'DATA'))
  st='pago' if s.startswith('pag') else ('atrasada' if s.startswith('atras') else 'previsto')
  if st=='previsto' and d and d<datetime.date.today().isoformat(): st='atrasada'
  f=col(r,'FORNECEDOR'); cat=next((g['cat'] for g in gastos if g['fornecedor']==f),'')
  mov.append(dict(data=d,fornecedor=f,desc=col(r,'DESCRIÇÃO'),parcela=col(r,'PARCELA'),valor=num(col(r,'VALOR')),status=st,forma=col(r,'FORMA'),cat=cat))
cron=[dict(data=dt(col(r,'DATA')),resp=col(r,'RESPONSÁVEL'),tarefa=col(r,'TAREFA'),cat=col(r,'CATEGORIA'),obs=col(r,'OBSERVAÇÃO'),status=col(r,'STATUS'),tipo=col(r,'TIPO'))
      for r in table(C,'TAREFA') if col(r,'TAREFA')]
# Resumo: ORÇAMENTO por categoria + células META / DATA DO CASAMENTO (formato "ROTULO,valor" em qualquer linha)
orcCat={};meta=0;data=None
for r in table(R,'ORÇAMENTO'):
  c=col(r,'CATEGORIA')
  if c and norm(c)!='total geral': orcCat[c]=num(col(r,'ORÇAMENTO'))
RR=rows(R)
def cell(r,c):  # posição fixa: I1 = meta, I2 = data (mesmo sem rótulo)
  return RR[r][c].strip() if len(RR)>r and len(RR[r])>c else ''
meta=num(cell(0,8)); data=dt(cell(1,8))
for x in RR:
  x=x+['']
  for j,c in enumerate(x[:-1]):
    if norm(c) in ('meta','meta geral','orcamento total'): meta=meta or num(x[j+1])
    if norm(c) in ('data do casamento','data casamento'): data=data or dt(x[j+1])
def agg(key):
  o={}
  for g in gastos:
    a=o.setdefault(g[key] or '—',dict(nome=g[key] or '—',orcamento=0,orcado=0,fechado=0,pago=0,restante=0,planejado=0,itens=0,cancelados=0))
    if g['tipo']=='cancelado': a['cancelados']+=1; continue
    a['itens']+=1; a['orcado']+=g['orcado']; a['pago']+=g['pago']
    if g['tipo']=='fechado': a['fechado']+=g['fechado']; a['restante']+=g['restante']
    else: a['planejado']+=g['orcado'] or g['fechado']
  for a in o.values(): a['projecao']=round(a['fechado']+a['planejado'],2)
  return o
cats=agg('cat')
for c,v in orcCat.items():
  cats.setdefault(c,dict(nome=c,orcado=0,fechado=0,pago=0,restante=0,planejado=0,projecao=0,itens=0,cancelados=0))['orcamento']=v
for a in cats.values(): a.setdefault('orcamento',orcCat.get(a['nome'],0))
forn=agg('fornecedor')
at=[g for g in gastos if g['tipo']!='cancelado']
fe=sum(g['fechado'] for g in at if g['tipo']=='fechado'); pl=sum(g['orcado'] or g['fechado'] for g in at if g['tipo']=='planejado')
eco=sum(g['orcado']-g['fechado'] for g in at if g['tipo']=='fechado' and g['orcado']>0)
pago=sum(g['pago'] for g in at)
totais=dict(meta=meta,fechado=round(fe,2),planejado=round(pl,2),projecao=round(fe+pl,2),saldo=round(meta-fe-pl,2),pago=round(pago,2),
  aPagar=round(fe-sum(g['pago'] for g in at if g['tipo']=='fechado'),2),economia=round(eco,2),itens=len(at))
sk=lambda d:sorted(d.values(),key=lambda a:-(a['projecao'] or a['orcamento']))
json.dump(dict(exemplo=('--exemplo' in sys.argv),geradoEm=datetime.datetime.now().astimezone().isoformat(timespec='minutes'),
  fonte='EXEMPLO (dados fictícios)' if '--exemplo' in sys.argv else 'Google Sheets "Casamento"',dataCasamento=data,totais=totais,
  categorias=sk(cats),fornecedores=sk(forn),gastos=gastos,movimentos=sorted(mov,key=lambda m:m['data'] or ''),cronograma=cron),
  sys.stdout,ensure_ascii=False,indent=1)
