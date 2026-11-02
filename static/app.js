/**
 * JARVIS Command Center Futuristic HUD & Full-Duplex Voice Telephony Engine
 */

document.addEventListener('DOMContentLoaded', () => {
    initClock();
    initHoloGlobe();
    initMemoryCanvas();
    initInteractions();
    initJarvisTelephony();
    initSidebarDrawers();
});

// ==========================================
// 1. LIVE DIGITAL CLOCK
// ==========================================
function initClock() {
    const timeEl = document.getElementById('clockTime');
    const dateEl = document.getElementById('clockDate');
    
    function update() {
        const now = new Date();
        const optionsDate = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
        if (dateEl) dateEl.textContent = now.toLocaleDateString('en-US', optionsDate);
        
        let hours = now.getHours();
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        const ampm = hours >= 12 ? 'pm' : 'am';
        hours = hours % 12;
        hours = hours ? hours : 12;
        
        if (timeEl) timeEl.textContent = `${hours}:${minutes}:${seconds} ${ampm}`;
    }
    update();
    setInterval(update, 1000);
}

// ==========================================
// 2. HOLOGRAPHIC 3D GLOBE / ORB CANVAS
// ==========================================
function initHoloGlobe() {
    const canvas = document.getElementById('holoCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let width = canvas.width = canvas.parentElement.clientWidth;
    let height = canvas.height = canvas.parentElement.clientHeight;

    window.addEventListener('resize', () => {
        if (!canvas.parentElement) return;
        width = canvas.width = canvas.parentElement.clientWidth;
        height = canvas.height = canvas.parentElement.clientHeight;
    });

    let angle = 0;

    function render() {
        ctx.clearRect(0, 0, width, height);
        const cx = width / 2;
        const cy = height / 2;
        const radius = Math.min(width, height) * 0.36;

        // Outer radial ambient glow
        const grad = ctx.createRadialGradient(cx, cy, radius * 0.1, cx, cy, radius * 1.3);
        grad.addColorStop(0, 'rgba(0, 240, 255, 0.22)');
        grad.addColorStop(0.5, 'rgba(0, 150, 255, 0.06)');
        grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(cx, cy, radius * 1.3, 0, Math.PI * 2);
        ctx.fill();

        // 3D Wireframe Latitude Lines
        ctx.strokeStyle = 'rgba(0, 240, 255, 0.25)';
        ctx.lineWidth = 1;
        const numLat = 7;
        for (let i = -numLat; i <= numLat; i++) {
            const latRadius = radius * Math.cos((i / (numLat + 1)) * (Math.PI / 2));
            const yOffset = radius * Math.sin((i / (numLat + 1)) * (Math.PI / 2));
            ctx.beginPath();
            ctx.ellipse(cx, cy + yOffset, latRadius, latRadius * 0.3, 0, 0, Math.PI * 2);
            ctx.stroke();
        }

        // 3D Wireframe Longitude Lines (Rotating)
        ctx.strokeStyle = 'rgba(0, 240, 255, 0.4)';
        const numLong = 6;
        for (let i = 0; i < numLong; i++) {
            const currentAngle = angle + (i * Math.PI) / numLong;
            const xRadius = radius * Math.abs(Math.sin(currentAngle));
            ctx.beginPath();
            ctx.ellipse(cx, cy, xRadius, radius, 0, 0, Math.PI * 2);
            ctx.stroke();
        }

        // Orbital Ring with Orbiting Particle
        ctx.strokeStyle = 'rgba(0, 240, 255, 0.7)';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.ellipse(cx, cy, radius * 1.35, radius * 0.45, -0.25, 0, Math.PI * 2);
        ctx.stroke();

        const orbX = cx + Math.cos(angle * 1.8) * (radius * 1.35);
        const orbY = cy + Math.sin(angle * 1.8) * (radius * 0.45);
        ctx.fillStyle = '#00f0ff';
        ctx.shadowColor = '#00f0ff';
        ctx.shadowBlur = 12;
        ctx.beginPath();
        ctx.arc(orbX, orbY, 4, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;

        angle += 0.012;
        requestAnimationFrame(render);
    }
    render();
}

// ==========================================
// 3. MEMORY CONSTELLATION CANVAS
// ==========================================
function initMemoryCanvas() {
    const canvas = document.getElementById('memoryCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const width = canvas.width = 160;
    const height = canvas.height = 65;

    const nodes = [
        { x: 20, y: 35, vx: 0.2, vy: 0.1 },
        { x: 45, y: 20, vx: -0.1, vy: 0.2 },
        { x: 70, y: 48, vx: 0.15, vy: -0.15 },
        { x: 100, y: 25, vx: -0.2, vy: 0.1 },
        { x: 130, y: 38, vx: 0.1, vy: 0.2 }
    ];

    function draw() {
        ctx.clearRect(0, 0, width, height);

        ctx.strokeStyle = 'rgba(0, 240, 255, 0.35)';
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        for (let i = 0; i < nodes.length; i++) {
            if (i === 0) ctx.moveTo(nodes[i].x, nodes[i].y);
            else ctx.lineTo(nodes[i].x, nodes[i].y);
        }
        ctx.stroke();

        nodes.forEach(n => {
            n.x += n.vx;
            n.y += n.vy;
            if (n.x < 10 || n.x > width - 10) n.vx *= -1;
            if (n.y < 10 || n.y > height - 10) n.vy *= -1;

            ctx.fillStyle = '#00f0ff';
            ctx.shadowColor = '#00f0ff';
            ctx.shadowBlur = 6;
            ctx.beginPath();
            ctx.arc(n.x, n.y, 2.5, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;
        });

        requestAnimationFrame(draw);
    }
    draw();
}

// ============================================================
// 4. 📞 JARVIS FULL-DUPLEX VOICE TELEPHONY SYSTEM ("TELEPON JARVIS")
// ============================================================
let isCallActive = false;
let callSeconds = 0;
let callTimerInterval = null;
let recognition = null;
let isJarvisSpeaking = false;
let audioCtx = null;
let micStream = null;
let micAnalyser = null;
let micAnimFrame = null;
let silenceTimer = null;
let currentSpeechAccumulator = '';

// Sound Effects via Web Audio API (Synthesized Sci-Fi Audio)
function playTone(freq1, freq2, duration, type = 'sine') {
    try {
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if (audioCtx.state === 'suspended') audioCtx.resume();

        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq1, audioCtx.currentTime);
        if (freq2) osc.frequency.exponentialRampToValueAtTime(freq2, audioCtx.currentTime + duration);

        gain.gain.setValueAtTime(0.12, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);

        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + duration);
    } catch (e) {
        // Fallback silent
    }
}

function sfxCallConnect() {
    playTone(440, 880, 0.35);
    setTimeout(() => playTone(660, 1320, 0.45), 180);
}

function sfxCallEnd() {
    playTone(700, 300, 0.4);
}

function sfxJarvisReady() {
    playTone(880, 1100, 0.2);
}

function initJarvisTelephony() {
    const callModal = document.getElementById('callModal');
    const startCallBtns = [
        document.getElementById('talkJarvisBtn'),
        document.getElementById('sidebarMicBtn'),
        document.getElementById('quickVoiceBtn'),
        document.getElementById('callJarvisBtnSide')
    ];
    const endCallBtn = document.getElementById('endCallBtn');
    const minimizeCallBtn = document.getElementById('minimizeCallBtn');
    const floatingPill = document.getElementById('floatingCallPill');
    const callStateText = document.getElementById('callStateText');
    const callStateSub = document.getElementById('callStateSub');
    const callTimerEl = document.getElementById('callTimer');
    const transcriptBox = document.getElementById('callTranscriptBox');
    const langSelect = document.getElementById('callLangSelect');
    const micStatusText = document.getElementById('micStatusText');
    const micPermissionBanner = document.getElementById('micPermissionBanner');
    const btnRequestMic = document.getElementById('btnRequestMic');
    const callTextInput = document.getElementById('callTextInput');
    const callSendBtn = document.getElementById('callSendBtn');

    // 1. Microphone Hardware Acquisition & Live Volume Visualizer
    async function setupMicrophoneHardware() {
        try {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                if (micStatusText) micStatusText.textContent = "Browser tidak mendukung mic API.";
                return;
            }

            micStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
            if (micPermissionBanner) micPermissionBanner.style.display = 'none';
            if (micStatusText) micStatusText.textContent = "Mikrofon aktif & mendengarkan...";

            if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            if (audioCtx.state === 'suspended') audioCtx.resume();

            const source = audioCtx.createMediaStreamSource(micStream);
            micAnalyser = audioCtx.createAnalyser();
            micAnalyser.fftSize = 64;
            source.connect(micAnalyser);

            startMicVolumeLoop();
        } catch (err) {
            console.warn("Microphone access pending or denied:", err);
            if (micPermissionBanner) micPermissionBanner.style.display = 'flex';
            if (micStatusText) micStatusText.textContent = "⚠️ Menunggu izin mikrofon...";
        }
    }

    if (btnRequestMic) {
        btnRequestMic.addEventListener('click', () => {
            setupMicrophoneHardware();
        });
    }

    function startMicVolumeLoop() {
        if (!micAnalyser) return;
        const dataArray = new Uint8Array(micAnalyser.frequencyBinCount);
        const bars = [
            document.getElementById('mbar1'),
            document.getElementById('mbar2'),
            document.getElementById('mbar3'),
            document.getElementById('mbar4'),
            document.getElementById('mbar5')
        ];

        function checkLevel() {
            if (!isCallActive) return;
            micAnalyser.getByteFrequencyData(dataArray);
            let sum = 0;
            for (let i = 0; i < dataArray.length; i++) sum += dataArray[i];
            const avg = sum / dataArray.length;

            bars.forEach((bar, idx) => {
                if (bar) {
                    const h = Math.max(4, Math.min(22, (avg * 0.4) + (idx * 2)));
                    bar.style.height = `${h}px`;
                    bar.style.background = avg > 15 ? '#00ffaa' : '#38bdf8';
                }
            });

            micAnimFrame = requestAnimationFrame(checkLevel);
        }
        checkLevel();
    }

    // 2. Continuous Speech Recognition Engine
    function initSpeechEngine() {
        if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
            if (micStatusText) micStatusText.textContent = "Gunakan teks di bawah (Speech API tidak didukung browser ini).";
            return;
        }

        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRec();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = langSelect ? langSelect.value : 'id-ID';

        if (langSelect) {
            langSelect.addEventListener('change', () => {
                recognition.lang = langSelect.value;
                if (isCallActive && !isJarvisSpeaking) {
                    try { recognition.stop(); } catch (_) {}
                    setTimeout(() => { try { recognition.start(); } catch (_) {} }, 200);
                }
            });
        }

        recognition.onstart = () => {
            if (micStatusText && !isJarvisSpeaking) micStatusText.textContent = "Mendengarkan suara Anda...";
        };

        recognition.onresult = (event) => {
            if (isJarvisSpeaking) return;

            let interimStr = '';
            let finalStr = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalStr += event.results[i][0].transcript;
                } else {
                    interimStr += event.results[i][0].transcript;
                }
            }

            const currentSpoken = (finalStr || interimStr).trim();
            if (!currentSpoken) return;

            // Live preview user speech in transcript
            showInterimUserSpeech(currentSpoken);

            // Silence debounce: If user pauses for 1100ms, auto-dispatch to JARVIS!
            clearTimeout(silenceTimer);
            silenceTimer = setTimeout(() => {
                if (currentSpoken.length >= 2 && !isJarvisSpeaking) {
                    commitUserSpeech(currentSpoken);
                }
            }, 1100);
        };

        recognition.onerror = (e) => {
            console.log("Speech recognition event:", e.error);
            if (e.error === 'not-allowed') {
                if (micPermissionBanner) micPermissionBanner.style.display = 'flex';
                if (micStatusText) micStatusText.textContent = "⚠️ Izin mic belum diberikan.";
            } else if (e.error === 'network') {
                if (micStatusText) micStatusText.textContent = "Koneksi suara offline. Anda bisa gunakan chat di bawah.";
            } else if (isCallActive && !isJarvisSpeaking && e.error === 'no-speech') {
                // Normal silence timeout, restart recognition
                try { recognition.start(); } catch (_) {}
            }
        };

        recognition.onend = () => {
            // Keep listening continuously if call is still active
            if (isCallActive && !isJarvisSpeaking) {
                setTimeout(() => {
                    try { recognition.start(); } catch (_) {}
                }, 150);
            }
        };
    }

    initSpeechEngine();

    function showInterimUserSpeech(text) {
        let interimEl = document.getElementById('interimUserBubble');
        if (!interimEl) {
            interimEl = document.createElement('div');
            interimEl.id = 'interimUserBubble';
            interimEl.className = 'transcript-line user';
            transcriptBox.appendChild(interimEl);
        }
        interimEl.innerHTML = `<strong>User:</strong> <span style="opacity: 0.85;">${escapeHtml(text)}...</span>`;
        transcriptBox.scrollTop = transcriptBox.scrollHeight;
    }

    async function commitUserSpeech(text) {
        clearTimeout(silenceTimer);
        const interimEl = document.getElementById('interimUserBubble');
        if (interimEl) interimEl.remove();

        addTranscriptLine('User', text);
        callStateText.textContent = "JARVIS ANALYZING & EXECUTING...";
        callStateSub.textContent = `Memproses: "${text}"`;
        playTone(600, 750, 0.2);

        try {
            const response = await fetch('/api/v1/agent/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text,
                    session_id: 'voice_call_session',
                    voice_mode: true
                })
            });

            const data = await response.json();
            const reply = data.reply_text || "Saya telah menyelesaikan tugas tersebut.";

            if (data.is_task && data.task_result) {
                const streamBox = document.getElementById('executionStream');
                if (streamBox) renderExecutionResult(data.task_result, streamBox);
            }

            addTranscriptLine('JARVIS', reply);
            speakInCall(reply);
        } catch (err) {
            const errMsg = "Maaf, terjadi kendala saat memproses instruksi.";
            addTranscriptLine('JARVIS', errMsg);
            speakInCall(errMsg);
        }
    }

    // In-Call Text Input Dispatch (allows typing while in call too)
    if (callSendBtn && callTextInput) {
        const handleSend = () => {
            const txt = callTextInput.value.trim();
            if (!txt) return;
            callTextInput.value = '';
            commitUserSpeech(txt);
        };
        callSendBtn.addEventListener('click', handleSend);
        callTextInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') handleSend();
        });
    }

    // Start Call Trigger
    startCallBtns.forEach(btn => {
        if (btn) {
            btn.addEventListener('click', () => {
                startJarvisCall();
            });
        }
    });

    if (endCallBtn) endCallBtn.addEventListener('click', () => endJarvisCall());

    if (minimizeCallBtn) {
        minimizeCallBtn.addEventListener('click', () => {
            callModal.classList.remove('active');
            floatingPill.classList.add('active');
        });
    }

    if (floatingPill) {
        floatingPill.addEventListener('click', () => {
            floatingPill.classList.remove('active');
            callModal.classList.add('active');
        });
    }

    async function startJarvisCall() {
        if (isCallActive) {
            callModal.classList.add('active');
            floatingPill.classList.remove('active');
            return;
        }

        isCallActive = true;
        callSeconds = 0;
        callModal.classList.add('active');
        floatingPill.classList.remove('active');
        document.getElementById('sidebarMicBtn')?.classList.add('calling');

        // Play phone connect sound
        sfxCallConnect();

        // 1. Request microphone hardware immediately
        await setupMicrophoneHardware();

        // 2. Start speech recognition
        if (recognition) {
            try { recognition.start(); } catch (_) {}
        }

        // 3. Start call timer
        callTimerInterval = setInterval(() => {
            callSeconds++;
            const mins = String(Math.floor(callSeconds / 60)).padStart(2, '0');
            const secs = String(callSeconds % 60).padStart(2, '0');
            if (callTimerEl) callTimerEl.textContent = `${mins}:${secs}`;
            const pillTimer = document.getElementById('floatingCallTimer');
            if (pillTimer) pillTimer.textContent = `${mins}:${secs}`;
        }, 1000);

        callStateText.textContent = "JARVIS CONNECTED";
        callStateSub.textContent = "Terhubung ke JARVIS AI Core...";
        if (transcriptBox) transcriptBox.innerHTML = '';

        // Initial Greeting from JARVIS
        setTimeout(() => {
            const greeting = "Halo Bos! JARVIS aktif dan terhubung. Saya sedang mendengarkan. Ada yang bisa saya bantu atau kerjakan untuk Anda?";
            addTranscriptLine('JARVIS', greeting);
            speakInCall(greeting);
        }, 500);
    }

    function endJarvisCall() {
        isCallActive = false;
        clearInterval(callTimerInterval);
        if (silenceTimer) clearTimeout(silenceTimer);
        if (window.speechSynthesis) window.speechSynthesis.cancel();
        if (recognition) {
            try { recognition.stop(); } catch (_) {}
        }
        if (micAnimFrame) cancelAnimationFrame(micAnimFrame);
        if (micStream) {
            micStream.getTracks().forEach(t => t.stop());
            micStream = null;
        }

        sfxCallEnd();
        callModal.classList.remove('active');
        floatingPill.classList.remove('active');
        document.getElementById('sidebarMicBtn')?.classList.remove('calling');
        callStateText.textContent = "CALL ENDED";
    }

    function speakInCall(text) {
        if (!('speechSynthesis' in window)) return;

        window.speechSynthesis.cancel();
        isJarvisSpeaking = true;
        callStateText.textContent = "JARVIS IS SPEAKING...";
        callStateSub.textContent = "Mendengarkan jawaban JARVIS...";
        if (micStatusText) micStatusText.textContent = "JARVIS sedang berbicara...";

        // Temporarily pause recognition to avoid capturing own voice
        if (recognition) {
            try { recognition.stop(); } catch (_) {}
        }

        const utterance = new SpeechSynthesisUtterance(text);
        const isEnglish = (langSelect && langSelect.value === 'en-GB');

        const voices = window.speechSynthesis.getVoices();
        if (isEnglish) {
            utterance.lang = 'en-GB';
            const britishVoice = voices.find(v => v.lang.includes('en-GB') || v.name.includes('UK') || v.name.includes('British') || v.name.includes('George'));
            if (britishVoice) utterance.voice = britishVoice;
            utterance.rate = 1.0;
            utterance.pitch = 0.95;
        } else {
            utterance.lang = 'id-ID';
            const indoVoice = voices.find(v => v.lang.includes('id') || v.name.includes('Indonesian') || v.name.includes('Damayanti') || v.name.includes('Ardi'));
            if (indoVoice) utterance.voice = indoVoice;
            utterance.rate = 1.05;
            utterance.pitch = 1.0;
        }

        utterance.onend = () => {
            isJarvisSpeaking = false;
            callStateText.textContent = "JARVIS LISTENING...";
            callStateSub.textContent = "Silakan bicara, saya mendengarkan...";
            if (micStatusText) micStatusText.textContent = "Mendengarkan suara Anda...";
            sfxJarvisReady();

            // Resume speech recognition for continuous duplex telephone conversation
            if (isCallActive && recognition) {
                setTimeout(() => {
                    try { recognition.start(); } catch (_) {}
                }, 200);
            }
        };

        utterance.onerror = () => {
            isJarvisSpeaking = false;
            if (isCallActive && recognition) {
                setTimeout(() => {
                    try { recognition.start(); } catch (_) {}
                }, 200);
            }
        };

        window.speechSynthesis.speak(utterance);
    }

    function addTranscriptLine(sender, text) {
        if (!transcriptBox) return;
        const line = document.createElement('div');
        line.className = `transcript-line ${sender.toLowerCase()}`;
        line.innerHTML = `<strong>${sender}:</strong> <span>${escapeHtml(text)}</span>`;
        transcriptBox.appendChild(line);
        transcriptBox.scrollTop = transcriptBox.scrollHeight;
    }
}

        window.speechSynthesis.speak(utterance);
    }

    function addTranscriptLine(sender, text) {
        if (!transcriptBox) return;
        const line = document.createElement('div');
        line.className = `transcript-line ${sender.toLowerCase()}`;
        line.innerHTML = `<strong>${sender}:</strong> <span>${escapeHtml(text)}</span>`;
        transcriptBox.appendChild(line);
        transcriptBox.scrollTop = transcriptBox.scrollHeight;
    }
}

// ==========================================
// 5. MODAL TASK EXECUTION (TEXT HUD)
// ==========================================
function initInteractions() {
    const modal = document.getElementById('taskModal');
    const openBtns = [
        document.getElementById('quickNewTaskBtn'),
        document.getElementById('quickWorkflowBtn')
    ];
    const closeBtn = document.getElementById('closeModalBtn');
    const submitBtn = document.getElementById('submitTaskBtn');
    const promptInput = document.getElementById('promptInput');
    const streamBox = document.getElementById('executionStream');

    openBtns.forEach(btn => {
        if (btn) btn.addEventListener('click', () => modal.classList.add('open'));
    });

    if (closeBtn) closeBtn.addEventListener('click', () => modal.classList.remove('open'));

    // Preset prompts
    document.querySelectorAll('.preset-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            promptInput.value = chip.getAttribute('data-prompt');
        });
    });

    // Execute Autonomous Task via FastAPI backend
    if (submitBtn) {
        submitBtn.addEventListener('click', async () => {
            const prompt = promptInput.value.trim();
            if (!prompt) return;

            streamBox.innerHTML = `
                <div class="execution-step-pill">INITIATING JARVIS ORCHESTRATION</div>
                <p style="color: #38bdf8;">Mengirim instruksi ke Coordinator Agent...</p>
                <div style="margin-top: 10px; display: flex; align-items: center; gap: 8px;">
                   <div class="pulse-dot"></div>
                   <span style="font-size: 12px; color: #94a3b8;">Plan -> Execute -> Verify -> Output</span>
                </div>
            `;
            submitBtn.disabled = true;
            submitBtn.textContent = 'EXECUTING...';

            try {
                const response = await fetch('/api/v1/agent/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: prompt,
                        session_id: 'jarvis_hud_' + Date.now()
                    })
                });

                const data = await response.json();
                renderExecutionResult(data, streamBox);

                // Vocal feedback
                playTone(660, 990, 0.3);
            } catch (err) {
                streamBox.innerHTML = `<p style="color: #ef4444;">Error executing task: ${err.message}</p>`;
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'EXECUTE WITH JARVIS';
            }
        });
    }
}

function renderExecutionResult(data, streamBox) {
    if (!streamBox) return;
    let logsHtml = (data.logs || []).map(l => `<div style="font-size: 11px; color: #94a3b8;">• ${escapeHtml(l)}</div>`).join('');
    
    let verifHtml = '';
    if (data.verification) {
        const badgeColor = data.verification.is_passed ? '#00ffaa' : '#fb923c';
        verifHtml = `
            <div style="margin: 12px 0; padding: 8px 12px; background: rgba(0, 240, 255, 0.08); border-left: 3px solid ${badgeColor}; border-radius: 4px;">
                <b style="color: ${badgeColor};">QA Verification (Score: ${(data.verification.score * 100).toFixed(0)}%)</b>:
                <span style="font-size: 12px; color: #e2e8f0;">${escapeHtml(data.verification.critique || '')}</span>
            </div>
        `;
    }

    let formattedOutput = (data.output || '').replace(/\n/g, '<br/>');

    streamBox.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(0,240,255,0.2); padding-bottom: 8px; margin-bottom: 10px;">
           <span class="execution-step-pill" style="margin: 0;">TASK COMPLETED: ${(data.status || 'COMPLETED').toUpperCase()}</span>
           <span style="font-size: 11px; color: #00ffaa;">✓ Verified by Critic</span>
        </div>
        <div style="margin-bottom: 12px;">
           <span style="font-size: 11px; color: #38bdf8; font-weight: bold;">EXECUTION LOGS:</span>
           ${logsHtml}
        </div>
        ${verifHtml}
        <div style="background: rgba(10, 24, 46, 0.7); padding: 14px; border-radius: 6px; border: 1px solid rgba(0,240,255,0.15);">
           <span style="font-size: 12px; font-weight: bold; color: #00f0ff;">OUTPUT RESULT:</span>
           <div style="margin-top: 8px; font-size: 13px; color: #f8fafc; line-height: 1.6;">
               ${formattedOutput}
           </div>
        </div>
    `;
}

// ==========================================
// 6. SIDEBAR VIEWS & DRAWERS ACTIVATION
// ==========================================
function initSidebarDrawers() {
    const drawer = document.getElementById('sideDrawer');
    const drawerTitle = document.getElementById('drawerTitle');
    const drawerContent = document.getElementById('drawerContent');
    const closeDrawerBtn = document.getElementById('closeDrawerBtn');

    if (closeDrawerBtn) {
        closeDrawerBtn.addEventListener('click', () => drawer.classList.remove('open'));
    }

    // Sidebar navigation clicks
    const navItems = document.querySelectorAll('.nav-menu .nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', async () => {
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');

            const text = item.querySelector('span').textContent.trim();
            if (text === 'Command Center') {
                drawer.classList.remove('open');
                return;
            }

            openDrawer(text);
        });
    });

    async function openDrawer(title) {
        drawerTitle.textContent = title.toUpperCase();
        drawerContent.innerHTML = `<div style="text-align:center; padding: 20px; color: var(--cyan-primary);">Mengambil data ${title}...</div>`;
        drawer.classList.add('open');

        if (title === 'Tasks') {
            drawerContent.innerHTML = `
                <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 8px;">Daftar Tugas Otonom Terkini:</div>
                <div class="hud-card" style="padding: 10px;">
                    <div style="display:flex; justify-content:space-between; font-weight:bold; color:#00ffaa; font-size:12px;">
                        <span>TASK-01: Quiz Solver</span><span>PASSED (1.00)</span>
                    </div>
                    <div style="font-size:11px; color:#94a3b8; margin-top:4px;">Analisis ACID Relational Database & Evaluasi Opsi.</div>
                </div>
                <div class="hud-card" style="padding: 10px;">
                    <div style="display:flex; justify-content:space-between; font-weight:bold; color:#00ffaa; font-size:12px;">
                        <span>TASK-02: Academic Essay</span><span>VERIFIED</span>
                    </div>
                    <div style="font-size:11px; color:#94a3b8; margin-top:4px;">Penerapan Multi-Agent & Feedback Loop.</div>
                </div>
                <div class="hud-card" style="padding: 10px;">
                    <div style="display:flex; justify-content:space-between; font-weight:bold; color:#00ffaa; font-size:12px;">
                        <span>TASK-03: Python Sandbox</span><span>TESTED OK</span>
                    </div>
                    <div style="font-size:11px; color:#94a3b8; margin-top:4px;">Pembuatan fungsi data aggregation dan unit test.</div>
                </div>
            `;
        } else if (title === 'Memory') {
            try {
                const res = await fetch('/api/v1/agent/memory/voice_session');
                const data = await res.json();
                let itemsHtml = (data.items || []).map(m => `
                    <div class="hud-card" style="padding: 10px;">
                        <span style="font-size:10px; color:var(--cyan-primary); font-family:var(--font-hud);">${escapeHtml(m.key)}</span>
                        <div style="font-size:12px; color:#fff; margin-top:4px;">${escapeHtml(m.content)}</div>
                    </div>
                `).join('');

                drawerContent.innerHTML = `
                    <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 8px;">
                        Working Context & Persistent Knowledge (SQLite):
                    </div>
                    ${itemsHtml || '<div style="color:#94a3b8; font-size:12px;">Belum ada memori sesi tersimpan. Bicara atau kirim tugas ke JARVIS untuk mengisinya!</div>'}
                `;
            } catch (e) {
                drawerContent.innerHTML = `<div style="color:#ef4444;">Gagal memuat memori.</div>`;
            }
        } else if (title === 'Conversations') {
            drawerContent.innerHTML = `
                <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 8px;">Riwayat Dialog Suara & Teks:</div>
                <div class="hud-card" style="padding: 10px;">
                    <b style="color:var(--cyan-muted);">User:</b> "Halo Jarvis, apa kabar?"<br/>
                    <b style="color:#00ffaa;">JARVIS:</b> "Kondisi sistem dan memori berada dalam performa puncak, seratus persen siap melayani Anda."
                </div>
                <div class="hud-card" style="padding: 10px;">
                    <b style="color:var(--cyan-muted);">User:</b> "Tolong selesaikan soal pilihan ganda ACID"<br/>
                    <b style="color:#00ffaa;">JARVIS:</b> "Jawaban yang tepat adalah Opsi B. Konsistensi menjaga integritas status database."
                </div>
            `;
        } else if (title === 'Tools & Skills') {
            drawerContent.innerHTML = `
                <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 8px;">Alat Bantu Agen yang Aktif:</div>
                <div class="hud-card" style="padding: 10px;">
                    <b style="color:#00f0ff;">1. Code Sandbox Executor (AST Validator)</b>
                    <p style="font-size:11px; color:#94a3b8; margin-top:4px;">Memvalidasi kebenaran sintaks Python secara statis dan menjalankan uji assert pada subprocess terisolasi.</p>
                </div>
                <div class="hud-card" style="padding: 10px;">
                    <b style="color:#00f0ff;">2. Search & Reference Tool</b>
                    <p style="font-size:11px; color:#94a3b8; margin-top:4px;">Mengekstrak informasi kredibel dan materi pendukung esai serta analisis analitis.</p>
                </div>
                <div class="hud-card" style="padding: 10px;">
                    <b style="color:#00f0ff;">3. Dual-Layer Memory Engine</b>
                    <p style="font-size:11px; color:#94a3b8; margin-top:4px;">Short-term working context window + Long-term SQLite Vector/Keyword DB.</p>
                </div>
            `;
        } else if (title === 'Calendar') {
            drawerContent.innerHTML = `
                <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 8px;">Jadwal Misi & Agenda:</div>
                <div class="timeline-item"><span class="timeline-time">09:30</span><span>Daily Standup Team</span><span style="color:#00ffaa;">Done</span></div>
                <div class="timeline-item"><span class="timeline-time">12:00</span><span>Finalize HUD Spacing</span><span>in 42 min</span></div>
                <div class="timeline-item"><span class="timeline-time">14:00</span><span>Voice Pipeline Test</span><span>in 2h 42m</span></div>
                <div class="timeline-item"><span class="timeline-time">16:30</span><span>Executive Review V1</span><span>in 5h 12m</span></div>
            `;
        } else {
            drawerContent.innerHTML = `
                <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 8px;">Modul ${escapeHtml(title)}:</div>
                <div class="hud-card" style="padding: 14px;">
                    <p style="font-size:12px; color:#fff;">Status Modul: <b style="color:#00ffaa;">Active & Monitored</b></p>
                    <p style="font-size:11px; color:#94a3b8; margin-top:8px;">Terhubung secara otonom ke JARVIS AI Core v3.0.0.</p>
                </div>
            `;
        }
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
