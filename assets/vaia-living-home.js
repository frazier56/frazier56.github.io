/* Visual-only adapter. Existing VAIA owns voice, wake, sleep and conversation. */
(()=>{'use strict';
 const widget=document.getElementById('vaia-widget'),orb=document.getElementById('vaia-orb');
 if(!widget||!orb||!window.LivingVaia)return;
 const canvas=document.createElement('canvas');canvas.className='vaia-living-canvas';canvas.setAttribute('aria-hidden','true');
 const name=document.createElement('span');name.className='vaia-living-name';name.textContent='VAIA';name.setAttribute('aria-hidden','true');
 orb.append(canvas,name);let visual;
 try{visual=new LivingVaia(canvas)}catch(e){canvas.remove();name.remove();return}
 orb.classList.add('vaia-living-ready');
 const gain=.55;let context,analyser,wave,active,raf;const sources=new WeakMap();
 function unlock(){try{if(!context){context=new(window.AudioContext||window.webkitAudioContext)();analyser=context.createAnalyser();analyser.fftSize=256;wave=new Float32Array(256);analyser.connect(context.destination)}if(context.state==='suspended')context.resume().catch(()=>{});}catch(e){}}
 // Capture unlocks audio on the same gesture without replacing the existing click handler.
 orb.addEventListener('click',unlock,true);
 const text=document.getElementById('vaia-text');text?.addEventListener('keydown',e=>{if(e.key==='Enter')unlock()},true);
 window.vaiaAttachAudio=audio=>{
  unlock();if(!context||!analyser)return;
  try{let source=sources.get(audio);if(!source){source=context.createMediaElementSource(audio);source.connect(analyser);sources.set(audio,source)}active=audio;
   const clear=()=>{if(active===audio){active=null;visual.setEnergy(0)}};
   audio.addEventListener('ended',clear,{once:true});audio.addEventListener('error',clear,{once:true});
  }catch(e){/* Audio remains owned by the existing runtime. */}
 };
 function sync(){const c=widget.classList;visual.setState(c.contains('asleep')?'rest':c.contains('speaking')?'speaking':c.contains('thinking')?'thinking':c.contains('listening')?'listening':'rest');if(c.contains('asleep'))visual.setEnergy(0);visual.light=document.documentElement.dataset.theme!=='dark';}
 const stateObserver=new MutationObserver(sync);stateObserver.observe(widget,{attributes:true,attributeFilter:['class']});
 const themeObserver=new MutationObserver(sync);themeObserver.observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});sync();
 function frame(){let energy=0;if(analyser&&active&&!active.paused&&!active.ended&&!widget.classList.contains('asleep')){analyser.getFloatTimeDomainData(wave);let sum=0;for(const x of wave)sum+=x*x;energy=Math.min(1,Math.sqrt(sum/wave.length)*5)*gain}visual.setEnergy(energy);raf=requestAnimationFrame(frame)}frame();
 widget.dataset.speakingGain=String(gain);
 window.addEventListener('pagehide',event=>{if(event.persisted)return;cancelAnimationFrame(raf);stateObserver.disconnect();themeObserver.disconnect();visual.destroy();context?.close()});
})();
