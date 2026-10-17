const motion=matchMedia('(prefers-reduced-motion: reduce)');
document.querySelectorAll('.destination[data-video]').forEach(card=>{
 const video=document.createElement('video');video.muted=true;video.loop=true;video.playsInline=true;video.preload='none';video.className='destination-video';video.setAttribute('aria-hidden','true');card.prepend(video);
 const button=document.createElement('button');button.type='button';button.className='destination-play';owL(button,'aria-label','Pause {p} video',card.dataset.product);card.append(button);
 video.poster=card.querySelector('img').src;
 let onScreen=false,choice=null,failed=false;
 const shouldPlay=()=>onScreen&&!document.hidden&&!failed&&(choice===null?!motion.matches:choice);
 function label(){const action=video.paused?'Play':'Pause';owL(button,'aria-label',action+' {p} video',card.dataset.product);}
 async function update(){if(!shouldPlay()){video.pause();label();return;}if(!video.getAttribute('src'))video.src=card.dataset.video;try{await video.play();if(!shouldPlay())video.pause();}catch{video.pause();}label();}
 button.onclick=()=>{choice=video.paused;update()};
 video.addEventListener('playing',()=>{if(!shouldPlay()){video.pause();return;}card.classList.add('video-ready');label()});video.addEventListener('pause',label);
 new IntersectionObserver(entries=>{onScreen=entries[0].isIntersecting&&entries[0].intersectionRatio>=.3;update()},{threshold:[0,.3]}).observe(card);
 document.addEventListener('visibilitychange',update);motion.addEventListener('change',()=>{choice=null;update()});video.addEventListener('error',()=>{failed=true;video.pause();card.classList.remove('video-ready');button.hidden=true});label();
});
