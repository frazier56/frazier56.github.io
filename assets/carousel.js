const stage=document.querySelector('.scenes');
if(stage){
 const cards=[...stage.querySelectorAll('.scene')],reduce=matchMedia('(prefers-reduced-motion: reduce)');
 let index=0,paused=reduce.matches,timer,onScreen=false,hover=false,focused=false,hold,origin,suppressClick=false;
 cards.forEach(card=>{if(!card.dataset.video)return;const v=document.createElement('video');v.muted=true;v.loop=true;v.playsInline=true;v.preload='none';v.className='scene-video';v.setAttribute('aria-hidden','true');v.poster=card.querySelector('img').src;card.prepend(v);v.addEventListener('playing',()=>{if(card!==cards[index]||paused||!onScreen||document.hidden){v.pause();return;}card.classList.add('video-playing')});v.addEventListener('error',()=>{v.pause();card.classList.remove('video-playing')})});
 stage.classList.add('carousel');stage.setAttribute('aria-label',owT('Explore One World destinations'));
 const controls=document.createElement('div');controls.className='carousel-controls';
 controls.innerHTML='<button type="button" aria-label="'+owT('Previous destination')+'">←</button><span></span><button type="button" aria-label="'+owT('Next destination')+'">→</button><button type="button" class="carousel-toggle">'+owT('Pause')+'</button>';
 stage.after(controls);const [prev,next,toggle]=controls.querySelectorAll('button'),label=controls.querySelector('span');
 function render(){cards.forEach((card,i)=>{const slot=(i-index+cards.length)%cards.length;card.dataset.slot=slot;card.tabIndex=slot===0?0:-1;card.setAttribute('aria-hidden',slot===0?'false':'true');const v=card.querySelector('video');if(v){if(slot!==0||paused||!onScreen||document.hidden){v.pause();return;}if(!v.getAttribute('src'))v.src=card.dataset.video;v.play().then(()=>{if(card!==cards[index]||paused||!onScreen||document.hidden)v.pause()}).catch(()=>card.classList.remove('video-playing'));}});label.textContent=(index+1)+' / '+cards.length;toggle.textContent=owT(paused?'Play':'Pause');toggle.dataset.owState=paused?'Play':'Pause';toggle.setAttribute('aria-label',owT(paused?'Play carousel':'Pause carousel'));}
 function schedule(){clearInterval(timer);if(!paused&&onScreen&&!document.hidden&&!reduce.matches&&!hover&&!focused)timer=setInterval(()=>step(1),2800);}
 function step(delta){index=(index+delta+cards.length)%cards.length;const v=cards[index].querySelector('video');if(v&&v.readyState)v.currentTime=0;render();schedule();}
 prev.onclick=()=>step(-1);next.onclick=()=>step(1);toggle.onclick=()=>{paused=!paused;render();schedule()};
 stage.addEventListener('pointerenter',e=>{if(e.pointerType==='mouse'){hover=true;schedule()}});stage.addEventListener('pointerleave',()=>{hover=false;clearTimeout(hold);schedule()});
 stage.addEventListener('pointerdown',e=>{clearInterval(timer);suppressClick=false;origin={x:e.clientX,y:e.clientY};if(e.pointerType!=='mouse')hold=setTimeout(()=>{suppressClick=true;paused=false;render()},500)});
 stage.addEventListener('pointermove',e=>{if(origin&&Math.hypot(e.clientX-origin.x,e.clientY-origin.y)>12)clearTimeout(hold)});
 stage.addEventListener('pointerup',()=>{clearTimeout(hold);origin=null;schedule()});stage.addEventListener('pointercancel',()=>{clearTimeout(hold);origin=null;suppressClick=false;schedule()});
 stage.addEventListener('click',e=>{if(suppressClick){e.preventDefault();suppressClick=false}});stage.addEventListener('contextmenu',e=>{if(suppressClick)e.preventDefault()});
 stage.addEventListener('focusin',()=>{focused=true;schedule()});stage.addEventListener('focusout',()=>{focused=false;schedule()});
 stage.addEventListener('keydown',e=>{if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();step(e.key==='ArrowRight'?1:-1);cards[index].focus()}});
 document.addEventListener('visibilitychange',()=>{render();schedule()});
 new IntersectionObserver(es=>{onScreen=es[0].isIntersecting&&es[0].intersectionRatio>=.25;render();schedule()},{threshold:[0,.25]}).observe(stage);
 reduce.addEventListener('change',()=>{paused=reduce.matches;render();schedule()});render();schedule();
}
