/* Sources are configured only when matching, reviewed video files are available. */
document.querySelectorAll('.scene[data-video]').forEach(card => {
  if(card.parentElement.classList.contains('scenes'))return;
  const video=document.createElement('video');
  video.muted=true;video.loop=true;video.playsInline=true;video.preload='none';
  video.setAttribute('aria-hidden','true');video.className='scene-video';
  card.prepend(video);
  let timer,pressed=false,origin,active=false,suppressClick=false;
  const reduce=matchMedia('(prefers-reduced-motion: reduce)');
  function stop(){clearTimeout(timer);active=false;video.pause();card.classList.remove('video-playing');}
  async function play(){
    if(reduce.matches||!card.dataset.video)return;
    active=true;
    if(!video.getAttribute('src'))video.src=card.dataset.video;
    try{await video.play();if(active)card.classList.add('video-playing');else video.pause();}catch{stop();}
  }
  card.addEventListener('pointerenter',e=>{if(e.pointerType==='mouse')play();});
  card.addEventListener('pointerleave',stop);
  card.addEventListener('pointerdown',e=>{
    if(e.pointerType==='mouse')return;
    stop();pressed=true;suppressClick=false;origin={x:e.clientX,y:e.clientY};
    timer=setTimeout(()=>{if(pressed&&!reduce.matches){suppressClick=true;play();}},500);
  });
  card.addEventListener('pointermove',e=>{if(pressed&&origin&&Math.hypot(e.clientX-origin.x,e.clientY-origin.y)>12){pressed=false;stop();}});
  card.addEventListener('pointerup',()=>{pressed=false;clearTimeout(timer);});
  card.addEventListener('pointercancel',()=>{pressed=false;stop();});
  card.addEventListener('click',e=>{if(suppressClick){e.preventDefault();suppressClick=false;}});
  card.addEventListener('contextmenu',e=>{if(suppressClick)e.preventDefault();});
  card.addEventListener('focus',play);card.addEventListener('blur',stop);
  video.addEventListener('error',stop);
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
  reduce.addEventListener('change',()=>{if(reduce.matches)stop();});
  new IntersectionObserver(entries=>{if(!entries[0].isIntersecting)stop();},{threshold:.2}).observe(card);
});
