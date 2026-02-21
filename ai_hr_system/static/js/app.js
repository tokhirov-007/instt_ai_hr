console.log("AI HR App v6.1 Loaded");
let sessionId = null;
let currentQuestionIndex = 0;
let questions = [];
let timerInterval = null;
let isSubmitting = false;

const translations = {
    en: {
        loading: "Analyzing your CV...",
        loading_final: "Finalizing interview...",
        final_title: "Thank You!",
        final_msg: "Your interview is complete. You will receive an email notification soon. Please check your Inbox and Spam folder.",
        btn_start: "Start Interview",
        lbl_upload: "Select CV (PDF/DOCX)",
        answer_ph: "Type your answer here...",
        lbl_name: "Full Name:",
        lbl_phone: "Phone Number:",
        lbl_email: "Email Address:",
        no_file: "File not selected",
        file_chosen: "Uploaded file: ",
        err_fill_fields: "Please fill in all fields (Name, Phone, Email)",
        err_bad_phone: "Please enter a valid Uzbekistan phone number (+998XXXXXXXXX)",
        err_no_cv: "Please upload your CV first",
        err_try_again: "An error occurred. Please try again.",
        err_step_failed: "Request failed"
    },
    ru: {
        loading: "Анализируем ваше CV...",
        loading_final: "Завершаем интервью...",
        final_title: "Спасибо!",
        final_msg: "Интервью успешно завершено. В ближайшее время вам придет уведомление на почту. Пожалуйста, проверьте папку «Входящие» и «Спам».",
        btn_start: "Начать интервью",
        lbl_upload: "Выберите CV (PDF/DOCX)",
        answer_ph: "Введите ваш ответ здесь...",
        lbl_name: "ФИО:",
        lbl_phone: "Номер телефона:",
        lbl_email: "Email адрес:",
        no_file: "Файл не выбран",
        file_chosen: "Загружен файл: ",
        err_fill_fields: "Пожалуйста, заполните все поля (ФИО, Телефон, Email)",
        err_bad_phone: "Введите корректный номер Узбекистана (+998XXXXXXXXX)",
        err_no_cv: "Сначала загрузите CV",
        err_try_again: "Произошла ошибка. Попробуйте еще раз.",
        err_step_failed: "Запрос завершился с ошибкой"
    },
    uz: {
        loading: "CV tahlil qilinmoqda...",
        loading_final: "Intervyu yakunlanmoqda...",
        final_title: "Rahmat!",
        final_msg: "Sizning intervyungiz muvaffaqiyatli yakunlandi. Tez orada elektron pochtangizga xabar keladi. Iltimos, «Inboks» va «Spam» papkalarini tekshiring.",
        btn_start: "Intervyuni boshlash",
        lbl_upload: "CV-ni tanlang (PDF/DOCX)",
        answer_ph: "Javobingizni bu yerga yozing...",
        lbl_name: "F.I.SH.:",
        lbl_phone: "Telefon raqami:",
        lbl_email: "Email manzili:",
        no_file: "Fayl tanlanmagan",
        file_chosen: "Fayl yuklandi: ",
        err_fill_fields: "Iltimos, barcha maydonlarni to'ldiring (Ism, Telefon, Email)",
        err_bad_phone: "To'g'ri O‘zbekiston raqamini kiriting (+998XXXXXXXXX)",
        err_no_cv: "Avval CV yuklang",
        err_try_again: "Xatolik yuz berdi. Qayta urinib ko'ring.",
        err_step_failed: "So'rovda xatolik yuz berdi"
    }
};

async function fetchJsonOrThrow(url, options, stepName) {
    const res = await fetch(url, options);
    let data = null;
    try {
        data = await res.json();
    } catch (_) {
        // ignore JSON parse errors; we’ll throw below if !ok
    }
    if (!res.ok) {
        const detail = (data && (data.detail || data.message)) ? (data.detail || data.message) : `${stepName} (${res.status})`;
        throw new Error(detail);
    }
    return data;
}

function updateUI() {
    const lang = document.getElementById('lang-select').value;
    try { localStorage.setItem('aihr_lang', lang); } catch (_) {}
    const t = translations[lang];
    document.getElementById('loading-text').innerText = t.loading;
    document.getElementById('final-title').innerText = t.final_title;
    document.getElementById('final-msg').innerText = t.final_msg;
    document.getElementById('btn-start').innerText = t.btn_start;
    document.getElementById('lbl-upload').innerText = t.lbl_upload;
    document.getElementById('answer-text').placeholder = t.answer_ph;
    document.getElementById('lbl-name').innerText = t.lbl_name;
    document.getElementById('lbl-phone').innerText = t.lbl_phone;
    document.getElementById('lbl-email').innerText = t.lbl_email;

    // Refresh filename display
    const fileInput = document.getElementById('cv-file');
    const display = document.getElementById('file-name-display');
    if (fileInput.files.length > 0) {
        display.innerText = t.file_chosen + fileInput.files[0].name;
    } else {
        display.innerText = t.no_file;
    }
}

function handleFileSelect() {
    const fileInput = document.getElementById('cv-file');
    const display = document.getElementById('file-name-display');
    const lang = document.getElementById('lang-select').value;
    const t = translations[lang];

    if (fileInput.files.length > 0) {
        display.innerText = t.file_chosen + fileInput.files[0].name;
    } else {
        display.innerText = t.no_file;
    }
}

function validateUzPhone(phone) {
    const re = /^\+998\d{9}$/;
    return re.test(phone);
}

async function startProcessing() {
    const fileInput = document.getElementById('cv-file');
    const lang = document.getElementById('lang-select').value;
    const t = translations[lang] || translations.en;
    const name = document.getElementById('candidate-name').value;
    const phone = document.getElementById('candidate-phone').value;
    const email = document.getElementById('candidate-email').value;

    if (!name || !phone || !email) {
        alert(t.err_fill_fields);
        return;
    }

    // Validate phone number format only when UZ is selected (project currently enforces +998)
    if (lang === 'uz' && !validateUzPhone(phone)) {
        alert(t.err_bad_phone);
        return;
    }

    if (fileInput.files.length === 0) {
        alert(t.err_no_cv);
        return;
    }

    // Disable start button while processing to avoid double-start
    const startBtn = document.getElementById('btn-start');
    if (startBtn) startBtn.disabled = true;

    showStep('step-loading');

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('name', name);
    formData.append('phone', phone);
    formData.append('email', email);

    try {
        // Step 1: Analyze CV
        const cvResult = await fetchJsonOrThrow('/analyze', { method: 'POST', body: formData }, 'analyze');

        // Step 2: Detect Level
        const levelResult = await fetchJsonOrThrow('/detect-level', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ candidate_name: name, cv_result: cvResult })
        }, 'detect-level');

        // Step 3: Interview Plan
        await fetchJsonOrThrow('/interview-plan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(levelResult)
        }, 'interview-plan');

        // Step 4: Generate Questions
        const questionSet = await fetchJsonOrThrow('/generate-questions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ level_result: levelResult, max_questions: 5, lang: lang })
        }, 'generate-questions');
        questions = questionSet.questions;

        // Step 5: Start Interview Session
        const session = await fetchJsonOrThrow('/start-interview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                candidate_id: Math.random().toString(36).substring(7),
                candidate_name: name || "Unknown",
                candidate_phone: phone || "",
                candidate_email: email || "",
                question_set: questionSet,
                lang: lang || "en",
                cv_path: (cvResult && cvResult.cv_path) ? cvResult.cv_path : ""
            })
        }, 'start-interview');
        sessionId = session.session_id;

        loadQuestion();
        showStep('step-interview');
    } catch (error) {
        console.error(error);
        alert(`${t.err_try_again}\n\n${t.err_step_failed}: ${error && error.message ? error.message : ''}`);
        showStep('step-upload');
    } finally {
        if (startBtn) startBtn.disabled = false;
    }
}

function loadQuestion() {
    if (currentQuestionIndex >= questions.length) {
        finishInterview();
        return;
    }

    const q = questions[currentQuestionIndex];
    document.getElementById('question-text').innerText = q.question;
    document.getElementById('answer-text').value = "";
    document.getElementById('progress-fill').style.width = `${((currentQuestionIndex) / questions.length) * 100}%`;

    startTimer(120); // 2 minutes per question
}

async function submitAnswer(isTimeout = false) {
    if (isSubmitting) return;
    const answer = document.getElementById('answer-text').value;
    // Prevent "freeze" on timeout: allow empty answers when time is up
    if (!isTimeout && (!answer || !answer.trim())) {
        alert("Please type an answer");
        return;
    }

    clearInterval(timerInterval);
    isSubmitting = true;

    try {
        // Disable submit button to prevent duplicate submissions
        const btn = document.getElementById('btn-submit');
        if (btn) btn.disabled = true;

        await fetch(`/submit-answer/${sessionId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(answer || "")
        });

        currentQuestionIndex++;
        loadQuestion();
    } catch (error) {
        console.error(error);
        alert("Failed to submit answer.");
    } finally {
        isSubmitting = false;
        const btn = document.getElementById('btn-submit');
        if (btn) btn.disabled = false;
    }
}

async function finishInterview() {
    showStep('step-loading');
    const lang = document.getElementById('lang-select').value;
    const t = translations[lang] || translations.en;
    document.getElementById('loading-text').innerText = t.loading_final;

    try {
        // Step 6 & 7: Integrity and Recommendation
        await fetch(`/analyze-integrity/${sessionId}`, { method: 'POST' });
        await fetch(`/generate-recommendation/${sessionId}`, { method: 'POST' });

        showStep('step-final');
    } catch (error) {
        console.error(error);
        showStep('step-final'); // Show final anyway
    }
}

function startTimer(seconds) {
    let timeLeft = seconds;
    const timerEl = document.getElementById('timer');

    timerInterval = setInterval(() => {
        const mins = Math.floor(timeLeft / 60) || 0;
        const secs = timeLeft % 60 || 0;
        timerEl.innerText = `Time Remaining: ${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;

        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            submitAnswer(true); // Auto-submit on timeout (allow empty)
        }
        timeLeft--;
    }, 1000);
}

function showStep(stepId) {
    document.querySelectorAll('.step-card').forEach(el => el.classList.add('hidden'));
    document.getElementById(stepId).classList.remove('hidden');
}

document.addEventListener('DOMContentLoaded', () => {
    // Auto-select UI language from browser if possible (RU/EN/UZ), without changing DB
    try {
        const saved = localStorage.getItem('aihr_lang');
        const browserLang = (navigator.language || '').toLowerCase();
        const select = document.getElementById('lang-select');
        if (select) {
            if (saved && ['ru', 'en', 'uz'].includes(saved)) select.value = saved;
            else if (browserLang.startsWith('ru')) select.value = 'ru';
            else if (browserLang.startsWith('uz')) select.value = 'uz';
            else select.value = 'en';
        }
    } catch (_) {}
    updateUI();
});