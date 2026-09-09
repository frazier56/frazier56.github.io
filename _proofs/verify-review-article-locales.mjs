import fs from 'node:fs';import path from 'node:path';import vm from 'node:vm';import assert from 'node:assert/strict';import {execFileSync} from 'node:child_process';
const root=process.cwd(),file='blog/get-more-five-star-reviews/index.html';
const source=fs.readFileSync(path.join(root,file),'utf8');
const baseline=execFileSync('git',['-c','safe.directory='+root,'show','3a3a7abbf0fa54d02c52e43e82f514e97a77cf8b:'+file],{encoding:'utf8'});
const copy=fs.readFileSync(path.join(root,'blog/get-more-five-star-reviews/copy.js'),'utf8');
const normalize=s=>s.replaceAll('\r\n','\n');
const scripts=s=>[...s.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)];
for(const [,attrs,body] of scripts(source)){if(!body.trim())continue;if(attrs.includes('ld+json'))JSON.parse(body);else new vm.Script(body);}
const hrefs=s=>[...s.matchAll(/href="([^"]+)"/g)].map(x=>x[1]).sort();assert.deepEqual(hrefs(source),hrefs(baseline),'original destinations');
const section=(s,a,b)=>s.slice(s.indexOf(a),s.indexOf(b,s.indexOf(a)));
assert.equal(normalize(section(source,'    var I18N_META','    function applyLang')),normalize(section(baseline,'    var I18N_META','    function applyLang')),'all original dictionaries');
const clean=s=>normalize(s).replace(/<span data-review-copy="meta">([\s\S]*?)<\/span>/,'$1').replace('data-review-copy="related_heading"','data-i18n="blog_soon"').replace(/ data-review-(?:copy|alt)="[^"]+"/g,'');
assert.equal(clean(section(source,'        <article','    </main>')),clean(section(baseline,'        <article','    </main>')),'original English content, images, date, attribution');
const oldScripts=scripts(baseline).filter(x=>x[2].trim());const newScripts=scripts(source).filter(x=>x[2].trim());assert.equal(oldScripts.length,newScripts.length);
for(let i=0;i<oldScripts.length;i++){if(oldScripts[i][2].includes('function applyLang'))continue;assert.equal(normalize(newScripts[i][2]),normalize(oldScripts[i][2]),'unrelated script '+i);}
const nodes=[...source.matchAll(/<(h1|h2|h3|p|li|span)([^>]*data-review-copy="([^"]+)"[^>]*)>([\s\S]*?)<\/\1>/g)].map(m=>({key:m[3],innerHTML:m[4],getAttribute(){return this.key;}}));assert.equal(nodes.length,27);
const original=nodes.map(n=>n.innerHTML);const doc={title:'Original English title',querySelectorAll(sel){return sel==='[data-review-copy]'?nodes:[];},getElementById(){return null;}};const ctx={window:{},document:doc};vm.runInNewContext(copy,ctx);
let count=0;for(const lang of ['co','es','de','ru','zh','pt']){ctx.window.OWL_REVIEW_APPLY(lang);nodes.forEach((n,i)=>{assert(n.innerHTML.trim());assert.notEqual(n.innerHTML,original[i],lang+' translated '+n.key);assert.deepEqual(hrefs(n.innerHTML),hrefs(original[i]),lang+' links '+n.key);assert(!n.innerHTML.includes('[['));assert(!/[\u0000-\u0008\u000e-\u001f\ufffd]/.test(n.innerHTML));for(const tag of n.innerHTML.match(/<[^>]*>/g)||[])assert(/^<\/?(?:em|strong)>$|^<\/a>$|^<a href="[^"]+">$/.test(tag),tag);count++;});ctx.window.OWL_REVIEW_APPLY('en');assert.deepEqual(nodes.map(n=>n.innerHTML),original,'English restoration '+lang);assert.equal(doc.title,'Original English title');}
ctx.window.OWL_REVIEW_APPLY('unknown');assert.deepEqual(nodes.map(n=>n.innerHTML),original,'unknown locale fallback');
assert(source.includes("co:'es-CO'"));assert(source.includes('inert aria-hidden="true"'));assert(source.includes("b.setAttribute('role','menuitemradio')"));
console.log('PASS '+count+' localized bindings; exact English restoration; per-block links; unchanged dates, dictionary values, unrelated scripts and original destinations; inline JavaScript/JSON syntax.');
