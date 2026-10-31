#!/usr/bin/env python3
"""Gera apto/data.json a partir da planilha Google Sheets "Apto".
Entrada: JSON do read_range (valueRenderOption=UNFORMATTED_VALUE) das abas Gastos, Cronograma, Resumo, Imóvel
(ou 4 CSVs exportados: python3 build_data.py --csv Gastos.csv Cronograma.csv Resumo.csv Imovel.csv).
Uso: python3 build_data.py raw.json > data.json"""
import sys,json,csv,io,re,datetime
def load(argv):
  if argv[1]=='--csv': return [open(p,encoding='utf-8').read() for p in argv[2:6]]
  s=open(argv[1],encoding='utf-8').read(); s=s[s.index('{'):s.rindex('}')+1]
  d=json.loads(s); return [r['content'] for r in d['ranges']]
def rows(t): return [r for r in csv.reader(io.StringIO(t.strip('\n'))) ]
def num(x):
  if x in (None,'','-'): return 0.0
  try: return float(x)
  except: return float(re.sub(r'[^\d,.-]','',x).replace('.','').replace(',','.') or 0)
def dt(x):
  if x in (None,'','-'): return None
  try: return (datetime.date(1899,12,30)+datetime.timedelta(days=int(float(x)))).isoformat()
  except: 
    m=re.match(r'(\d+)/(\d+)/(\d+)',x)
    if not m: return None
    d,mo,y=map(int,m.groups()); y+=2000 if y<100 else 0; return f'{y:04d}-{mo:02d}-{d:02d}'
G,C,R,I=load(sys.argv)
g=rows(G); h=[x for x in g if x and x[0]=='DATA'][0]; gi=g.index(h)
gastos=[]
for r in g[gi+1:]:
  if not any(r) or not r[1]: continue
  r+=['']*11
  gastos.append(dict(data=dt(r[0]),fornecedor=r[1],desc=r[2],qtd=r[3],total=num(r[4]),pago=num(r[5]),entrega=dt(r[7]),obs=r[8],comodo=r[9],cat=r[10]))
c=rows(C); cron=[dict(data=dt(r[0]),resp=r[1],tarefa=r[2],comodo=r[3],obs=r[4],status=r[5],tipo=r[6]) for r in c[1:] if r and r[0]]
res=rows(R); cats=[];coms=[];tot=None
for r in res[1:]:
  r+=['']*9
  if r[0] and r[0]!='TOTAL GERAL': coms.append(dict(nome=r[0],total=num(r[1]),pago=num(r[2]),restante=num(r[3])))
  if r[5] and r[5]!='TOTAL GERAL': cats.append(dict(nome=r[5],total=num(r[6]),pago=num(r[7]),restante=num(r[8])))
  if r[5]=='TOTAL GERAL' or r[0]=='TOTAL GERAL': tot=dict(total=num(r[6] or r[1]),pago=num(r[7] or r[2]),restante=num(r[8] or r[3]))
im=rows(I); ires={};parc=[];mode=0
for r in im:
  if not r or not r[0]: continue
  if r[0]=='ITEM': continue
  if r[0]=='Nº': mode=1; continue
  if mode==0: ires[r[0]]=r[1]
  elif r[0]!='TOTAL': parc.append(dict(n=int(float(r[0])),venc=dt(r[1]),tipo=r[2],previsto=num(r[3]),pago=num(r[4]),correcao=num(r[5]),status=r[6]))
# Pagamentos com data (a planilha não tem coluna de data de pagamento):
#  - padrão: o valor PAGO cai no mês da coluna DATA do lançamento;
#  - AJUSTES abaixo vêm das observações da planilha / aba Cronograma (editar aqui se mudar).
AJ_PAGO={'Estofare':[('2026-08-31',2/3,'Entrada (50%)'),('2026-10-30',1/3,'2ª parcela (25%)')]}
PREV=[('2026-11-03','Pedras Rossler','Restante em dinheiro (Cronograma 03/11)',4500),
      ('2026-11-06','Ronaldo Luís','Instalador · pago na sexta da semana trabalhada',5600)]+\
     [(f'{y}-{m:02d}-16','CR Mármores',f'Cartão {i+1}/5 (restante R$ 6.500)',1300) for i,(y,m) in enumerate([(2026,11),(2026,12),(2027,1),(2027,2),(2027,3)])]
mov=[]
for x in gastos:
  if x['pago']>0:
    for d,f,lab in AJ_PAGO.get(x['fornecedor'],[(x['data'],1,'')]):
      mov.append(dict(data=d,fornecedor=x['fornecedor'],desc=x['desc']+(' · '+lab if lab else ''),valor=round(x['pago']*f,2),status='pago',cat=x['cat']))
agg={}
for m in mov:
  if m['fornecedor'] in AJ_PAGO:
    k=(m['data'],m['fornecedor']);a=agg.setdefault(k,dict(m,desc=m['desc'].split(' · ')[-1]+' · pedido de mobília',valor=0));a['valor']=round(a['valor']+m['valor'],2)
mov=[m for m in mov if m['fornecedor'] not in AJ_PAGO]+list(agg.values())
for d,f,desc,v in PREV: mov.append(dict(data=d,fornecedor=f,desc=desc,valor=v,status='previsto',cat=''))
for p in parc:
  pago=p['status'].lower().startswith('pago')
  mov.append(dict(data=p['venc'],fornecedor='Construtora Diamond',desc=f"Parcela {p['n']}/80 · {p['tipo']}"+(' (antecipada)' if 'antecip' in p['status'].lower() else ''),
    valor=p['pago'] if pago else p['previsto'],status='pago' if pago else ('atrasada' if 'atras' in p['status'].lower() else 'previsto'),cat='Imóvel'))
json.dump(dict(geradoEm=datetime.datetime.now().astimezone().isoformat(timespec='minutes'),fonte='Google Sheets "Apto"',
  total=tot,categorias=cats,comodos=coms,gastos=gastos,cronograma=cron,imovel=dict(resumo=ires,parcelas=parc),movimentos=mov),sys.stdout,ensure_ascii=False,indent=1)
