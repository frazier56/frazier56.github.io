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
        /* PUB30 17 Oct: vaia-chat is a members-only endpoint (gateway JWT + server getUser). A visitor
           who is not signed in gets an honest invitation to sign in instead of a silent 401. */
        var VAIA_SIGNIN = {
            en: "I can answer questions once you're signed in with One ID. Tap Sign in at the top — it takes a few seconds.",
            co: "Puedo responder tus preguntas cuando inicies sesión con One ID. Toca Ingresar arriba; toma unos segundos.",
            es: "Puedo responder a tus preguntas en cuanto inicies sesión con One ID. Toca Entrar arriba; tarda unos segundos.",
            de: "Ich kann deine Fragen beantworten, sobald du mit One ID angemeldet bist. Tippe oben auf Login – das dauert nur ein paar Sekunden.",
            ru: "Я смогу ответить на твои вопросы, когда ты войдёшь через One ID. Нажми «Войти» вверху — это займёт пару секунд.",
            zh: "使用 One ID 登录后，我就能回答你的问题。点一下顶部的“登录”，几秒钟就好。",
            pt: "Posso responder às suas perguntas assim que você entrar com o One ID. Toque em Entrar no topo — leva só alguns segundos."
        };
        Object.keys(VAIA_SIGNIN).forEach(function(k){ if (VAIA_STRINGS[k]) VAIA_STRINGS[k].signinNeeded = VAIA_SIGNIN[k]; });
        /* PUB30 17 Oct (Max security review of candidate 6): the visitor only ever sees these controlled lines,
           never raw server error text. */
        var VAIA_LIMIT = {
            en: "I've answered a lot of questions in a short time. Let's pause for a minute, then ask me again.",
            co: "He respondido muchas preguntas en poco tiempo. Hagamos una pausa de un minuto y vuelve a preguntarme.",
            es: "He respondido muchas preguntas en poco tiempo. Hagamos una pausa de un minuto y vuelve a preguntarme.",
            de: "Ich habe in kurzer Zeit viele Fragen beantwortet. Lass uns eine Minute Pause machen, dann frag mich wieder.",
            ru: "За короткое время я ответила на много вопросов. Давай сделаем минутную паузу, а потом спроси снова.",
            zh: "我在短时间内回答了很多问题。我们先休息一分钟，然后再问我吧。",
            pt: "Respondi muitas perguntas em pouco tempo. Vamos fazer uma pausa de um minuto e depois me pergunte de novo."
        };
        var VAIA_REAUTH = {
            en: "Your sign-in has expired. Tap Sign in at the top, then ask me again.",
            co: "Tu sesión expiró. Toca Ingresar arriba y vuelve a preguntarme.",
            es: "Tu sesión ha caducado. Toca Entrar arriba y vuelve a preguntarme.",
            de: "Deine Anmeldung ist abgelaufen. Tippe oben auf Login und frag mich dann noch einmal.",
            ru: "Срок входа истёк. Нажми «Войти» вверху и спроси меня снова.",
            zh: "你的登录已过期。点一下顶部的“登录”，然后再问我。",
            pt: "Sua sessão expirou. Toque em Entrar no topo e me pergunte de novo."
        };
        Object.keys(VAIA_LIMIT).forEach(function(k){ if (VAIA_STRINGS[k]) { VAIA_STRINGS[k].limitLine = VAIA_LIMIT[k]; VAIA_STRINGS[k].reauthLine = VAIA_REAUTH[k]; } });
        var VAIA_KEY = 'sb_publishable_hO1MOsFr6lk0XDC6gizF8g_WfBZ68Tc';
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
        var busy = false, voiceMode = false, asleep = false, everSlept = false, currentAudio = null, activeSpeech = [];
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
        var gen = 0;  /* bumped on every identity change / reset: anything started under an older value is discarded */
        /* One utterance, always finished within a bound (PUB30 17 Oct, Max candidate-7 review): the TTS fetch,
           the audio blob, playback and the browser fallback all end by `limit` at the latest. Only the newest
           utterance may clear the speaking state, and nothing plays once the conversation's identity changed. */
        var speakSeq = 0, MAX_TTS_BYTES = 5242880;
        function speak(text){
            var g = gen, mine = ++speakSeq;
            widget.classList.add('speaking');
            var spoken = phoneticize(String(text || ''));
            var limit = Math.min(60000, 8000 + spoken.length * 120);
            return new Promise(function(done){
                var finished = false, audio = null, url = null, usedFallback = false, rd = null;
                var ctl = (typeof AbortController !== 'undefined') ? new AbortController() : null;
                function finish(timedOut){
                    if (finished) return;
                    finished = true;
                    clearTimeout(timer);
                    if (ctl) { try { ctl.abort(); } catch(e){} }
                    if (rd) { try { rd.cancel(); } catch(e){} rd = null; }   /* also ends a read that is still pending */
                    if (audio) { try { audio.pause(); } catch(e){} if (currentAudio === audio) currentAudio = null; }
                    if (url) { try { URL.revokeObjectURL(url); } catch(e){} }
                    if (timedOut === true && usedFallback && window.speechSynthesis) { try { window.speechSynthesis.cancel(); } catch(e){} }
                    var at = activeSpeech.indexOf(finish); if (at > -1) activeSpeech.splice(at, 1);
                    if (mine === speakSeq) widget.classList.remove('speaking');
                    done();
                }
                var timer = setTimeout(function(){ finish(true); }, limit);
                activeSpeech.push(finish);   /* stopSpeaking() ends every utterance in progress */
                function fallback(){ if (finished || g !== gen) return finish(); usedFallback = true; fallbackSpeak(spoken).then(finish); }
                try {
                    fetch(SUPABASE_URL + '/functions/v1/elevenlabs-tts', {
                        method: 'POST', headers: {'Content-Type':'application/json'},
                        body: JSON.stringify({ text: spoken, voiceId: VAIA_VOICE_ID }),
                        signal: ctl ? ctl.signal : undefined
                    }).then(function(r){
                        if (finished || g !== gen) return finish();
                        var ct = r.headers.get('content-type') || '';
                        var len = parseInt(r.headers.get('content-length') || '0', 10) || 0;
                        if (ct.indexOf('audio') === -1 || len > MAX_TTS_BYTES || !r.body) return fallback();
                        /* stream the audio with a running byte count: stop reading (and cancel) once the RETAINED payload passes 5 MB,
                           and after at most 4096 reads (zero-length chunks included). This bounds what is kept, not every transient buffer. */
                        rd = r.body.getReader(); var chunks = [], total = 0, audioReads = 0;
                        var pump = function(){
                            if (finished || !rd) return Promise.resolve(null);
                            if (++audioReads > 4096) { try { rd.cancel(); } catch(e){} chunks = []; return Promise.resolve('too-big'); }
                            return rd.read().then(function(res){
                                if (finished || g !== gen || !rd) { if (rd) { try { rd.cancel(); } catch(e){} } return null; }
                                if (res.done) return new Blob(chunks, { type: ct.split(';')[0] });
                                var v = res.value || new Uint8Array(0);
                                total += v.byteLength;
                                if (total > MAX_TTS_BYTES) { try { rd.cancel(); } catch(e){} chunks = []; return 'too-big'; }
                                chunks.push(v);
                                return pump();
                            });
                        };
                        return pump().then(function(blob){
                            if (finished || g !== gen) return finish();
                            if (!blob || blob === 'too-big') return fallback();
                            url = URL.createObjectURL(blob);
                            audio = new Audio(url);
                            currentAudio = audio;
                            if (window.vaiaAttachAudio) { try { window.vaiaAttachAudio(audio); } catch (e) {} }
                            audio.onended = finish; audio.onerror = finish;
                            var pl = audio.play(); if (pl && pl.catch) pl.catch(function(){ finish(); });
                        });
                    }).then(null, function(){ if (!finished) fallback(); });
                } catch(e) { fallback(); }
            });
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
                var g1 = gen; speak(m).then(function(){ if (g1 === gen && voiceMode) startListening(); });
                return true;
            }
            if (wantsClose) {
                addMsg('user', text);
                var m2 = vaiaT('closeChat');
                addMsg('vaia', m2);
                var g2 = gen; speak(m2).then(function(){ if (g2 !== gen) return; closePanel(); if (voiceMode) startListening(); });
                return true;
            }
            return false;
        }

        /* ---- conversation identity (PUB30, hardened 17 Oct after Max's candidate-6 security review) ----
           A conversation belongs to exactly one identity key: a member's id, or "anon". Any change —
           sign-out, sign-in, another member, another tab, the shared cookie — bumps `gen`, which
           cancels the request in flight, stops current and queued speech, and clears the transcript.
           Every asynchronous step re-checks `gen` before it touches the page, the history or the voice. */
        var historyOwner = null, authBlockedToken = null, inflight = null;
        function currentIdentity(){ var s = (typeof window.OW_SESSION === 'function') ? window.OW_SESSION() : null; return (s && s.userId && s.accessToken) ? s : null; }
        function idKey(s){ return s ? 'm:' + s.userId : 'anon'; }
        function resetConversation(){
            gen++;
            if (inflight) { try { inflight.cancel(); } catch(e){} inflight = null; }
            stopSpeaking();
            history.length = 0; while (log.firstChild) log.removeChild(log.firstChild);
            historyOwner = null; authBlockedToken = null;
            busy = false; voiceMode = false; stopListening();
            widget.classList.remove('thinking', 'speaking');
        }
        function own(){ if (historyOwner === null) historyOwner = idKey(currentIdentity()); }
        function checkIdentity(){ if (historyOwner !== null && historyOwner !== idKey(currentIdentity())) resetConversation(); }
        window.addEventListener('storage', function(e){ if (!e.key || e.key.indexOf('-auth-token') > -1) checkIdentity(); });
        document.addEventListener('ow:session', checkIdentity);
        window.addEventListener('focus', checkIdentity);
        document.addEventListener('visibilitychange', function(){ if (!document.hidden) checkIdentity(); });

        var MAX_REPLY = 6000, MAX_BYTES = 262144, MAX_EVENTS = 4000, MAX_CHUNKS = 4096, DEADLINE_MS = 30000;

        function askVaia(userText){
            if (busy || !userText) return;
            var who = currentIdentity();
            if (historyOwner !== null && historyOwner !== idKey(who)) resetConversation();
            if (handleLocalIntent(userText)) return;
            historyOwner = idKey(who);
            var myGen = gen;
            var live = function(){ return myGen === gen; };
            busy = true;
            widget.classList.add('thinking');
            addMsg('user', userText);
            history.push({ role:'user', content: userText });
            var replyEl = addMsg('vaia', '…');
            var full = '';
            var spokenUpTo = 0;
            var speakQueue = Promise.resolve();

            /* speak completed sentences as they arrive instead of waiting for the whole reply */
            function queueSentence(s){
                s = s.trim();
                if (!s) return;
                speakQueue = speakQueue.then(function(){
                    if (asleep || !live()) return;
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
            /* a reply that is not from the server: shown, remembered and spoken under the same generation guard */
            function localReply(line, then){
                if (!live()) return;
                full = line; replyEl.textContent = line; history.push({ role:'assistant', content: line });
                widget.classList.remove('thinking'); openPanel();
                speak(line).then(function(){ if (live()) { busy = false; if (then) then(); } });
            }

            if (!who) { voiceMode = false; stopListening(); localReply(vaiaT('signinNeeded')); return; }
            /* 401 already seen for this exact token: do not call the server again until the sign-in changes */
            if (authBlockedToken && authBlockedToken === who.accessToken) { voiceMode = false; stopListening(); localReply(vaiaT('reauthLine')); return; }

            /* ---- one request, exactly one outcome ---- */
            var settled = false, reader = null;
            var ctl = (typeof AbortController !== 'undefined') ? new AbortController() : null;
            function stopTransport(){
                if (ctl) { try { ctl.abort(); } catch(e){} }
                if (reader) { try { reader.cancel(); } catch(e){} }
            }
            var deadline = setTimeout(function(){ settle('timeout'); }, DEADLINE_MS);
            inflight = { cancel: function(){ settle('cancelled'); } };
            /* kind: ok | truncated | timeout | cancelled | limit | auth | error */
            function settle(kind){
                if (settled) return;
                settled = true;
                clearTimeout(deadline);
                stopTransport();
                if (inflight && myGen === gen) inflight = null;
                if (!live()) return;   /* resetConversation() already cleared busy, speech and transcript */
                if (kind === 'cancelled') {   /* she was put to sleep mid-answer: drop the request quietly */
                    if (replyEl && replyEl.parentNode && !full) replyEl.parentNode.removeChild(replyEl);
                    widget.classList.remove('thinking');
                    busy = false;
                    return;
                }
                widget.classList.remove('thinking');
                if (kind === 'ok' || kind === 'truncated') {
                    if (!full) full = vaiaT('noCatch');
                    else if (kind === 'truncated') full += '…';
                    replyEl.textContent = full;
                    history.push({ role:'assistant', content: full });
                    drainSentences(true);
                    speakQueue.then(function(){ if (!live()) return; busy = false; if (voiceMode && !asleep) startListening(); });
                    return;
                }
                if (kind === 'auth') { authBlockedToken = who.accessToken; voiceMode = false; stopListening(); }
                var line = kind === 'limit' ? vaiaT('limitLine') : kind === 'auth' ? vaiaT('reauthLine') : vaiaT('connError');
                full = line; replyEl.textContent = line;
                history.push({ role:'assistant', content: line });
                speak(line).then(function(){
                    if (!live()) return;
                    busy = false;
                    if (kind === 'limit') {
                        /* out of budget for now — go quiet instead of re-asking straight into the limit */
                        asleep = true; voiceMode = false;
                        widget.classList.remove('listening', 'speaking');
                        widget.classList.add('asleep');
                        everSlept = true;
                        return;
                    }
                    if (kind !== 'auth' && voiceMode && !asleep) startListening();
                });
            }

            var bytes = 0, events = 0, chunks = 0, carry = '';
            function onLine(line){
                line = line.trim();
                if (line.indexOf('data:') !== 0) return true;
                if (++events > MAX_EVENTS) return false;
                var payload = line.slice(5).trim();
                if (payload === '[DONE]') return true;
                try {
                    var json = JSON.parse(payload);
                    var delta = json.choices && json.choices[0] && json.choices[0].delta && json.choices[0].delta.content;
                    if (typeof delta === 'string' && delta) {
                        if (full.length + delta.length > MAX_REPLY) { full += delta.slice(0, MAX_REPLY - full.length); replyEl.textContent = full; return false; }
                        full += delta; replyEl.textContent = full; log.scrollTop = log.scrollHeight; drainSentences(false);
                    }
                } catch(e){}
                return true;
            }
            try {
                fetch(SUPABASE_URL + '/functions/v1/vaia-chat', {
                    method:'POST', headers:{'Content-Type':'application/json', 'apikey': VAIA_KEY, 'Authorization': 'Bearer ' + who.accessToken},
                    /* intentionally NOT sending mode:'voice' — that server-side 160-token cap truncated real replies (Jul 14) */
                    body: JSON.stringify({ messages: history, app: 'homepage', lang: window.OWL_LANG || 'en' }),
                    signal: ctl ? ctl.signal : undefined
                }).then(function(r){
                    if (settled) { try { r.body && r.body.cancel(); } catch(e){} return; }
                    if (!live()) return settle('cancelled');
                    if (r.status === 401 || r.status === 403) return settle('auth');
                    if (r.status === 429) return settle('limit');
                    if (!r.ok || !r.body) {
                        /* read only a small, bounded error body, and only for the rate-limit flag — its text is never shown */
                        if (!r.body) return settle('error');
                        reader = r.body.getReader();
                        /* at most 4096 BYTES and 64 reads of an error body; only a literal rateLimited:true counts; its text is never shown */
                        var parts = [], took = 0, reads = 0;
                        var errDone = function(){
                            var buf = new Uint8Array(took), o = 0;
                            parts.forEach(function(x){ buf.set(x, o); o += x.byteLength; });
                            var lim = false;
                            try { var j = JSON.parse(new TextDecoder().decode(buf)); lim = !!j && j.rateLimited === true; } catch(e){}
                            settle(lim ? 'limit' : 'error');
                        };
                        var readErr = function(){
                            if (settled) return;
                            if (reads >= 64) return errDone();   /* ceiling checked BEFORE the next read: at most 64 reads */
                            reads++;
                            return reader.read().then(function(res){
                                if (settled) return;
                                if (res.done) return errDone();
                                var v = res.value || new Uint8Array(0), room = 4096 - took;
                                if (v.byteLength) { var part = v.subarray(0, Math.min(room, v.byteLength)); parts.push(part); took += part.byteLength; }
                                if (took >= 4096) return errDone();
                                return readErr();
                            });
                        };
                        return readErr();
                    }
                    var ctype = (r.headers.get('content-type') || '').toLowerCase();
                    if (ctype.indexOf('text/event-stream') === -1) return settle('error');
                    reader = r.body.getReader();
                    var decoder = new TextDecoder();
                    function pump(){
                        return reader.read().then(function(res){
                            if (settled) return;
                            if (!live()) return settle('cancelled');
                            if (res.done) {
                                /* the last event may arrive without a trailing newline */
                                var tail = (carry + decoder.decode()).split('\n'); carry = '';
                                for (var t = 0; t < tail.length; t++) { if (tail[t] && !onLine(tail[t])) return settle('truncated'); }
                                return settle('ok');
                            }
                            bytes += res.value.byteLength;
                            if (++chunks > MAX_CHUNKS || bytes > MAX_BYTES) return settle(full ? 'truncated' : 'error');
                            var lines = (carry + decoder.decode(res.value, {stream:true})).split('\n');
                            carry = lines.pop();
                            if (carry.length > 65536) return settle(full ? 'truncated' : 'error');
                            for (var i = 0; i < lines.length; i++) { if (!onLine(lines[i])) return settle('truncated'); }
                            return pump();
                        });
                    }
                    return pump();
                }).then(null, function(){ settle('error'); });
            } catch(e) { settle('error'); }
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
                    own(); history.push({ role:'assistant', content: line });
                    var gr = gen;
                    speak(line).then(function(){
                        if (gr !== gen) return;
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
            activeSpeech.slice().forEach(function(f){ try { f(); } catch(e){} });
        }

        function sleep(){
            asleep = true;
            voiceMode = false;
            if (inflight) { try { inflight.cancel(); } catch(e){} }
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
            var gw = gen;
            var goListen = function(){ if (gw !== gen || asleep) return; voiceMode = true; startListening(); };
            if (!everWoken) {
                /* Sleep-first (Lee, Jul 16): the FIRST tap is the introduction —
                   she never speaks before being touched. */
                everWoken = true;
                var firstWake = vaiaT('firstWake');
                own(); history.push({ role:'assistant', content: firstWake });
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
        document.addEventListener('ow:lang', function(){ if (recog) { try { recog.lang = VAIA_BCP47[window.OWL_LANG || 'en'] || 'en-US'; } catch(e){} } });
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
  /* browsers without :has() (Safari < 15.4, Firefox < 121) still get the desktop room for VAIA's hero slot */
  var heroCopy = document.querySelector('.hero-copy');
  if (heroCopy && heroCopy.querySelector(':scope > .vaia-hero-slot')) heroCopy.classList.add('vaia-has-slot');
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
