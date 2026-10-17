/* Original procedural VAIA study. No stock image or external rendering library. */
class LivingVaia {
 constructor(canvas){
  this.canvas=canvas;this.state='rest';this.energy=0;this.targetEnergy=0;this.time=0;this.paused=false;this.light=false;this.visible=true;
  this.reduce=matchMedia('(prefers-reduced-motion: reduce)');
  const gl=this.gl=canvas.getContext('webgl',{alpha:true,antialias:true,premultipliedAlpha:false});
  if(!gl)throw new Error('This preview needs WebGL. Try a browser with hardware acceleration.');
  const vs=`precision highp float;
attribute vec3 aSeed;
uniform float uTime,uEnergy,uActivity,uScale,uLight,uDpr,uStabilize;
uniform mat2 uShapeLock;uniform vec2 uCenter;
uniform mediump float uPoint;uniform vec2 uResolution;
varying mediump vec4 vColor;varying mediump float vGlow;
vec3 palette(float t){
 vec3 a=vec3(.05,.70,.95), b=vec3(.56,.29,.98),c=vec3(.94,.30,.67),d=vec3(.96,.72,.20),e=vec3(.10,.82,.57);
 float x=fract(t)*5.;if(x<1.)return mix(a,b,x);if(x<2.)return mix(b,c,x-1.);if(x<3.)return mix(c,d,x-2.);if(x<4.)return mix(d,e,x-3.);return mix(e,a,x-4.);
}
void main(){
 float u=aSeed.x,v=aSeed.y,layer=aSeed.z;
 float companion=step(1.1,layer),mist=step(2.5,layer),spark=step(3.5,layer)*(1.-step(4.5,layer)),soul=step(4.5,layer);
 vGlow=mist+soul;
 float t=uTime-companion*.65+soul*.40;
 // A pole-free folded ribbon. Each spatial mode changes independently;
 // no global rotation, angular phase advance, fixed north or south pole.
 float q=2.*v;
 float ax=.64*cos(t*.37), ay=.67*sin(t*.29+.8), az=.55*cos(t*.31+.4);
 vec3 center=vec3(
   ax*cos(u)+.40*sin(2.*u)*sin(t*.43+.9),
   ay*sin(u)+.43*cos(3.*u)*cos(t*.34+.2),
   az*sin(2.*u)+.30*cos(u)*sin(t*.47));
 float h=v/3.14159265*2.-1.;
 float width=.20+.11*sin(u*3.)*cos(t*.53);
 // Open fans rather than a closed cross-section: no tube target to return to.
 vec3 ribbon=vec3(
   h*(.32+.12*cos(u*2.))*cos(u*2.)+width*(h*h-.33)*sin(u),
   h*(.30+.13*sin(u*3.))*sin(u*2.)+width*(h*h-.33)*cos(u),
   .25*(h*h-.33)+.16*h*sin(u*3.));
 vec3 p=center+ribbon;
 // Dissolve the closed ribbon into a gathered volume, pointed fans and open folds.
 float gather=.5+.25*sin(t*.52+.7)+.25*sin(t*.327+1.4);
 float points=.5+.5*sin(t*.71+1.1);
 float radial=.70+.28*points*cos(5.*u)*sin(v)*sin(v)+.15*sin(3.*v)*cos(2.*u)*sin(t*.63);
 vec3 cloud=vec3(cos(u)*sin(v)*radial,cos(v)*radial,sin(u)*sin(v)*radial*.65);
 cloud.x+=.27*sin(2.*v)*sin(t*.41)+.17*sin(3.*u)*sin(v)*cos(t*.57);
 cloud.y+=.24*cos(2.*u)*sin(v)*sin(t*.48);
 cloud.z+=.20*cos(3.*v)*sin(u)*cos(t*.39);
 p=mix(p,cloud,.38+.60*gather);
 // Neighboring strands drift apart and gather again instead of keeping a tube wall.
 float loosen=.10*sin(t*.67);
 p+=loosen*vec3(sin(3.*v+2.*u),sin(4.*u-v),cos(3.*u+v));
 p*=mix(.30,1.,min(layer,1.));
 // The companion follows with a delayed, independently displaced veil.
 if(companion>.5){
   p*=1.12;
   p+=vec3(.15*sin(2.*u)*cos(t*.61),.13*cos(3.*u)*sin(t*.41),.14*sin(q+u));
 }
 if(companion>.5 && uPoint>.5 && mist<.5){
 p*=1.12;
 p+=vec3(.38*sin(u*17.+v*11.)+.06*sin(t*.8+u),.35*cos(u*13.-v*9.)+.07*cos(t*.6+v),.14*sin(v*19.));
 }
 if(mist>.5 && soul<.5){p*=.63;}
 // Inner mist stays nestled within the body, with its own breathing displacement.
 if(soul>.5){
 p*=.60+.10*sin(u*3.+v);
 p+=vec3(.065*sin(t*.83+u*2.),.07*cos(t*.71+v*3.),.04*sin(t*.57+u));
 }
 // Opposing local contraction and stretch. No overall speech inflation.
 // Short, taut contractions in fixed regions; no travelling sine-wave wobble.
 float impulse=uEnergy*.07*sin(u*3.)*cos(v*4.);
 p.x*=1.+impulse;p.y*=1.-impulse;
 p*=uScale;
 // Orthographic, fixed camera. Cancel only the aggregate screen-plane turn.
 float ca=cos(uStabilize),sa=sin(uStabilize);
 vec2 locked=uShapeLock*(p.xy-uCenter*uScale);
 vec2 screen=vec2(ca*locked.x-sa*locked.y,sa*locked.x+ca*locked.y)*vec2(.59,.65);
 screen.x*=min(uResolution.x,uResolution.y)/uResolution.x;
 screen.y*=min(uResolution.x,uResolution.y)/uResolution.y;
 gl_Position=vec4(screen,0.,1.);
 gl_PointSize=mix(1.5+1.8*pow(.5+.5*sin(u*19.+v*13.+t),8.),mix(65.+25.*sin(v)*sin(v),24.,spark),mist)*uDpr;
 if(soul>.5)gl_PointSize=(155.+45.*sin(u*7.+v)*sin(u*7.+v))*uDpr;
 float fixedDepth=sin(u)*sin(v);
 float front=smoothstep(-1.,1.,fixedDepth);
 vec3 color=palette(u/6.283+v*.19);
 color=mix(color,vec3(.18,.55,1.),mist*.55);
 color=mix(color,vec3(.28,.75,1.),soul*.55);
 color=mix(color,vec3(1.),.12);color=mix(color,color*.65,uLight);
 // Keep the body readable; ambiguity belongs mainly at the silhouette.
 float lightField=.5+.28*sin(u*2.3+v*1.7)*cos(t*.24)+.22*cos(v*3.1-u*1.4)*sin(t*.17);
 float reveal=smoothstep(.26,.78,lightField);
 float interior=smoothstep(.12,.52,abs(fixedDepth));
 float fullReveal=.5+.5*sin(t*.19);
 float edgeVisibility=mix(.08,.82,max(reveal,fullReveal*.7));
 float alpha=mix(edgeVisibility,.78,interior)*mix(.55,1.,front);
 if(companion>.5){
 if(uPoint>.5)alpha=mist>.5?mix(.22,1.5,spark)*(.65+.35*sin(t*.7+u*3.)*sin(t*.7+u*3.)):.65;
 else alpha*=.70;
 }
 else if(uPoint>.5)alpha*=.65;
 if(soul>.5){
 color=mix(vec3(.025,.20,1.),vec3(.02,.95,.68),.5+.5*sin(u*2.+v+t*.32));
 alpha=.30*(.75+.25*sin(t*.9+u*2.+v));
 }
 vColor=vec4(color,alpha);
}`;
  const fs=`precision mediump float;uniform mediump float uPoint;varying mediump vec4 vColor;varying mediump float vGlow;void main(){float a=vColor.a;if(uPoint>.5){float d=length(gl_PointCoord-.5);a*=mix(1.-smoothstep(.15,.5,d),mix(exp(-d*d*28.)*.65+exp(-d*d*500.)*.35,exp(-d*d*18.)*(1.-smoothstep(.35,.5,d)),step(1.5,vGlow)),min(vGlow,1.));}gl_FragColor=vec4(vColor.rgb,a);}`;
  const shader=(type,source)=>{const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error(gl.getShaderInfoLog(s));return s};
  this.program=gl.createProgram();gl.attachShader(this.program,shader(gl.VERTEX_SHADER,vs));gl.attachShader(this.program,shader(gl.FRAGMENT_SHADER,fs));gl.linkProgram(this.program);
  if(!gl.getProgramParameter(this.program,gl.LINK_STATUS))throw new Error(gl.getProgramInfoLog(this.program));
  gl.useProgram(this.program);this.uniforms={};for(const name of ['uTime','uEnergy','uActivity','uPoint','uScale','uLight','uDpr','uResolution','uStabilize','uShapeLock','uCenter'])this.uniforms[name]=gl.getUniformLocation(this.program,name);
  const vertices=[],tau=Math.PI*2;const edge=(u,v,U,V)=>vertices.push(u,v,1,U,V,1);
  // Two intersecting families of fine threads, not a solid skin.
  const small=canvas.clientWidth<150,rows=small?29:81,cols=small?20:64;for(let row=1;row<rows;row++){let v=row/rows*Math.PI;for(let n=0;n<160;n++)edge(n/160*tau,v,(n+1)/160*tau,v)}
  for(let col=0;col<cols;col++){let u=col/cols*tau;for(let n=0;n<100;n++)edge(u,n/100*Math.PI,u,(n+1)/100*Math.PI)}
  // A separate, delayed veil shares the folds but is not welded to the main mesh.
  for(let row=1;row<(small?10:23);row++){let v=row/(small?10:23)*Math.PI;for(let n=0;n<120;n++)vertices.push(n/120*tau,v,2,(n+1)/120*tau,v,2)}
  this.lines=vertices.length/3;let seed=1937;const rand=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296};
  const particles=small?180:1500;for(let n=0;n<particles;n++)vertices.push(rand()*tau,Math.acos(2*rand()-1),.25+.75*Math.cbrt(rand()));
  const dust=small?100:700,glow=small?28:120;
  for(let n=0;n<dust;n++)vertices.push(rand()*tau,Math.acos(2*rand()-1),2);
  for(let n=0;n<glow;n++)vertices.push(rand()*tau,Math.acos(2*rand()-1),3);
  for(let n=0;n<(small?3:9);n++)vertices.push(rand()*tau,Math.acos(2*rand()-1),4);
  for(let n=0;n<(small?18:48);n++)vertices.push(rand()*tau,Math.acos(2*rand()-1),5);
  this.points=particles+dust+glow+(small?3:9)+(small?18:48);const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(vertices),gl.STATIC_DRAW);
  const loc=gl.getAttribLocation(this.program,'aSeed');gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,3,gl.FLOAT,false,0,0);gl.enable(gl.BLEND);gl.disable(gl.DEPTH_TEST);
  this.observer=new IntersectionObserver(es=>{this.visible=es[0].isIntersecting});this.observer.observe(canvas);
  this.lost=false;canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();this.lost=true;canvas.dataset.status='context-lost'});
  canvas.addEventListener('webglcontextrestored',()=>location.reload());
  canvas.dataset.status='ready';this.last=performance.now();this.tick=this.tick.bind(this);this.raf=requestAnimationFrame(this.tick);
 }
 setState(state){if(!['rest','listening','thinking','speaking'].includes(state))throw new Error('Unknown VAIA state');this.state=state}
 setEnergy(value){this.targetEnergy=Number.isFinite(value)?Math.max(0,Math.min(1,value)):0}
 // Track corresponding material points and remove their best-fit rigid turn.
 // Unlike merely omitting a rotation matrix, this cancels rotation caused by morphing.
 stabilize(t){
  const points=[];
  for(let i=0;i<32;i++)for(let j=0;j<8;j++){
   const u=i*Math.PI/16,q=j*Math.PI/4,h=q/Math.PI-1;
   const width=.20+.11*Math.sin(u*3)*Math.cos(t*.53);
   let x=.64*Math.cos(t*.37)*Math.cos(u)+.40*Math.sin(2*u)*Math.sin(t*.43+.9)
    +h*(.32+.12*Math.cos(u*2))*Math.cos(u*2)+width*(h*h-.33)*Math.sin(u);
   let y=.67*Math.sin(t*.29+.8)*Math.sin(u)+.43*Math.cos(3*u)*Math.cos(t*.34+.2)
    +h*(.30+.13*Math.sin(u*3))*Math.sin(u*2)+width*(h*h-.33)*Math.cos(u);
   const v=q/2,gather=.5+.25*Math.sin(t*.52+.7)+.25*Math.sin(t*.327+1.4),tips=.5+.5*Math.sin(t*.71+1.1);
   const radial=.70+.28*tips*Math.cos(5*u)*Math.sin(v)**2+.15*Math.sin(3*v)*Math.cos(2*u)*Math.sin(t*.63);
   const X=Math.cos(u)*Math.sin(v)*radial+.27*Math.sin(2*v)*Math.sin(t*.41)+.17*Math.sin(3*u)*Math.sin(v)*Math.cos(t*.57);
   const Y=Math.cos(v)*radial+.24*Math.cos(2*u)*Math.sin(v)*Math.sin(t*.48);
   const blend=.38+.60*gather,loosen=.10*Math.sin(t*.67);
   x=x*(1-blend)+X*blend+loosen*Math.sin(3*v+2*u);
   y=y*(1-blend)+Y*blend+loosen*Math.sin(4*u-v);
   points.push([x,y]);
  }
  const mx=points.reduce((a,p)=>a+p[0],0)/points.length,my=points.reduce((a,p)=>a+p[1],0)/points.length;
  for(const p of points){p[0]-=mx;p[1]-=my;}
  // Remove the changing global ellipse/shear before fitting material motion.
  // Otherwise a changing long axis can look like rotation despite zero net turn.
  let xx=0,xy=0,yy=0;
  for(const [x,y] of points){xx+=x*x;xy+=x*y;yy+=y*y;}
  xx/=points.length;xy/=points.length;yy/=points.length;
  const det=Math.sqrt(Math.max(1e-8,xx*yy-xy*xy));
  const k=Math.sqrt(xx+yy+2*det),den=(xx+det)*(yy+det)-xy*xy;
  const a=k*(yy+det)/den*.39,b=-k*xy/den*.39,d=k*(xx+det)/den*.39;
  this.shapeLock=[a,b,b,d];this.shapeCenter=[mx,my];
  for(const p of points){const x=p[0],y=p[1];p[0]=a*x+b*y;p[1]=b*x+d*y;}
  if(this.previousPoints){
   let dot=0,cross=0;
   for(let i=0;i<points.length;i++){const [x,y]=this.previousPoints[i],[X,Y]=points[i];dot+=x*X+y*Y;cross+=x*Y-y*X;}
   this.stabilizedAngle-=Math.atan2(cross,dot);
  }else this.stabilizedAngle=0;
  this.previousPoints=points;
  return this.stabilizedAngle;
 }
 tick(now){this.raf=requestAnimationFrame(this.tick);const dt=Math.min((now-this.last)/1000,.05);this.last=now;if(document.hidden||!this.visible||this.lost)return;
  const movement={rest:.85,listening:.95,thinking:2.55,speaking:.85}[this.state];
  if(!this.paused)this.energy+=(this.targetEnergy-this.energy)*(1-Math.exp(-dt*(this.targetEnergy>this.energy?48:22)));
  if(!this.paused&&!this.reduce.matches)this.time+=dt*movement;
  const gl=this.gl,dpr=Math.min(devicePixelRatio||1,2),w=Math.round(this.canvas.clientWidth*dpr),h=Math.round(this.canvas.clientHeight*dpr);
  if(this.canvas.width!==w||this.canvas.height!==h){this.canvas.width=w;this.canvas.height=h}gl.viewport(0,0,w,h);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);
  gl.useProgram(this.program);const f=(n,v)=>gl.uniform1f(this.uniforms[n],v);
  gl.uniform2f(this.uniforms.uResolution,w,h);f('uTime',this.time);f('uStabilize',this.stabilize(this.time));gl.uniformMatrix2fv(this.uniforms.uShapeLock,false,this.shapeLock);gl.uniform2fv(this.uniforms.uCenter,this.shapeCenter);f('uEnergy',this.reduce.matches?0:this.energy);f('uActivity',movement);f('uScale',.94);f('uLight',this.light?1:0);f('uDpr',dpr);
  gl.blendFunc(gl.SRC_ALPHA,this.light?gl.ONE_MINUS_SRC_ALPHA:gl.ONE);
  f('uPoint',1);gl.drawArrays(gl.POINTS,this.lines,this.points);f('uPoint',0);gl.drawArrays(gl.LINES,0,this.lines);
 }
 destroy(){cancelAnimationFrame(this.raf);this.observer.disconnect();this.gl.getExtension('WEBGL_lose_context')?.loseContext()}
}
window.LivingVaia=LivingVaia;
