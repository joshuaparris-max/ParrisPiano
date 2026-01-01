// Simple MIDI -> on-screen keyboard mapping
(function(){
  const startNote = 21; // A0
  const endNote = 108;  // C8

  function noteName(n){
    const names = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'];
    return names[n % 12] + (Math.floor(n/12) - 1);
  }

  function isBlack(n){
    return [1,3,6,8,10].includes(n % 12);
  }

  function injectStyles(){
    const css = `
      #keyboard { position: relative; user-select: none; height:160px; margin-top:8px; }
      #keyboard .keys { display:flex; position:relative; height:100%; }
      #keyboard .key { box-sizing:border-box; border:1px solid rgba(0,0,0,0.25); cursor:default; }
      #keyboard .key.white { width:28px; height:100%; background:#fff; border-radius:4px; margin-right:1px; display:flex; align-items:flex-end; justify-content:center; padding-bottom:6px; font-size:9px; color:#111; }
      #keyboard .key.black { width:18px; height:64%; background:#111; color:#fff; position:relative; margin-left:-9px; z-index:2; border-radius:4px; display:flex; align-items:flex-end; justify-content:center; padding-bottom:6px; font-size:9px; }
      #keyboard .key.active.white { background: linear-gradient(180deg,#fffbeb,#ffd6c1); box-shadow:0 6px 18px rgba(255,90,40,0.2) inset; }
      #keyboard .key.active.black { background: linear-gradient(180deg,#ffd6c1,#ff8a5a); box-shadow:0 6px 16px rgba(255,120,92,0.25) inset; }
      #keyboard-container { overflow:auto; }
    `;
    const s = document.createElement('style'); s.textContent = css; document.head.appendChild(s);
  }

  function createKeyboard(container){
    const wrapper = document.createElement('div'); wrapper.id = 'keyboard';
    const keysRow = document.createElement('div'); keysRow.className = 'keys';
    for(let n = startNote; n <= endNote; n++){
      const k = document.createElement('div');
      k.className = 'key ' + (isBlack(n) ? 'black' : 'white');
      k.dataset.note = String(n);
      k.title = noteName(n);
      k.innerHTML = `<div style="pointer-events:none">${noteName(n)}</div>`;
      keysRow.appendChild(k);
    }
    wrapper.appendChild(keysRow);
    container.appendChild(wrapper);
  }

  function highlight(note){
    const el = document.querySelector(`#keyboard [data-note='${note}']`);
    if(el) el.classList.add('active');
  }
  function release(note){
    const el = document.querySelector(`#keyboard [data-note='${note}']`);
    if(el) el.classList.remove('active');
  }

  // MIDI handling
  let midiAccess = null;
  let currentInput = null;

  function setStatus(text){
    const s = document.getElementById('midi-state'); if(s) s.textContent = text;
  }

  function onMIDIMessage(e){
    const data = e.data; const status = data[0] & 0xf0; const note = data[1]; const vel = data[2];
    if(status === 0x90 && vel > 0){ highlight(note); }
    else if(status === 0x80 || (status === 0x90 && vel === 0)){ release(note); }
  }

  function listInputs(select){
    select.innerHTML = '';
    const empty = document.createElement('option'); empty.value = ''; empty.textContent = '(Choose input)'; select.appendChild(empty);
    for(const input of midiAccess.inputs.values()){
      const opt = document.createElement('option'); opt.value = input.id; opt.textContent = input.name || input.manufacturer || input.id; select.appendChild(opt);
    }
  }

  function attachInputById(id){
    if(currentInput){ currentInput.onmidimessage = null; }
    currentInput = id ? midiAccess.inputs.get(id) : null;
    if(currentInput){ currentInput.onmidimessage = onMIDIMessage; setStatus('connected'); }
    else { setStatus('disconnected'); }
  }

  function initMIDI(){
    if(!navigator.requestMIDIAccess){ setStatus('unsupported'); return; }
    navigator.requestMIDIAccess({ sysex: false }).then(ma => {
      midiAccess = ma;
      const sel = document.getElementById('midi-inputs');
      listInputs(sel);
      sel.addEventListener('change', (ev)=> attachInputById(ev.target.value));
      // auto-select a Yamaha/CVP if available
      for(const input of midiAccess.inputs.values()){
        if(/yamaha|cvp|usb/i.test((input.name||'').toLowerCase())){ sel.value = input.id; attachInputById(input.id); break; }
      }
      midiAccess.onstatechange = ()=> { listInputs(sel); };
      setStatus('ready');
    }).catch(err => { setStatus('error'); console.warn('MIDI init error', err); });
  }

  // bootstrap
  document.addEventListener('DOMContentLoaded', ()=>{
    injectStyles();
    const cont = document.getElementById('keyboard-container');
    if(!cont){ console.warn('No keyboard container'); return; }
    createKeyboard(cont);
    initMIDI();
  });

})();
