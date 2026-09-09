import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const root=new URL('../',import.meta.url);
const ctx={window:{}};vm.createContext(ctx);vm.runInContext(fs.readFileSync(new URL('public-directory-copy.js',root),'utf8'),ctx);
assert.deepEqual(Object.keys(ctx.window.OWL_PUBLIC_COPY).sort(),['de','es','pt','ru','zh']);
let checks=0;
for(const path of ['index.html','apps/index.html']){
 const html=fs.readFileSync(new URL(path,root),'utf8');
 assert.match(html,/public-directory-copy\.js/);
 for(const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)){if(/src=/.test(m[1]))continue;if(/application\/ld\+json/.test(m[1]))JSON.parse(m[2]);else new vm.Script(m[2]);}
 const attrs=key=>[...html.matchAll(new RegExp(key+'="([^\"]*)"','g'))].map(m=>m[1]);
 for(const [lang,p] of Object.entries(ctx.window.OWL_PUBLIC_COPY)){
  for(const key of attrs('data-i18n').filter(k=>k.startsWith('public_')||k.startsWith('directory_'))){assert.ok(p.text[key],path+' '+lang+' missing '+key);checks++;}
  for(const key of attrs('data-public-alt-source'))assert.ok(p.alts[key]);
  for(const key of attrs('data-public-placeholder-source'))assert.ok(p.placeholders[key]);
  assert.equal(ctx.window.OWL_PUBLIC_MENU_LABEL(lang,true),p.aria['Close menu']);
  assert.equal(ctx.window.OWL_PUBLIC_MENU_LABEL(lang,false),p.aria['Open menu']);
  assert.ok(p.titles.every(t=>t.includes('One World')));
  for(const app of ['onescore','onejob','onehome','oneevent','onesocial','oneagent','onepay','onebusiness'])for(const kind of ['tag','desc'])assert.ok(p.text['directory_'+app+'_'+kind]);
 }
 if(path==='index.html'){
  assert.deepEqual([...html.matchAll(/<option[^>]*value="([^\"]+)"/g)].map(m=>m[1]),['OneVoice call answering','OnePage website upgrade','OneApp mobile app','OneEvent tickets and events','OneHome rentals or sales','OneJob, OneScore, or OneSocial','Something else']);
 }else assert.equal(attrs('data-directory-name').length,8);
}
assert.equal(ctx.window.OWL_PUBLIC_MENU_LABEL('en',true),'Close menu');
assert.equal(ctx.window.OWL_PUBLIC_MENU_LABEL('co',true),'Cerrar menú');
console.log('PASS '+checks+' five-locale bindings, titles, menu labels, image/placeholder coverage, stable contact option values and eight app controls.');
