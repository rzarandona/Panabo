(async()=>{
 const deckHost=document.getElementById('deck');
 try{
  const response=await fetch('slides.html',{cache:'no-cache'});
  if(!response.ok)throw new Error(`HTTP ${response.status}`);
  deckHost.innerHTML=await response.text();
 }catch(error){
  deckHost.innerHTML=`<div class="load-error"><div><b>Presentation could not load.</b><span>${error.message}</span></div></div>`;
  return;
 }
 const slides=[...document.querySelectorAll('.slide')];
 const dots=document.getElementById('dots');
 const counter=document.getElementById('counter');
 const bar=document.getElementById('bar');
 const prev=document.getElementById('prev');
 const next=document.getElementById('next');
 const deck=document.getElementById('deck');
 let at=0,startX=0,startY=0,startTarget=null;
 const pad=n=>String(n).padStart(2,'0');
 slides.forEach((slide,index)=>{const button=document.createElement('button');button.className='dot';button.type='button';button.ariaLabel=`Go to slide ${index+1}: ${slide.dataset.title}`;button.onclick=()=>show(index);dots.appendChild(button)});
 const dotButtons=[...dots.children];
 function show(index,updateHash=true){
   at=(index+slides.length)%slides.length;
   slides.forEach((slide,n)=>slide.classList.toggle('active',n===at));
   dotButtons.forEach((dot,n)=>dot.classList.toggle('on',n===at));
   counter.textContent=`${pad(at+1)} / ${pad(slides.length)}`;
   bar.style.width=`${(at+1)/slides.length*100}%`;
   prev.disabled=at===0;
   next.innerHTML=at===slides.length-1?'<span>Start</span> ↺':'<span>Next</span> →';
   next.ariaLabel=at===slides.length-1?'Return to first slide':'Next slide';
   document.title=`${pad(at+1)} · ${slides[at].dataset.title} — Panabo Digital Permit Pilot`;
   slides[at].scrollTop=0;
   if(updateHash)history.replaceState(null,'',`#slide-${at+1}`);
 }
 prev.onclick=()=>{if(at)show(at-1)};
 next.onclick=()=>show(at===slides.length-1?0:at+1);
 document.getElementById('print').onclick=()=>print();
 document.onkeydown=event=>{
   if(['ArrowRight','PageDown',' '].includes(event.key)){event.preventDefault();show(at===slides.length-1?0:at+1)}
   if(['ArrowLeft','PageUp'].includes(event.key)){event.preventDefault();if(at)show(at-1)}
   if(event.key==='Home')show(0);
   if(event.key==='End')show(slides.length-1);
 };
 deck.addEventListener('touchstart',event=>{
   if(event.touches.length!==1)return;
   startTarget=event.target;
   startX=event.touches[0].clientX;
   startY=event.touches[0].clientY;
 },{passive:true});
 deck.addEventListener('touchend',event=>{
   if(!startTarget||startTarget.closest('button,a,input,textarea,select')){startTarget=null;return}
   const touch=event.changedTouches[0],deltaX=touch.clientX-startX,deltaY=touch.clientY-startY;
   startTarget=null;
   if(Math.abs(deltaX)>55&&Math.abs(deltaX)>Math.abs(deltaY)*1.35){
     if(deltaX<0&&at<slides.length-1)show(at+1);
     else if(deltaX>0&&at>0)show(at-1);
   }
 },{passive:true});
 const match=location.hash.match(/slide-(\d+)/);
 show(match?Math.min(Math.max(+match[1]-1,0),slides.length-1):0,false);
})();
