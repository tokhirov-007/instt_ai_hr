console.log("AI HR Admin v6.1 Loaded");
let adminLang = 'ru';

const adminTranslations = {
    en: {
        title: "Candidates",
        subtitle: "Hiring flow management",
        th_candidate: "Candidate",
        th_phone: "Phone",
        th_email: "Email",
        th_lang: "Lang",
        th_date: "Date",
        th_status: "Status",
        th_score: "Score",
        th_actions: "Actions",
        view_cv: "Open CV",
        status_invited: "Invited",
        status_rejected: "Rejected",
        status_review: "Under review",
        status_pending: "Pending",
        update_success: "Status updated successfully!",
        ai_loading: "Generating AI analysis…",
        ai_failed: "AI analysis failed. Please try again."
    },
    ru: {
        title: "Кандидаты",
        subtitle: "Управление потоком найма",
        th_candidate: "Кандидат",
        th_phone: "Телефон",
        th_email: "Email",
        th_lang: "Язык",
        th_date: "Дата",
        th_status: "Статус",
        th_score: "Баллы",
        th_actions: "Действия",
        view_cv: "Открыть CV",
        status_invited: "Приглашен",
        status_rejected: "Отклонен",
        status_review: "На проверке",
        status_pending: "Ожидание",
        update_success: "Статус успешно обновлен!",
        ai_loading: "Генерируем AI анализ…",
        ai_failed: "Не удалось выполнить AI анализ. Попробуйте снова."
    },
    uz: {
        title: "Nomzodlar",
        subtitle: "Yollash oqimini boshqarish",
        th_candidate: "Nomzod",
        th_phone: "Telefon",
        th_email: "Email",
        th_lang: "Til",
        th_date: "Sana",
        th_status: "Holat",
        th_score: "Ball",
        th_actions: "Harakatlar",
        view_cv: "CV-ni ochish",
        status_invited: "Taklif etildi",
        status_rejected: "Rad etildi",
        status_review: "Ko'rib chiqilmoqda",
        status_pending: "Kutilmoqda",
        update_success: "Holat muvaffaqiyatli yangilandi!",
        ai_loading: "AI tahlil yaratilmoqda…",
        ai_failed: "AI tahlil bajarilmadi. Qayta urinib ko'ring."
    }
};

function switchAdminLang(lang) {
    adminLang = lang;
    document.querySelectorAll('.lang-switcher button').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`btn-admin-${lang}`).classList.add('active');
    updateAdminUI();
}

function updateAdminUI() {
    const t = adminTranslations[adminLang];
    document.getElementById('admin-title').innerText = t.title;
    document.getElementById('admin-subtitle').innerText = t.subtitle;
    document.getElementById('th-candidate').innerText = t.th_candidate;
    document.getElementById('th-phone').innerText = t.th_phone;
    document.getElementById('th-email').innerText = t.th_email;
    document.getElementById('th-lang').innerText = t.th_lang;
    document.getElementById('th-date').innerText = t.th_date;
    document.getElementById('th-status').innerText = t.th_status;
    document.getElementById('th-score').innerText = t.th_score;
    document.getElementById('th-actions').innerText = t.th_actions;

    loadCandidates();
}

let allCandidates = [];

async function loadCandidates() {
    try {
        const response = await fetch('/admin/sessions');
        const data = await response.json();
        allCandidates = data; // Store for modal access
        renderCandidates(data);
    } catch (error) {
        console.error("Failed to load candidates:", error);
    }
}

function renderCandidates(candidates) {
    const body = document.getElementById('candidates-body');
    const t = adminTranslations[adminLang];
    body.innerHTML = '';

    candidates.forEach(c => {
        const tr = document.createElement('tr');

        let statusClass = 'status-review';
        let statusText = t.status_review;

        if (c.status_public === 'INVITED') {
            statusClass = 'status-invited';
            statusText = t.status_invited;
        } else if (c.status_public === 'REJECTED') {
            statusClass = 'status-rejected';
            statusText = t.status_rejected;
        }

        const cvLink = c.cv_path ? `<a href="/uploads/${c.cv_path.replace(/\\/g, '/').split('/').pop()}" target="_blank" class="admin-btn btn-cv">📄 CV</a>` : 'No CV';

        // Normalize date for display in admin panel (shift 5 hours forward relative to stored time)
        const startTime = c.start_time ? new Date(c.start_time) : null;
        const dateLocale = adminLang === 'uz' ? 'uz-UZ' : 'ru-RU';
        const dateOptions = {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            // We intentionally do not force a timeZone here, manual shift is below
        };
        // +5 часов вперёд относительно сохранённого времени
        const shiftedTime = startTime ? new Date(startTime.getTime() + 5 * 60 * 60 * 1000) : null;
        const formattedDate = shiftedTime ? shiftedTime.toLocaleString(dateLocale, dateOptions) : '';

        tr.innerHTML = `
            <td><strong>${c.candidate_name}</strong></td>
            <td>${c.candidate_phone}</td>
            <td>${c.candidate_email}</td>
            <td>${(c.candidate_lang || 'en').toUpperCase()}</td>
            <td>${formattedDate}</td>
            <td><span class="status-badge ${statusClass}">${statusText}</span></td>
            <td class="score-cell">${c.score !== null ? c.score : '-'}</td>
            <td>
                <div style="display:flex; gap:8px; align-items: center;">
                    ${cvLink}
                    <button onclick="showQA('${c.session_id}')" class="admin-btn btn-qa" title="View Q&A">💬 Q&A</button>
                    <button onclick="showAIReport('${c.session_id}')" class="admin-btn btn-ai-report" title="AI Report">📊 AI</button>
                    <button onclick="updateStatus('${c.session_id}', 'INVITED')" class="admin-btn btn-invite" title="Invite">✅</button>
                    <button onclick="updateStatus('${c.session_id}', 'REJECTED')" class="admin-btn btn-reject" title="Reject">❌</button>
                </div>
            </td>
        `;
        body.appendChild(tr);
    });
}

function showQA(sessionId) {
    const candidate = allCandidates.find(c => c.session_id === sessionId);
    if (!candidate) return;

    // Reset modal header for Q&A
    const modalHeader = document.querySelector('#qa-modal .modal-header h3');
    if (modalHeader) {
        modalHeader.textContent = 'История ответов / Interview Q&A';
    }

    const content = document.getElementById('qa-content');
    content.innerHTML = '';

    if (!candidate.questions || candidate.questions.length === 0) {
        content.innerHTML = '<p style="text-align:center; padding: 20px; opacity: 0.6;">No questions found for this session.</p>';
    } else {
        candidate.questions.forEach((q, idx) => {
            const ansObj = (candidate.answers && candidate.answers[idx]) ? candidate.answers[idx] : null;
            const answerText = ansObj ? ansObj.answer_text : '<i>No answer provided</i>';

            let badges = '';
            if (ansObj) {
                // Check AI Score
                if (ansObj.ai_score && ansObj.ai_score > 0.5) {
                    badges += `<span class="ai-badge" title="${ansObj.ai_explanation || 'AI Pattern Detected'}">🤖 AI (${Math.round(ansObj.ai_score * 100)}%)</span>`;
                }
                // Check Speed Trap flag in explanation
                if (ansObj.ai_explanation && ansObj.ai_explanation.includes('typing_speed')) {
                    badges += `<span class="fast-type-badge" title="Typed impossibly fast">⚡ Fast Type</span>`;
                }
            }

            const qaItem = document.createElement('div');
            qaItem.className = 'qa-item';
            qaItem.innerHTML = `
                <div class="qa-q"><strong>Q${idx + 1}:</strong> ${q.question}</div>
                <div class="qa-a"><strong>A:</strong> ${answerText} ${badges}</div>
            `;
            content.appendChild(qaItem);
        });
    }

    document.getElementById('qa-modal').classList.remove('hidden');
}

function showAIReport(sessionId) {
    const candidate = allCandidates.find(c => c.session_id === sessionId);
    if (!candidate) return;

    const content = document.getElementById('qa-content');
    content.innerHTML = '';

    // Determine UI language for admin (RU/UZ) – we always show report in admin's language
    const uiLang = (adminLang || 'ru').toLowerCase();
    const isUz = uiLang === 'uz';
    const isRu = uiLang === 'ru';
    const isEn = !isUz && !isRu;

    // Decision translations
    const decisionsRU = {
        "Strong Hire": "Настоятельно рекомендую",
        "Hire": "Нанять",
        "Review": "На проверку",
        "Reject": "Отказать"
    };
    const decisionsUZ = {
        "Strong Hire": "Juda tavsiya etiladi",
        "Hire": "Ishga olish",
        "Review": "Ko'rib chiqish",
        "Reject": "Rad etish"
    };
    const decisionsEN = {
        "Strong Hire": "Strong Hire",
        "Hire": "Hire",
        "Review": "Review",
        "Reject": "Reject"
    };

    // Flags translations
    const flagsMap = {
        // AI Detector Flags
        "superhuman_typing_speed": ["Нереальная скорость печати", "G'ayritabiiy yozish tezligi"],
        "fast_typing_suspicion": ["Подозрительно быстрая печать", "Shubhali tez yozish"],
        "perfect_numbered_list": ["Идеальные списки (AI)", "Mukammal ro'yxatlar (AI)"],
        "perfect_bullet_points": ["Идеальные пункты (AI)", "Mukammal punktlar (AI)"],
        "uniform_sentence_lengths": ["Монотонные предложения", "Bir xil gap uzunligi"],
        "high_marker_density": ["Много AI-фраз", "Ko'p AI iboralari"],
        "empty_text": ["Пустой ответ", "Bo'sh javob"],
        "ai_star_formatting": ["Форматирование через звездочки (*)", "Yulduzchali formatlash (*)"],
        "colon_definitions_pattern": ["Стиль 'Термин: Определение'", "'Termin: Ta'rif' uslubi"],
        "high_repetition_rate": ["Высокая повторяемость слов", "So'zlar qaytarilishi yuqori"],
        "robot_transitions": ["Роботизированные связки", "Robotga xos bog'lamlar"],

        // Structure Analyzer Flags
        "contains_code": ["Содержит код", "Kod mavjud"],
        "logical_steps_detected": ["Логические шаги обнаружены", "Mantiqiy qadamlar aniqlandi"],
        "lack_of_explaining_steps": ["Отсутствие объяснений", "Tushuntirishlar yo'q"],
        "comprehensive_answer": ["Полный ответ", "To'liq javob"],
        "too_short_answer": ["Слишком короткий ответ", "Juda qisqa javob"],
        "raw_code_no_explanation": ["Код без объяснений", "Tushuntirishsiz kod"],
        "long_text_no_code": ["Длинный текст без кода", "Kodsiz uzun matn"],

        // Time Behavior Flags
        "too_fast_for_hard_question": ["Слишком быстро для сложного вопроса", "Qiyin savol uchun juda tez"],
        "too_fast_for_medium_question": ["Слишком быстро для среднего вопроса", "O'rta savol uchun juda tez"],
        "suspiciously_short_time": ["Подозрительно короткое время", "Shubhali qisqa vaqt"],
        "impossible_typing_speed": ["Невозможная скорость печати", "Imkonsiz yozish tezligi"],
        "extremely_high_typing_speed": ["Экстремально высокая скорость", "Haddan tashqari yuqori tezlik"],

        // Plagiarism Checker Flags
        "known_template_detected": ["Обнаружен известный шаблон", "Ma'lum shablon aniqlandi"],
        "possible_templated_phrasing": ["Возможно шаблонные фразы", "Shablon iboralar bo'lishi mumkin"],
        "high_self_similarity": ["Высокое самоповторение", "Yuqori o'z-o'zini takrorlash"],

        // Final Analyzer Global Flags
        "HIGH_RISK_OF_CHEATING": ["ВЫСОКИЙ РИСК ОБМАНА", "ALDASH XAVFI YUQORI"],
        "SYSTEMIC_AI_USAGE_LIKELY": ["СИСТЕМНОЕ ИСПОЛЬЗОВАНИЕ AI", "Tizimli AI foydalanish"]
    };

    // Extract data
    const decision = candidate.decision || "N/A";
    const hrComment = candidate.hr_comment || "No comment available";

    // Translate decision
    const translatedDecision = isUz
        ? (decisionsUZ[decision] || decision)
        : (isRu ? (decisionsRU[decision] || decision) : (decisionsEN[decision] || decision));

    // Split comment (RU ||| UZ). Use admin UI language (RU/UZ).
    const commentParts = hrComment.split("|||");
    const displayComment = isUz
        ? (commentParts[1] ? commentParts[1].trim() : commentParts[0].trim())
        : commentParts[0].trim();

    // If analysis is not present yet, trigger backend generation then reload and render
    const needsGeneration = !candidate.decision || candidate.score === null || !candidate.hr_comment;
    if (needsGeneration) {
        const t = adminTranslations[adminLang] || adminTranslations.en;
        content.innerHTML = `<div style="padding:20px; opacity:0.85;">${t.ai_loading}</div>`;

        async function runGeneration() {
            try {
                const res1 = await fetch(`/analyze-integrity/${sessionId}`, { method: 'POST' });
                if (!res1.ok) {
                    const errTxt = await res1.text();
                    throw new Error(`Step 1 (Integrity) failed: ${res1.status} ${errTxt}`);
                }

                const res2 = await fetch(`/generate-recommendation/${sessionId}`, { method: 'POST' });
                if (!res2.ok) {
                    const errTxt = await res2.text();
                    throw new Error(`Step 2 (Recommendation) failed: ${res2.status} ${errTxt}`);
                }

                await loadCandidates();
                showAIReport(sessionId);
            } catch (err) {
                console.error("AI Generation Error:", err);
                content.innerHTML = `<div style="padding:20px; color:#ff6b6b;">${t.ai_failed}<br><small>${err.message}</small></div>`;
                alert(`AI Analysis Error: ${err.message}`);
            }
        }

        runGeneration();
        document.getElementById('qa-modal').classList.remove('hidden');
        return;
    }

    // Parse flags (can be array, JSON string, or comma-separated string depending on DB/serializer)
    let flags = [];
    const rawFlags = candidate.flags;
    if (Array.isArray(rawFlags)) {
        flags = rawFlags;
    } else if (typeof rawFlags === 'string') {
        const trimmed = rawFlags.trim();
        if (trimmed.startsWith('[')) {
            try {
                flags = JSON.parse(trimmed) || [];
            } catch {
                flags = [];
            }
        } else if (trimmed.length > 0) {
            flags = trimmed.split(',').map(f => f.trim()).filter(f => f);
        }
    }

    // Translate flags
    const translatedFlags = flags.slice(0, 5).map(flag => {
        if (flagsMap[flag]) {
            return isUz ? flagsMap[flag][1] : flagsMap[flag][0];
        }
        return flag; // Return raw if no translation
    });

    // Build HTML
    const reportHTML = `
        <div style="padding: 20px;">
            <h3 style="margin-top: 0; color: #2c3e50;">${isUz ? '📊 AI Tahlil' : (isRu ? '📊 AI Анализ' : '📊 AI Report')}</h3>
            
            <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <strong style="color: #3498db;">${isUz ? '📊 Qaror:' : (isRu ? '📊 Решение:' : '📊 Decision:')}</strong>
                <p style="margin: 8px 0; font-size: 1.1em;">${translatedDecision}</p>
            </div>

            <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <strong style="color: #9b59b6;">${isUz ? '💬 Izoh:' : (isRu ? '💬 Комментарий:' : '💬 Comment:')}</strong>
                <p style="margin: 8px 0;">${displayComment}</p>
            </div>

            <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px;">
                <strong style="color: #e74c3c;">${isUz ? '🚨 Sabablar:' : (isRu ? '🚨 Причины:' : '🚨 Reasons:')}</strong>
                <ul style="margin: 8px 0; padding-left: 20px;">
                    ${translatedFlags.length > 0
            ? translatedFlags.map(f => `<li>${f}</li>`).join('')
            : `<li style="opacity: 0.6;">${isUz ? 'Izohlar yo\'q' : (isRu ? 'Нет замечаний' : 'No flags')}</li>`
        }
                </ul>
            </div>
        </div>
    `;

    content.innerHTML = reportHTML;

    // Update modal header for AI Report
    const modalHeader = document.querySelector('#qa-modal .modal-header h3');
    if (modalHeader) {
        modalHeader.textContent = isUz ? '📊 AI Tahlil' : (isRu ? '📊 AI Анализ' : '📊 AI Report');
    }

    document.getElementById('qa-modal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('qa-modal').classList.add('hidden');
}

async function updateStatus(sessionId, status) {
    const t = adminTranslations[adminLang];
    try {
        const res = await fetch(`/update-session-status/${sessionId}?internal_status=${status}&public_status=${status}`, {
            method: 'POST'
        });
        if (!res.ok) {
            const errTxt = await res.text();
            throw new Error(`${res.status}: ${errTxt}`);
        }
        alert(t.update_success);
        loadCandidates();
    } catch (error) {
        console.error("Failed to update status:", error);
        alert(`Failed to update status: ${error.message}`);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    updateAdminUI();
});
