import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync(new URL('../onevoice/get-started/index.html',import.meta.url),'utf8');
const currency=html.slice(html.indexOf('  /* ---------- currency ---------- */'),html.indexOf('  function applyPrices(root){'));
assert.ok(currency.includes('window.OV_MONEY_SUM'));
assert.match(html,/sumTotal'\).textContent=window.OV_MONEY_SUM \? window.OV_MONEY_SUM\(\[Math.round\(setup\*100\),Math.round\(termTotal\*100\)\]\)/);
const ctx={window:{},current:'co',CURRENCY_ON:true,FX_MARKUP:1.05,RATES:null,FALLBACK_RATES:{COP:4100,USD:1},CCY:{COP:{sym:'COP ',pos:'before',grp:'.',dec:',',dec2under:0},USD:{sym:'$',pos:'before',grp:',',dec:'.',dec2under:5}},langByCode:c=>({ccy:c==='co'?'COP':'USD'})};
vm.createContext(ctx); vm.runInContext(currency,ctx);
const amount=s=>Number(s.replace('COP ','').replaceAll('.',''));
let cases=0, regressions=0;
for(const rate of [3000,3126.47,3285.19,3900,4100,4321.987]){
 ctx.RATES={COP:rate,USD:1};
 for(const base of [149,297]) for(const count of [1,2,4,10]) for(const tf of [0,1,count]) for(const term of [{m:1,d:0},{m:3,d:.25},{m:12,d:.35}]){
  const monthly=base+tf*129+Math.max(0,count-tf-1)*89;
  const parts=[29900,Math.round(monthly*term.m*(1-term.d)*100)];
  const original=[...parts];
  const shown=parts.map(n=>amount(ctx.window.OV_MONEY(n)));
  const total=amount(ctx.window.OV_MONEY_SUM(parts));
  assert.equal(total,shown[0]+shown[1]); assert.deepEqual(parts,original);
  if(total!==amount(ctx.window.OV_MONEY(parts[0]+parts[1])))regressions++;
  ctx.current='us'; assert.equal(ctx.window.OV_MONEY_SUM(parts),ctx.window.OV_MONEY(parts[0]+parts[1])); ctx.current='co'; cases++;
 }
}
assert.ok(regressions>0,'matrix must catch the original independently rounded total');
ctx.RATES=null;
assert.equal(amount(ctx.window.OV_MONEY_SUM([29900,23800])),amount(ctx.window.OV_MONEY(29900))+amount(ctx.window.OV_MONEY(23800)));
// The COP-only correction must not change other currencies or their existing formatter.
ctx.langByCode=()=>({ccy:'EUR'});ctx.CCY.EUR={sym:'EUR ',pos:'before',grp:'.',dec:',',dec2under:5};ctx.RATES={EUR:.92};
assert.equal(ctx.window.OV_MONEY_SUM([29900,23800]),ctx.window.OV_MONEY(53700));
console.log('PASS '+cases+' quote cases; '+regressions+' old-total mismatches covered, fallback and USD/EUR unchanged.');
