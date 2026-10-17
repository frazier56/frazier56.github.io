const stage=document.querySelector('.scenes');
if(stage){
 const cards=[...stage.querySelectorAll('.scene')],reduce=matchMedia('(prefers-reduced-motion: reduce)');
 let index=0,paused=false,timer,onScreen=false,hover=false,focused=false,hold,origin,suppressClick=false,suppressUntil=0;
 cards.forEach(card=>{if(!card.dataset.video)return;const v=document.createElement('video');v.muted=true;v.loop=true;v.playsInline=true;v.preload='none';v.className='scene-video';v.setAttribute('aria-hidden','true');v.poster=card.querySelector('img').src;card.prepend(v);v.addEventListener('playing',()=>{if(card!==cards[index]||paused||reduce.matches||hover||focused||!onScreen||document.hidden){v.pause();return;}card.classList.add('video-playing')});v.addEventListener('error',()=>{v.pause();card.classList.remove('video-playing')})});
 stage.classList.add('carousel');owL(stage,'aria-label','Explore One World destinations');
 const controls=document.createElement('div');controls.className='carousel-controls';
 controls.innerHTML='<button type="button" data-owt-aria-label="Previous destination" aria-label="'+owT('Previous destination')+'">←</button><span></span><button type="button" data-owt-aria-label="Next destination" aria-label="'+owT('Next destination')+'">→</button>';
 stage.after(controls);const [prev,next]=controls.querySelectorAll('button'),label=controls.querySelector('span');
 function render(){cards.forEach((card,i)=>{const slot=(i-index+cards.length)%cards.length;card.dataset.slot=slot;card.tabIndex=slot===0?0:-1;card.setAttribute('aria-hidden',slot===0?'false':'true');const v=card.querySelector('video');if(v){if(slot!==0||paused||reduce.matches||hover||focused||!onScreen||document.hidden){v.pause();if(slot!==0)card.classList.remove('video-playing');return;}if(!v.getAttribute('src'))v.src=card.dataset.video;v.play().then(()=>{if(card!==cards[index]||paused||reduce.matches||hover||focused||!onScreen||document.hidden)v.pause()}).catch(()=>card.classList.remove('video-playing'));}});label.textContent=(index+1)+' / '+cards.length;}
 function schedule(){clearInterval(timer);if(!paused&&onScreen&&!document.hidden&&!reduce.matches&&!hover&&!focused)timer=setInterval(()=>step(1),2800);}
 function step(delta){index=(index+delta+cards.length)%cards.length;const v=cards[index].querySelector('video');if(v&&v.readyState)v.currentTime=0;render();schedule();}
 prev.onclick=()=>step(-1);next.onclick=()=>step(1);
 const inside=node=>!!node&&(stage.contains(node)||controls.contains(node));
 const hint=document.createElement('span');hint.id='carousel-motion-help';hint.style.cssText='position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap';hint.setAttribute('role','status');controls.after(hint);stage.setAttribute('aria-describedby',hint.id);
 function motionHint(){const co=document.documentElement.lang.startsWith('es');if(reduce.matches){hint.textContent=co?'Movimiento pausado por la configuración de movimiento reducido del dispositivo.':'Motion paused by your device’s reduced-motion setting.';return;}hint.textContent=co?(paused?'Movimiento pausado. Mantén presionada una tarjeta o pulsa Espacio para reanudar.':'Mantén presionada una tarjeta o pulsa Espacio para pausar el movimiento.'):(paused?'Motion paused. Hold a card or press Space to resume.':'Hold a card or press Space to pause motion.');}
 function toggleMotion(){if(reduce.matches){motionHint();return;}paused=!paused;motionHint();render();schedule()}
 document.addEventListener('ow:lang',motionHint);motionHint();
 for(const area of [stage,controls]){
 area.addEventListener('pointerenter',e=>{if(e.pointerType==='mouse'){hover=true;render();schedule()}});
 area.addEventListener('pointerleave',e=>{if(!inside(e.relatedTarget)){hover=false;render();schedule()}});
 area.addEventListener('focusin',()=>{focused=true;render();schedule()});
 area.addEventListener('focusout',e=>{focused=inside(e.relatedTarget);render();schedule()});
 }
 stage.addEventListener('dragstart',e=>e.preventDefault());
 stage.addEventListener('pointerdown',e=>{if(!e.isPrimary||e.button>0||origin)return;clearInterval(timer);suppressClick=false;origin={x:e.clientX,y:e.clientY,id:e.pointerId,axis:null};if(e.pointerType!=='mouse')hold=setTimeout(()=>{if(!origin||origin.axis)return;origin.axis='hold';suppressClick=true;suppressUntil=Date.now()+1000;toggleMotion()},500)});
 stage.addEventListener('pointermove',e=>{if(!origin||e.pointerId!==origin.id)return;const dx=e.clientX-origin.x,dy=e.clientY-origin.y;if(Math.hypot(dx,dy)>12){clearTimeout(hold);if(!origin.axis)origin.axis=Math.abs(dx)>Math.abs(dy)*1.3?'x':'y';}if(origin.axis==='x'){suppressClick=true;suppressUntil=Date.now()+1000;stage.setPointerCapture(e.pointerId)}});
 stage.addEventListener('pointerup',e=>{if(!origin||e.pointerId!==origin.id)return;clearTimeout(hold);const dx=e.clientX-origin.x,swipe=origin.axis==='x'&&Math.abs(dx)>=40;if(suppressClick)suppressUntil=Date.now()+500;origin=null;if(stage.hasPointerCapture(e.pointerId))stage.releasePointerCapture(e.pointerId);if(swipe)step(dx<0?1:-1);else schedule()});
 stage.addEventListener('pointercancel',e=>{if(!origin||e.pointerId!==origin.id)return;clearTimeout(hold);origin=null;suppressClick=false;if(stage.hasPointerCapture(e.pointerId))stage.releasePointerCapture(e.pointerId);schedule()});
 stage.addEventListener('click',e=>{if(suppressClick&&e.detail!==0&&Date.now()<=suppressUntil)e.preventDefault();suppressClick=false});
 stage.addEventListener('contextmenu',e=>{if(origin?.axis==='hold')e.preventDefault()});
 stage.addEventListener('keydown',e=>{if(e.code==='Space'||e.key===' '){e.preventDefault();if(!e.repeat)toggleMotion();return;}if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();step(e.key==='ArrowRight'?1:-1);cards[index].focus()}});
 document.addEventListener('visibilitychange',()=>{render();schedule()});
 new IntersectionObserver(es=>{onScreen=es[0].isIntersecting&&es[0].intersectionRatio>=.25;render();schedule()},{threshold:[0,.25]}).observe(stage);
 reduce.addEventListener('change',()=>{motionHint();render();schedule()});render();schedule();
}
