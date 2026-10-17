/* VAIA voice assistant — ported verbatim from the previous www.oneworldlabs.ai homepage (04131c97). */
/* ---------- VAIA voice assistant: ambient orb, tap to talk / tap to sleep ---------- */
    (function(){
        var SUPABASE_URL = 'https://wseblryyqxawvbjmylbo.supabase.co';
        var VAIA_VOICE_ID = 'pFZP5JQG7iQjIQuC4Bku'; /* Lily — same voice for every utterance, greeting included */

        /* Language: VAIA now speaks whatever language is selected in the header flag switcher
           (window.OWL_LANG, set by the lang-menu click handler), not just English. BCP-47 codes
           drive both the browser's speech-recognition locale and the fallback-TTS voice; the
           backend vaia-chat call also gets `lang` so Gemini replies in that language, and these
           local hardcoded lines (greeting, chat-window toggles, error/rest lines) get their own
           per-language text so nothing stays English-only once a language is picked. */
        var VAIA_BCP47 = { en:'en-US', es:'es-ES', co:'es-CO', de:'de-DE', ru:'ru-RU', zh:'zh-CN', pt:'pt-BR' };
        var VAIA_STRINGS = {
            en: { greeting:"Hey, welcome to One World Labs — this is VAIA! Let me know if you have any questions, or tap me anytime if you'd like me to go quiet.",
                  openChat:"Sure — here's our chat window.", closeChat:"Got it, hiding the chat.",
                  noCatch:"Sorry, I didn't catch that — could you try again?",
                  connError:"I'm having trouble connecting right now — try again in a moment.",
                  restLine:"I haven't heard anything in a bit, so I'll rest for now — just tap me anytime to wake me back up!",
                  wakeLines:["Oh — I fell asleep there for a sec, sorry about that! I'm back now, how can I help?","Whoops, dozed off for a moment. I'm back — what were we saying?","Sorry, I drifted off there for a bit! Back now — go ahead.","My bad, I nodded off for a second. I'm here — how can I help?"],
                  firstWake:"Oh — you woke me up! Hey, I'm glad you found me. I'm VAIA, your One World assistant — how can I help?" },
            es: { greeting:"¡Hola, bienvenido a One World Labs, soy VAIA! Avísame si tienes alguna pregunta, o tócame en cualquier momento si prefieres que me quede callada.",
                  openChat:"Claro, aquí tienes nuestra ventana de chat.", closeChat:"Listo, ocultando el chat.",
                  noCatch:"Perdona, no entendí bien — ¿puedes repetirlo?",
                  connError:"Estoy teniendo problemas para conectarme ahora mismo — inténtalo de nuevo en un momento.",
                  restLine:"No he escuchado nada en un rato, así que voy a descansar — tócame cuando quieras para despertarme.",
                  wakeLines:["Uy, me quedé dormida un segundo, perdón. Ya volví, ¿en qué te ayudo?","Vaya, me distraje un momento. Ya estoy aquí — ¿qué decíamos?","Perdona, me desconecté un poco. Ya volví, adelante.","Disculpa, me dormité un segundo. Aquí estoy — ¿en qué te ayudo?"],
                  firstWake:"Ay, ¡me despertaste! Qué bueno que me encontraste. Soy VAIA, tu asistente de One World — ¿en qué te ayudo?" },
            co: { greeting:"¡Hola, bienvenido a One World Labs, soy VAIA! Cuéntame si tienes alguna pregunta, o tócame cuando quieras si prefieres que me quede callada.",
                  openChat:"Claro que sí, acá tienes nuestra ventana de chat.", closeChat:"Listo, ocultando el chat.",
                  noCatch:"Uy, no te entendí bien — ¿puedes repetirlo?",
                  connError:"Estoy teniendo problemas para conectarme en este momento — inténtalo de nuevo en un momentico.",
                  restLine:"No he escuchado nada hace un rato, así que voy a descansar — tócame cuando quieras para despertarme.",
                  wakeLines:["Ay, me quedé dormida un segundo, disculpa. Ya volví, ¿en qué te ayudo?","Uy, me distraje un momento. Ya estoy acá — ¿qué me decías?","Perdón, me desconecté un poco. Ya volví, dime.","Disculpa, me dormité un segundo. Acá estoy — ¿en qué te colaboro?"],
                  firstWake:"Ay, ¡me despertaste! Qué bueno que me encontraste. Soy VAIA, tu asistente de One World — ¿en qué te colaboro?" },
            de: { greeting:"Hey, willkommen bei One World Labs — ich bin VAIA! Sag mir Bescheid, wenn du Fragen hast, oder tippe mich jederzeit an, wenn ich still sein soll.",
                  openChat:"Klar — hier ist unser Chatfenster.", closeChat:"Alles klar, ich blende den Chat aus.",
                  noCatch:"Entschuldigung, das habe ich nicht verstanden — kannst du das wiederholen?",
                  connError:"Ich habe gerade Verbindungsprobleme — versuch es gleich noch einmal.",
                  restLine:"Ich habe eine Weile nichts gehört, also ruhe ich mich jetzt aus — tipp mich jederzeit an, um mich zu wecken!",
                  wakeLines:["Oh — ich bin kurz eingenickt, entschuldige! Ich bin wieder da, wie kann ich helfen?","Ups, kurz weggenickt. Bin wieder da — was haben wir besprochen?","Entschuldige, ich war kurz weg! Bin wieder da, leg los.","Sorry, kurz eingedöst. Ich bin hier — wie kann ich helfen?"],
                  firstWake:"Oh — du hast mich geweckt! Schön, dass du mich gefunden hast. Ich bin VAIA, deine One-World-Assistentin — wie kann ich helfen?" },
            ru: { greeting:"Привет, добро пожаловать в One World Labs — это ВАЙЯ! Дай мне знать, если у тебя есть вопросы, или коснись меня в любой момент, если хочешь, чтобы я замолчала.",
                  openChat:"Конечно — вот наше окно чата.", closeChat:"Хорошо, скрываю чат.",
                  noCatch:"Извини, я не расслышала — можешь повторить?",
                  connError:"У меня сейчас проблемы с подключением — попробуй ещё раз через момент.",
                  restLine:"Я давно ничего не слышала, поэтому немного отдохну — коснись меня в любой момент, чтобы разбудить!",
                  wakeLines:["Ой, я тут задремала на секунду, извини! Я снова на связи, чем помочь?","Упс, немного отвлеклась. Я вернулась — на чём мы остановились?","Извини, я ненадолго отключилась! Уже здесь, продолжай.","Прости, чуть задремала. Я тут — чем могу помочь?"],
                  firstWake:"Ой — ты меня разбудил! Здорово, что ты меня нашёл. Я ВАЙЯ, твой помощник One World — чем могу помочь?" },
            zh: { greeting:"嗨，欢迎来到 One World Labs——我是 VAIA！有任何问题都可以告诉我，如果想让我安静下来，随时点我一下就行。",
                  openChat:"好的，这是我们的聊天窗口。", closeChat:"好的，正在隐藏聊天窗口。",
                  noCatch:"抱歉，我没听清——可以再说一遍吗？",
                  connError:"我现在连接有点问题——请稍后再试。",
                  restLine:"我有一阵子没听到声音了，先休息一下——随时点我一下就能叫醒我！",
                  wakeLines:["哦，我刚才打了个小盹，不好意思！我回来了，有什么可以帮你的？","呃，刚走神了一下。我回来了——我们说到哪了？","抱歉，我刚才走神了一下！我回来了，请继续。","不好意思，刚打了个盹。我在这儿——有什么可以帮你？"],
                  firstWake:"哦——你把我叫醒了！很高兴你找到了我。我是 VAIA，你的 One World 助手——有什么可以帮你的？" },
            pt: { greeting:"Oi, bem-vindo à One World Labs — eu sou a VAIA! Me avise se tiver alguma pergunta, ou toque em mim a qualquer momento se quiser que eu fique quieta.",
                  openChat:"Claro — aqui está nossa janela de chat.", closeChat:"Certo, escondendo o chat.",
                  noCatch:"Desculpa, não entendi direito — pode repetir?",
                  connError:"Estou com problemas de conexão agora — tente de novo em um instante.",
                  restLine:"Já faz um tempo que não escuto nada, então vou descansar — toque em mim quando quiser para me acordar!",
                  wakeLines:["Ah, cochilei um segundinho, desculpa! Já voltei, como posso ajudar?","Opa, me distraí um instante. Já estou de volta — o que estávamos dizendo?","Desculpa, me desconectei um pouco! De volta, pode continuar.","Foi mal, cochilei rapidinho. Estou aqui — como posso ajudar?"],
                  firstWake:"Ah — você me acordou! Que bom que me encontrou. Eu sou a VAIA, sua assistente One World — como posso ajudar?" }
        };
        function vaiaT(key){
            var lang = window.OWL_LANG || 'en';
            var dict = VAIA_STRINGS[lang] || VAIA_STRINGS.en;
            return (dict[key] != null) ? dict[key] : VAIA_STRINGS.en[key];
        }
        /* Full 5-product knowledge base + rate limiting now live server-side in the vaia-chat edge
           function (keyed off app:'homepage' below) — no client-side knowledge injection needed. */
        var widget = document.getElementById('vaia-widget');
        var orb = document.getElementById('vaia-orb');
        var closeBtn = document.getElementById('vaia-close');
        var log = document.getElementById('vaia-log');
        var textIn = document.getElementById('vaia-text');
        var history = [];
        var busy = false, voiceMode = false, asleep = false, everSlept = false, currentAudio = null, pendingResolve = null, abortCtl = null;
        /* tracks consecutive listen cycles that ended with nothing heard, so she can announce
           "going to rest" after real silence instead of either looping forever or going mute
           with no explanation (the "5th state" — neither listening, thinking, speaking, nor asleep) */
        var noResultStreak = 0;
        var AUTO_SLEEP_AFTER = 3;

        function addMsg(role, text){
            var b = document.createElement('div');
            b.className = 'vaia-msg ' + (role === 'user' ? 'user' : 'vaia');
            b.textContent = text;
            log.appendChild(b);
            log.scrollTop = log.scrollHeight;
            return b;
        }

        function openPanel(){ widget.classList.add('open'); }
        function closePanel(){ widget.classList.remove('open'); }

        /* the LLM always spells her name "VAIA" in generated text (correct for the transcript log),
           but that spelling is ambiguous to TTS engines and got pronounced a different way almost
           every time. Two hyphenated phonetic respellings ("VY-uh", "VAY-uh") both got read back
           wrong. Trying a plain natural word-shape instead of a phonetic hint — "Vaya" — since
           TTS engines often handle real word shapes more reliably than hyphenated spellings.
           Only the audio path gets this substitution — addMsg()/the visible transcript always
           keeps the real "VAIA" spelling. */
        function phoneticize(text){
            return text.replace(/vaia/gi, 'Vaya');
        }

        /* one voice path for EVERY utterance (greeting included) so she never switches voices mid-conversation */
        function speak(text){
            widget.classList.add('speaking');
            var spoken = phoneticize(text);
            return fetch(SUPABASE_URL + '/functions/v1/elevenlabs-tts', {
                method: 'POST', headers: {'Content-Type':'application/json'},
                body: JSON.stringify({ text: spoken, voiceId: VAIA_VOICE_ID })
            }).then(function(r){
                var ct = r.headers.get('content-type') || '';
                if (ct.indexOf('audio') !== -1) {
                    return r.blob().then(function(blob){
                        return new Promise(function(resolve){
                            var audio = new Audio(URL.createObjectURL(blob));
                            currentAudio = audio;
                            pendingResolve = resolve;
                            audio.onended = function(){ currentAudio = null; pendingResolve = null; resolve(); };
                            audio.onerror = function(){ currentAudio = null; pendingResolve = null; resolve(); };
                            audio.play().catch(function(){ currentAudio = null; pendingResolve = null; resolve(); });
                        });
                    });
                }
                return fallbackSpeak(spoken);
            }).catch(function(){ return fallbackSpeak(spoken); })
              .then(function(){ widget.classList.remove('speaking'); });
        }

        /* only used if the ElevenLabs call truly fails — same content, so still one coherent turn.
           Called with already-phoneticized text from speak(); the .replace() below is a no-op in
           that case but keeps this safe if ever called directly with raw text elsewhere. */
        function fallbackSpeak(text){
            text = phoneticize(text);
            return new Promise(function(resolve){
                if (!('speechSynthesis' in window)) { resolve(); return; }
                try {
                    var u = new SpeechSynthesisUtterance(text);
                    u.lang = VAIA_BCP47[window.OWL_LANG || 'en'] || 'en-US';
                    u.rate = 1; u.pitch = 1;
                    u.onend = resolve; u.onerror = resolve;
                    window.speechSynthesis.speak(u);
                } catch(e) { resolve(); }
            });
        }

        /* handle "pull up / hide the chat" locally so the box only appears when asked, never on tap */
        function handleLocalIntent(text){
            var t = text.toLowerCase();
            var wantsOpen = /(chat|text)\s*(window|box)?/.test(t) && /(pull up|open|show|bring up|display|see)/.test(t);
            var wantsClose = /(chat|text)\s*(window|box)?/.test(t) && /(close|hide|minimize|get rid of|dismiss)/.test(t);
            if (wantsOpen) {
                addMsg('user', text);
                openPanel();
                var m = vaiaT('openChat');
                addMsg('vaia', m);
                speak(m).then(function(){ if (voiceMode) startListening(); });
                return true;
            }
            if (wantsClose) {
                addMsg('user', text);
                var m2 = vaiaT('closeChat');
                addMsg('vaia', m2);
                speak(m2).then(function(){ closePanel(); if (voiceMode) startListening(); });
                return true;
            }
            return false;
        }

        function askVaia(userText){
            if (busy || !userText) return;
            if (handleLocalIntent(userText)) return;
            busy = true;
            widget.classList.add('thinking');
            addMsg('user', userText);
            history.push({ role:'user', content: userText });
            var replyEl = addMsg('vaia', '…');
            var full = '';
            var spokenUpTo = 0;
            var speakQueue = Promise.resolve();
            var rateLimited = false;

            /* speak completed sentences as they arrive instead of waiting for the whole reply —
               this is what makes her feel like she's answering right away instead of after a pause */
            function queueSentence(s){
                s = s.trim();
                if (!s) return;
                speakQueue = speakQueue.then(function(){
                    if (asleep) return;
                    widget.classList.remove('thinking');
                    return speak(s);
                });
            }
            function drainSentences(finalFlush){
                var unspoken = full.slice(spokenUpTo);
                var re = /[^.!?]*[.!?]+(\s|$)/g, m, lastIndex = 0;
                while ((m = re.exec(unspoken)) !== null) { queueSentence(m[0]); lastIndex = re.lastIndex; }
                spokenUpTo += lastIndex;
                if (finalFlush) {
                    var rest = full.slice(spokenUpTo);
                    if (rest.trim()) { queueSentence(rest); }
                    spokenUpTo = full.length;
                }
            }

            abortCtl = (typeof AbortController !== 'undefined') ? new AbortController() : null;
            fetch(SUPABASE_URL + '/functions/v1/vaia-chat', {
                method:'POST', headers:{'Content-Type':'application/json'},
                /* NOTE: intentionally NOT sending mode:'voice' here — that activates a 160-token
                   cap server-side, and gemini-flash-latest/2.5-flash-lite burn a chunk of that
                   budget on hidden reasoning/thought-signature content via the OpenAI-compat
                   endpoint, so real replies got cut off after 2-3 words (finish_reason:"length").
                   Confirmed live Jul 14: identical request with mode:'voice' truncated ("Think of…"),
                   without it the same question returned a full, correct answer. Leave uncapped
                   (TEXT_STYLE) until a safe token budget for this model is found. */
                body: JSON.stringify({ messages: history, app: 'homepage', lang: window.OWL_LANG || 'en' }),
                signal: abortCtl ? abortCtl.signal : undefined
            }).then(function(r){
                if (!r.ok || !r.body) {
                    return r.json().catch(function(){ return {}; }).then(function(errBody){
                        var e = new Error(errBody.error || 'bad response');
                        e.rateLimited = !!errBody.rateLimited;
                        throw e;
                    });
                }
                var reader = r.body.getReader(), decoder = new TextDecoder();
                function pump(){
                    return reader.read().then(function(res){
                        if (res.done) return;
                        var chunk = decoder.decode(res.value, {stream:true});
                        chunk.split('\n').forEach(function(line){
                            line = line.trim();
                            if (line.indexOf('data:') !== 0) return;
                            var payload = line.slice(5).trim();
                            if (payload === '[DONE]') return;
                            try {
                                var json = JSON.parse(payload);
                                var delta = json.choices && json.choices[0] && json.choices[0].delta && json.choices[0].delta.content;
                                if (delta) { full += delta; replyEl.textContent = full; log.scrollTop = log.scrollHeight; drainSentences(false); }
                            } catch(e){}
                        });
                        return pump();
                    });
                }
                return pump();
            }).then(function(){
                if (!full) full = vaiaT('noCatch');
                replyEl.textContent = full;
                history.push({ role:'assistant', content: full });
                drainSentences(true);
                return speakQueue;
            }).catch(function(err){
                widget.classList.remove('thinking');
                if (err && err.name === 'AbortError') return;
                var m = (err && err.rateLimited && err.message) ? err.message : vaiaT('connError');
                rateLimited = !!(err && err.rateLimited);
                full = m;
                replyEl.textContent = m;
                history.push({ role:'assistant', content: m });
                return speak(m);
            }).then(function(){
                widget.classList.remove('thinking');
                busy = false;
                if (rateLimited) {
                    /* out of session budget for this visitor — go quiet instead of immediately
                       re-asking (which would just hit the limit again) or looping TTS calls */
                    asleep = true; voiceMode = false;
                    widget.classList.remove('listening', 'speaking');
                    widget.classList.add('asleep');
                    everSlept = true;
                    return;
                }
                if (voiceMode && !asleep) startListening();
            });
        }

        /* ---- speech recognition (Chrome/Edge/Safari webkit) ---- */
        var Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        var recog = null;
        if (Recognition) {
            recog = new Recognition();
            recog.lang = VAIA_BCP47[window.OWL_LANG || 'en'] || 'en-US'; recog.continuous = false; recog.interimResults = false;
            var gotResultThisCycle = false;
            recog.onstart = function(){ widget.classList.add('listening'); gotResultThisCycle = false; };
            recog.onresult = function(e){
                var t = e.results[0][0].transcript;
                if (t && t.trim()) { gotResultThisCycle = true; noResultStreak = 0; askVaia(t.trim()); }
            };
            recog.onerror = function(){ /* onend always fires right after — it owns what happens next */ };
            /* onend is the ONE event that always fires no matter how the cycle ended (result, error,
               or a plain silent timeout some browsers don't even report as an error) — so it's the
               single place that decides what happens next. This is what closes the old "5th state":
               previously a silent timeout with no error event just dropped her into limbo (not
               listening, not thinking, not speaking, not asleep). Now every path leads to exactly
               one of the four real states. */
            recog.onend = function(){
                widget.classList.remove('listening');
                if (busy || asleep || !voiceMode) return; // askVaia() owns the next state, or she's off
                if (gotResultThisCycle) return; // a local-intent reply is already handling its own restart
                noResultStreak++;
                if (noResultStreak >= AUTO_SLEEP_AFTER) {
                    noResultStreak = 0;
                    var line = vaiaT('restLine');
                    addMsg('vaia', line);
                    history.push({ role:'assistant', content: line });
                    speak(line).then(function(){
                        asleep = true; voiceMode = false;
                        widget.classList.remove('listening', 'speaking');
                        widget.classList.add('asleep');
                        everSlept = true;
                    });
                    return;
                }
                startListening();
            };
        }
        function startListening(){
            if (!recog || busy || asleep) return;
            try { recog.start(); } catch(e){}
        }
        function stopListening(){
            if (recog) { try { recog.stop(); } catch(e){} }
        }

        function stopSpeaking(){
            window.speechSynthesis && window.speechSynthesis.cancel();
            if (currentAudio) { try { currentAudio.pause(); } catch(e){} currentAudio = null; }
            if (pendingResolve) { var _r = pendingResolve; pendingResolve = null; _r(); }
        }

        function sleep(){
            asleep = true;
            voiceMode = false;
            if (abortCtl) { try { abortCtl.abort(); } catch(e){} }
            stopListening();
            stopSpeaking();
            widget.classList.remove('listening', 'speaking');
            widget.classList.add('asleep');
            everSlept = true;
        }
        var everWoken = false;
        function wake(){
            asleep = false;
            noResultStreak = 0;
            widget.classList.remove('asleep');
            var goListen = function(){ voiceMode = true; startListening(); };
            if (!everWoken) {
                /* Sleep-first (Lee, Jul 16): the FIRST tap is the introduction —
                   she never speaks before being touched. */
                everWoken = true;
                var firstWake = vaiaT('firstWake');
                history.push({ role:'assistant', content: firstWake });
                addMsg('vaia', firstWake);
                speak(firstWake).then(goListen);
            }
            else if (everSlept) {
                var wl = vaiaT('wakeLines');
                var line = wl[Math.floor(Math.random() * wl.length)];
                speak(line).then(goListen);
            }
            else { goListen(); }
        }

        var orbBusy = false;
        orb.addEventListener('click', function(){
            /* rapid double/triple taps used to desync sleep/wake (e.g. "wake up" firing without a real sleep in between) —
               a short lock after each accepted tap keeps state consistent without feeling laggy on a normal single tap */
            if (orbBusy) return;
            orbBusy = true;
            setTimeout(function(){ orbBusy = false; }, 450);
            if (asleep) { wake(); return; }
            if (widget.classList.contains('listening') || widget.classList.contains('speaking') || voiceMode) { sleep(); return; }
            /* first-ever tap: this IS the required user gesture — start the listening loop */
            voiceMode = true;
            startListening();
        });
        orb.addEventListener('keydown', function(e){ if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); orb.click(); } });
        closeBtn.addEventListener('click', function(){ closePanel(); /* closing the transcript never stops the conversation */ });
        textIn.addEventListener('keydown', function(e){
            if (e.key === 'Enter' && textIn.value.trim()) {
                askVaia(textIn.value.trim());
                textIn.value = '';
            }
        });

        /* auto-greet on load, same voice path as every other line. Chain straight into listening the
           moment the greeting finishes — she was previously left just sitting idle after "let me know
           if you have any questions," which is exactly why she looked like she wasn't hearing anyone.
           If the browser blocks the mic without a prior tap, startListening()/onerror handle that
           gracefully (she just waits for the first tap, same as before). */
        /* Sleep-first (Lee, Jul 16): NO auto-greeting, ever. She was talking the moment
           the page loaded and bothering people at work. She now starts asleep — dim,
           slowly breathing — and only ever speaks after someone taps her (wake()). */
        window.addEventListener('load', function(){
            asleep = true;
            widget.classList.add('asleep');
        });

        /* keep VAIA's ears in sync if the visitor switches language mid-session — updates the
           speech-recognition locale for the NEXT listen cycle (can't hot-swap mid-utterance). */
        var prevOwlLangChange = window.OWL_ON_LANG_CHANGE;
        window.OWL_ON_LANG_CHANGE = function(){
            if (typeof prevOwlLangChange === 'function') prevOwlLangChange();
            if (recog) { try { recog.lang = VAIA_BCP47[window.OWL_LANG || 'en'] || 'en-US'; } catch(e){} }
        };
    })();

/* PUB30, 17 Oct 2026 — Lee: on phones VAIA sits under the menu (Blog / Contact), to the right of the
   headline, and stays there while people scroll. Desktop keeps her in the bottom-left corner. */
(function(){
  var w = document.getElementById('vaia-widget'); if (!w) return;
  function place(){
    if (window.matchMedia('(min-width:900px)').matches) { w.style.top = ''; return; }
    var h = document.querySelector('header');
    var top = h ? h.offsetTop + h.offsetHeight + 10 : 120;
    w.style.top = Math.max(top, 64) + 'px';
  }
  place();
  window.addEventListener('resize', place);
  window.addEventListener('load', place);
})();
