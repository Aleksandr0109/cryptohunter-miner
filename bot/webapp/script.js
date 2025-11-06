// === script.js — ПОЛНАЯ ВЕРСИЯ: ОПЛАТА, МУЛЬТИЯЗЫЧНОСТЬ, НАЧИСЛЕНИЯ, ВСЁ РАБОТАЕТ ===
console.log("CryptoHunter Miner WebApp загружен");
const tg = window.Telegram?.WebApp;

// === КОНФИГУРАЦИЯ ===
const CONFIG = {
    API_BASE: window.location.origin,
    MIN_INVEST: 1,
    MIN_WITHDRAW: 1,
    DAILY_RATE: 0.25,
    BONUS_PERCENT: 5,
    REFERRAL_LEVEL1: 5,
    REFERRAL_LEVEL2: 2,
    BOT_USERNAME: '@CryptoHunterTonBot'
};

// === ПЕРЕВОДЫ ===
const translations = {
    ru: {
        "invest": "Инвестировать",
        "withdraw": "Вывод",
        "your_balance": "ВАШ БАЛАНС",
        "invested": "Инвестировано",
        "earned": "Заработано",
        "speed": "Скорость",
        "detailed_stats": "Детальная статистика",
        "referral_program": "Реферальная программа",
        "back": "Назад",
        "investments": "ИНВЕСТИЦИИ",
        "amount": "Сумма:",
        "day": "День:",
        "week": "Неделя:",
        "month": "Месяц:",
        "free_mining": "БЕСПЛАТНЫЙ МАЙНИНГ",
        "ton_per_days": "1 TON за:",
        "accumulated": "Накоплено:",
        "currently_earning": "СЕЙЧАС НАЧИСЛЯЕТСЯ",
        "per_day": "В день:",
        "per_hour": "В час:",
        "not_ready": "Не готово",
        "min_withdraw": "Минимум: 1 TON (1.00 TON осталось)",
        "community": "СООБЩЕСТВО",
        "total_subscribers": "Всего подписчиков:",
        "active_today": "Активных сегодня:",
        "top_investors": "ТОП 10 ИНВЕСТОРОВ",
        "withdraw_requests": "ЗАЯВКИ НА ВЫВОД",
        "wallet": "Кошелек",
        "amount_ton": "Сумма TON",
        "status": "Статус",
        "direct_referrals": "прямых рефералов",
        "level_2": "2-й уровень",
        "earned_ton": "Заработано TON",
        "your_referral_link": "Ваша реферальная ссылка:",
        "copy_link": "Скопировать ссылку",
        "investing": "Инвестирование",
        "investment_amount": "Сумма инвестиции (TON):",
        "generate_qr": "Сгенерировать QR для оплаты",
        "scan_qr": "Отсканируйте QR-код для оплаты:",
        "ton_address": "Адрес TON:",
        "comment": "Комментарий:",
        "copy_address": "Скопировать адрес",
        "profit_calculator": "Калькулятор доходности",
        "amount_for_calc": "Сумма для расчета:",
        "calculate_profit": "Рассчитать доходность",
        "investment_bonus": "Бонус за инвестицию:",
        "year": "Год:",
        "withdraw_funds": "Вывод средств",
        "available_for_withdraw": "Доступно для вывода:",
        "ton_wallet_address": "Адрес TON кошелька:",
        "withdraw_amount": "Сумма вывода (TON):",
        "min_ton": "Минимум 1 TON",
        "enter_amount": "Введите сумму",
        "wallet_placeholder": "Начинается с kQ, UQ или EQ",
        "server_sleeping": "Сервер спит...",
        "calc_local": "Расчет выполнен локально",
        "qr_ready": "QR-код готов для сканирования!",
        "address_copied": "Адрес скопирован в буфер обмена!",
        "payment_url_copied": "Ссылка на оплату скопирована!",
        "copy_error": "Не удалось скопировать",
        "no_address": "Нет адреса для копирования",
        "enter_correct_amount": "Введите корректную сумму в TON",
        "min_invest_error": "Минимальная сумма инвестиции 1 TON",
        "enter_wallet": "Введите адрес TON кошелька",
        "wallet_format_error": "Адрес должен начинаться с kQ, UQ или EQ",
        "min_withdraw_error": "Минимум 1 TON",
        "insufficient_funds": "Недостаточно средств",
        "withdraw_success": "Запрос на вывод успешно отправлен!",
        "payment_confirmed": "Платеж подтвержден! Бонус:",
        "payment_pending": "Платеж еще не подтвержден",
        "no_pending_payments": "Нет ожидающих платежей",
        "referral_copied": "Реферальная ссылка скопирована!",
        "connection_error": "Ошибка соединения",
        "deposit_created": "Депозит создан!",
        "payment_checking": "Проверяем платеж...",
        "payment_expired": "Время оплаты истекло",
        "payment_error": "Ошибка проверки платежа",
        "refresh": "Обновить",
        "accrued": "Начислено +",
        "check_payment": "Проверить оплату",
        "payment_checking_auto": "Автопроверка каждые 5 сек...",
        "deposit_creation_failed": "Не удалось создать депозит"
    },
    en: {
        "invest": "Invest",
        "withdraw": "Withdraw",
        "your_balance": "YOUR BALANCE",
        "invested": "Invested",
        "earned": "Earned",
        "speed": "Speed",
        "detailed_stats": "Detailed Statistics",
        "referral_program": "Referral Program",
        "back": "Back",
        "investments": "INVESTMENTS",
        "amount": "Amount:",
        "day": "Day:",
        "week": "Week:",
        "month": "Month:",
        "free_mining": "FREE MINING",
        "ton_per_days": "1 TON in:",
        "accumulated": "Accumulated:",
        "currently_earning": "CURRENTLY EARNING",
        "per_day": "Per day:",
        "per_hour": "Per hour:",
        "not_ready": "Not ready",
        "min_withdraw": "Minimum: 1 TON (1.00 TON left)",
        "community": "COMMUNITY",
        "total_subscribers": "Total subscribers:",
        "active_today": "Active today:",
        "top_investors": "TOP 10 INVESTORS",
        "withdraw_requests": "WITHDRAWAL REQUESTS",
        "wallet": "Wallet",
        "amount_ton": "Amount TON",
        "status": "Status",
        "direct_referrals": "direct referrals",
        "level_2": "Level 2",
        "earned_ton": "Earned TON",
        "your_referral_link": "Your referral link:",
        "copy_link": "Copy link",
        "investing": "Investing",
        "investment_amount": "Investment amount (TON):",
        "generate_qr": "Generate QR for payment",
        "scan_qr": "Scan QR code for payment:",
        "ton_address": "TON address:",
        "comment": "Comment:",
        "copy_address": "Copy address",
        "profit_calculator": "Profit Calculator",
        "amount_for_calc": "Amount for calculation:",
        "calculate_profit": "Calculate profit",
        "investment_bonus": "Investment bonus:",
        "year": "Year:",
        "withdraw_funds": "Withdraw Funds",
        "available_for_withdraw": "Available for withdrawal:",
        "ton_wallet_address": "TON wallet address:",
        "withdraw_amount": "Withdrawal amount (TON):",
        "min_ton": "Minimum 1 TON",
        "enter_amount": "Enter amount",
        "wallet_placeholder": "Starts with kQ, UQ or EQ",
        "server_sleeping": "Server is sleeping...",
        "calc_local": "Calculation performed locally",
        "qr_ready": "QR code ready for scanning!",
        "address_copied": "Address copied to clipboard!",
        "payment_url_copied": "Payment link copied!",
        "copy_error": "Failed to copy",
        "no_address": "No address to copy",
        "enter_correct_amount": "Enter correct amount in TON",
        "min_invest_error": "Minimum investment amount 1 TON",
        "enter_wallet": "Enter TON wallet address",
        "wallet_format_error": "Address must start with kQ, UQ or EQ",
        "min_withdraw_error": "Minimum withdrawal amount 1 TON",
        "insufficient_funds": "Insufficient funds for withdrawal",
        "withdraw_success": "Withdrawal request successfully sent!",
        "payment_confirmed": "Payment confirmed! Bonus:",
        "payment_pending": "Payment not confirmed yet",
        "no_pending_payments": "No pending payments",
        "referral_copied": "Referral link copied!",
        "connection_error": "Connection error",
        "deposit_created": "Deposit created!",
        "payment_checking": "Checking payment...",
        "payment_expired": "Payment time expired",
        "payment_error": "Payment check error",
        "refresh": "Refresh",
        "accrued": "Accrued +",
        "check_payment": "Check payment",
        "payment_checking_auto": "Auto-check every 5 sec...",
        "deposit_creation_failed": "Failed to create deposit"
    }
};

// === ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ===
let currentLanguage = 'ru';
let currentUserData = null;
let currentDepositId = null;
let paymentCheckInterval = null;
let hourlyAccrualInterval = null;

// === ПОЛУЧИТЬ initData ===
function getInitData() {
    return tg?.initData || '';
}

// === СМЕНА ЯЗЫКА ===
function changeLanguage(lang) {
    if (currentLanguage === lang) return;
    currentLanguage = lang;
    document.querySelectorAll('.lang-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`lang-${lang}`).classList.add('active');
    updateAllTexts();
    localStorage.setItem('preferredLanguage', lang);
}

// === ОБНОВЛЕНИЕ ТЕКСТОВ ===
function updateAllTexts() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[currentLanguage][key]) el.textContent = translations[currentLanguage][key];
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (translations[currentLanguage][key]) el.placeholder = translations[currentLanguage][key];
    });
}

// === ПОКАЗАТЬ СЕКЦИЮ ===
function showSection(id) {
    document.querySelectorAll('.section').forEach(s => {
        s.style.display = 'none';
        s.classList.remove('active');
    });
    const target = document.getElementById(id);
    if (target) {
        target.style.display = 'block';
        target.classList.add('active');
    }
    if (id === 'stats') loadUserData();
    if (id === 'dashboard') loadDashboardData();
    if (id === 'referral') loadReferralData();
    if (id === 'withdraw') updateWithdrawInfo();
    if (id === 'invest') stopPaymentChecking();
}

// === УВЕДОМЛЕНИЯ ===
function showNotification(msgKey, type = 'info', extra = '') {
    const n = document.getElementById('notification');
    if (!n) return;
    const message = (translations[currentLanguage][msgKey] || msgKey) + (extra ? ` ${extra}` : '');
    n.textContent = message;
    n.className = 'notification';
    n.style.background = type === 'error' ? '#ff4444' : type === 'success' ? '#00ff88' : '#00ccff';
    n.classList.add('show');
    setTimeout(() => n.classList.remove('show'), 3000);
}

// === АНИМАЦИЯ ЧИСЕЛ ===
function animateValue(id, end, duration = 600) {
    const el = document.getElementById(id);
    if (!el) return;
    const start = parseFloat(el.textContent) || 0;
    const range = end - start;
    const startTime = performance.now();
    function step(time) {
        const elapsed = time - startTime;
        const progress = Math.min(elapsed / duration, 1);
        el.textContent = (start + range * progress).toFixed(4);
        if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
}

// === ЗАГРУЗКА ДАННЫХ ПОЛЬЗОВАТЕЛЯ ===
async function loadUserData() {
    try {
        const res = await fetch(`${CONFIG.API_BASE}/api/user`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Telegram-WebApp-Init-Data': getInitData()
            }
        });
        if (res.ok) {
            const data = await res.json();
            currentUserData = data;
            animateValue('balance', parseFloat(data.balance));
            document.getElementById('invested').textContent = Number(data.invested).toFixed(2);
            document.getElementById('earned').textContent = Number(data.earned).toFixed(4);
            document.getElementById('speed').textContent = data.speed;
            updateWithdrawInfo();
            startHourlyAccrual();
        }
    } catch (e) {
        showNotification('server_sleeping', 'error');
    }
}

// === АВТО-НАЧИСЛЕНИЯ ===
function startHourlyAccrual() {
    if (hourlyAccrualInterval) clearInterval(hourlyAccrualInterval);
    hourlyAccrualInterval = setInterval(() => {
        if (!currentUserData) return;
        const invested = parseFloat(currentUserData.invested) || 0;
        const hourly = (invested * CONFIG.DAILY_RATE) / 24 / 100;
        const newBal = (parseFloat(currentUserData.balance) || 0) + hourly;
        currentUserData.balance = newBal.toFixed(4);
        currentUserData.earned = (parseFloat(currentUserData.earned) || 0) + hourly;
        animateValue('balance', newBal);
        document.getElementById('earned').textContent = currentUserData.earned.toFixed(4);
        showNotification('accrued', 'success', `+${hourly.toFixed(4)} TON`);
        if (document.getElementById('dashboard').classList.contains('active')) loadDashboardData();
    }, 60000); // 1 минута
}

// === ДАШБОРД ===
async function loadDashboardData() {
    try {
        const res = await fetch(`${CONFIG.API_BASE}/api/dashboard`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Telegram-WebApp-Init-Data': getInitData()
            }
        });
        if (res.ok) {
            const d = await res.json();
            document.getElementById('dash-invested').textContent = `${d.invested.toFixed(2)} TON`;
            document.getElementById('dash-daily-inv').textContent = d.daily_investment.toFixed(3) + ' TON';
            document.getElementById('dash-weekly-inv').textContent = (d.daily_investment * 7).toFixed(3) + ' TON';
            document.getElementById('dash-monthly-inv').textContent = (d.daily_investment * 30).toFixed(2) + ' TON';
            document.getElementById('dash-speed').textContent = `${d.speed.toFixed(0)}%`;
            document.getElementById('dash-daily-free').textContent = d.daily_free.toFixed(4) + ' TON';
            document.getElementById('dash-days-per-ton').textContent = d.days_per_ton.toFixed(1) + ' ' + (currentLanguage === 'ru' ? 'дней' : 'days');
            document.getElementById('dash-accumulated').textContent = d.balance.toFixed(2) + ' TON';
            document.getElementById('dash-total-daily').textContent = d.total_daily.toFixed(4) + ' TON';
            document.getElementById('dash-hourly').textContent = d.hourly.toFixed(4) + ' TON';
            document.getElementById('dash-withdraw-status').innerHTML = d.can_withdraw
                ? (currentLanguage === 'ru' ? "Готово" : "Ready")
                : (currentLanguage === 'ru' ? "Не готово" : "Not ready");
            const rem = Math.max(0, CONFIG.MIN_WITHDRAW - d.balance);
            document.getElementById('dash-min-withdraw').textContent = currentLanguage === 'ru'
                ? `Минимум: ${CONFIG.MIN_WITHDRAW} TON (${rem.toFixed(2)} TON осталось)`
                : `Minimum: ${CONFIG.MIN_WITHDRAW} TON (${rem.toFixed(2)} TON left)`;
        }
    } catch (e) {
        console.error(e);
    }
}

// === РЕФЕРАЛЫ ===
async function loadReferralData() {
    try {
        const res = await fetch(`${CONFIG.API_BASE}/api/referral`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Telegram-WebApp-Init-Data': getInitData()
            }
        });
        if (res.ok) {
            const d = await res.json();
            document.getElementById('ref-direct').textContent = d.direct_count;
            document.getElementById('ref-level2').textContent = d.level2_count;
            document.getElementById('ref-income').textContent = Number(d.income).toFixed(2);
            const link = d.link || `https://t.me/${CONFIG.BOT_USERNAME}?start=ref_${currentUserData?.user_id || 'unknown'}`;
            document.getElementById('ref-link').textContent = link;
        }
    } catch (e) {
        console.error(e);
    }
}

// === КАЛЬКУЛЯТОР ===
window.calculate = async function() {
    const amount = parseFloat(document.getElementById('calc-amount').value);
    if (!amount || amount < CONFIG.MIN_INVEST) return showNotification('min_invest_error', 'error');
    try {
        const res = await fetch(`${CONFIG.API_BASE}/api/calc`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount })
        });
        if (res.ok) {
            const data = await res.json();
            updateCalculatorResults(amount, data);
        } else {
            calculateLocally(amount);
        }
    } catch (e) {
        calculateLocally(amount);
    }
};

function calculateLocally(amount) {
    const daily = amount * (CONFIG.DAILY_RATE / 100);
    const bonus = amount * (CONFIG.BONUS_PERCENT / 100);
    const el = document.getElementById('calc-result');
    if (el) {
        el.innerHTML = `
            <div class="calc-result-item"><span>${translations[currentLanguage]['day']}</span><b>${daily.toFixed(4)} TON</b></div>
            <div class="calc-result-item"><span>${translations[currentLanguage]['week']}</span><b>${(daily * 7).toFixed(4)} TON</b></div>
            <div class="calc-result-item"><span>${translations[currentLanguage]['month']}</span><b>${(daily * 30).toFixed(4)} TON</b></div>
            <div class="calc-result-item"><span>${translations[currentLanguage]['year']}</span><b>${(daily * 365).toFixed(4)} TON</b></div>
            <div class="calc-result-item"><span>${translations[currentLanguage]['investment_bonus']}</span><b>+${bonus.toFixed(2)} TON</b></div>
        `;
    }
    showNotification('calc_local', 'info');
}

function updateCalculatorResults(amount, data) {
    const el = document.getElementById('calc-result');
    if (el) {
        el.innerHTML = `
            <div class="calc-result-item"><span>${translations[currentLanguage]['day']}</span><b>${data.daily.toFixed(4)} TON</b></div>
            <div class="calc-result-item"><span>${translations[currentLanguage]['week']}</span><b>${(data.daily * 7).toFixed(4)} TON</b></div>
            <div class="calc-result-item"><span>${translations[currentLanguage]['month']}</span><b>${data.monthly.toFixed(4)} TON</b></div>
            <div class="calc-result-item"><span>${translations[currentLanguage]['year']}</span><b>${data.yearly.toFixed(4)} TON</b></div>
            <div class="calc-result-item"><span>${translations[currentLanguage]['investment_bonus']}</span><b>+${(amount * CONFIG.BONUS_PERCENT / 100).toFixed(2)} TON</b></div>
        `;
    }
}

// === СОЗДАНИЕ ДЕПОЗИТА ===
window.createDeposit = async function() {
    const amountInput = document.getElementById("invest-amount");
    const amount = amountInput?.value?.trim();
    if (!amount || isNaN(amount) || parseFloat(amount) <= 0) return showNotification("enter_correct_amount", "error");
    const amountNum = parseFloat(amount);
    if (amountNum < CONFIG.MIN_INVEST) return showNotification("min_invest_error", "error");

    try {
        showNotification("payment_checking", "info");
        const res = await fetch("/api/deposit", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Telegram-WebApp-Init-Data": getInitData()
            },
            body: JSON.stringify({ amount: amountNum }),
        });
        if (!res.ok) throw new Error("Сервер не отвечает");
        const data = await res.json();

        if (data.success) {
            currentDepositId = data.deposit_id;

            const qrSection = document.getElementById("qr-section");
            const qrImg = document.getElementById("qr-img");
            const qrAddress = document.getElementById("qr-address");
            const qrComment = document.getElementById("qr-comment");
            const paymentUrl = document.getElementById("payment-url");
            const checkBtn = document.getElementById("checkPaymentBtn");
            const copyAddressBtn = document.getElementById("copyAddressBtn");
            const copyPaymentUrlBtn = document.getElementById("copyPaymentUrlBtn");

            if (qrImg) qrImg.src = data.qr_code || "";
            if (qrAddress) qrAddress.textContent = data.address || "—";
            if (qrComment) qrComment.textContent = data.comment || "—";
            if (paymentUrl) {
                paymentUrl.href = data.payment_url || "#";
                paymentUrl.textContent = data.payment_url || "Открыть в кошельке";
            }

            if (copyAddressBtn) copyAddressBtn.onclick = () => copyToClipboard(data.address, "address_copied");
            if (copyPaymentUrlBtn) copyPaymentUrlBtn.onclick = () => copyToClipboard(data.payment_url, "payment_url_copied");

            if (checkBtn) {
                checkBtn.style.display = "block";
                checkBtn.innerHTML = `<span data-i18n="check_payment">${translations[currentLanguage].check_payment}</span>`;
                checkBtn.onclick = checkPaymentManually;
            }

            if (qrSection) {
                qrSection.style.display = "block";
                qrSection.scrollIntoView({ behavior: "smooth" });
            }

            showNotification("deposit_created", "success");
            showNotification("payment_checking_auto", "info");
            startPaymentChecking(currentDepositId);

        } else {
            showNotification("deposit_creation_failed", "error");
        }
    } catch (err) {
        console.error(err);
        showNotification("connection_error", "error");
    }
};

// === КОПИРОВАНИЕ ===
function copyToClipboard(text, successKey) {
    if (!text) return showNotification("no_address", "error");
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => showNotification(successKey, "success")).catch(() => fallbackCopy(text, successKey));
    } else {
        fallbackCopy(text, successKey);
    }
}

function fallbackCopy(text, successKey) {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed"; ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.focus(); ta.select();
    try { document.execCommand("copy"); showNotification(successKey, "success"); }
    catch { showNotification("copy_error", "error"); }
    document.body.removeChild(ta);
}

// === ПРОВЕРКА ПЛАТЕЖА ===
function checkPaymentManually() {
    if (!currentDepositId) return;
    showNotification("payment_checking", "info");
    fetch("/api/check-payment", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Telegram-WebApp-Init-Data": getInitData() },
        body: JSON.stringify({ deposit_id: currentDepositId })
    })
    .then(r => r.json())
    .then(res => {
        if (res.status === 'completed') {
            stopPaymentChecking();
            showNotification(`payment_confirmed ${res.bonus?.toFixed(4) || 0} TON`, 'success');
            loadUserData(); loadDashboardData();
            setTimeout(() => {
                const qr = document.getElementById("qr-section"); if (qr) qr.style.display = 'none';
                const btn = document.getElementById("checkPaymentBtn"); if (btn) btn.style.display = 'none';
            }, 3000);
        } else {
            showNotification('payment_pending', 'info');
        }
    })
    .catch(() => showNotification('payment_error', 'error'));
}

function startPaymentChecking(id) {
    stopPaymentChecking();
    paymentCheckInterval = setInterval(async () => {
        try {
            const res = await fetch("/api/check-payment", {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-Telegram-WebApp-Init-Data": getInitData() },
                body: JSON.stringify({ deposit_id: id })
            });
            if (res.ok) {
                const d = await res.json();
                if (d.status === 'completed') {
                    stopPaymentChecking();
                    showNotification(`payment_confirmed ${d.bonus?.toFixed(4) || 0} TON`, 'success');
                    loadUserData(); loadDashboardData();
                    setTimeout(() => {
                        const qr = document.getElementById("qr-section"); if (qr) qr.style.display = 'none';
                        const btn = document.getElementById("checkPaymentBtn"); if (btn) btn.style.display = 'none';
                    }, 3000);
                } else if (d.status === 'expired') {
                    stopPaymentChecking();
                    showNotification('payment_expired', 'error');
                }
            }
        } catch (e) { console.error(e); }
    }, 5000);
    setTimeout(stopPaymentChecking, 25 * 60 * 1000);
}

function stopPaymentChecking() {
    if (paymentCheckInterval) clearInterval(paymentCheckInterval);
    paymentCheckInterval = null;
}

// === ВЫВОД ===
window.withdraw = async function() {
    const addr = document.getElementById('withdraw-address').value.trim();
    const amount = parseFloat(document.getElementById('withdraw-amount').value);
    const available = parseFloat(document.getElementById('withdraw-available').textContent);

    if (!addr) return showNotification('enter_wallet', 'error');
    if (!addr.match(/^[kQU][A-Za-z0-9]{46}$/)) return showNotification('wallet_format_error', 'error');
    if (!amount || amount < CONFIG.MIN_WITHDRAW) return showNotification('min_withdraw_error', 'error');
    if (amount > available) return showNotification('insufficient_funds', 'error');

    try {
        const res = await fetch(`${CONFIG.API_BASE}/api/withdraw`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-Telegram-WebApp-Init-Data': getInitData() },
            body: JSON.stringify({ address: addr, amount })
        });
        const result = await res.json();
        const statusEl = document.getElementById('withdraw-status');
        if (res.ok) {
            if (statusEl) { statusEl.textContent = result.message || (currentLanguage === 'ru' ? 'Запрос отправлен' : 'Request sent'); statusEl.className = 'status-message status-success'; }
            showNotification('withdraw_success', 'success');
            addWithdrawRequest(addr, amount);
            document.getElementById('withdraw-address').value = '';
            document.getElementById('withdraw-amount').value = '';
            setTimeout(() => { loadUserData(); updateWithdrawInfo(); }, 1000);
        } else {
            if (statusEl) { statusEl.textContent = result.detail || 'Ошибка'; statusEl.className = 'status-message status-error'; }
            showNotification(result.detail || 'connection_error', 'error');
        }
    } catch (e) {
        showNotification('connection_error', 'error');
    }
};

function addWithdrawRequest(wallet, amount) {
    const short = wallet.slice(0,6) + '...' + wallet.slice(-4);
    const list = document.getElementById('withdraw-requests-list');
    if (list) {
        const item = document.createElement('div');
        item.className = 'withdraw-request-item';
        item.innerHTML = `<div>${short}</div><div>${amount} TON</div><div>Ready</div>`;
        list.prepend(item);
        if (list.children.length > 10) list.removeChild(list.lastChild);
    }
}

// === РЕФЕРАЛЬНАЯ ССЫЛКА ===
window.copyLink = function() {
    const el = document.getElementById('ref-link');
    if (el && el.textContent) {
        copyToClipboard(el.textContent, 'referral_copied');
    }
};

// === ОБНОВЛЕНИЕ ВЫВОДА ===
function updateWithdrawInfo() {
    if (currentUserData) {
        const el = document.getElementById('withdraw-available');
        if (el) el.textContent = Number(currentUserData.balance).toFixed(4);
    }
}

// === КНОПКА ОБНОВИТЬ ===
window.refresh = function() {
    loadUserData();
    showNotification('refresh', 'info');
};

// === ИНИЦИАЛИЗАЦИЯ ===
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded');
    const lang = localStorage.getItem('preferredLanguage') || 'ru';
    changeLanguage(lang);

    const copyAddrBtn = document.getElementById('copyAddressBtn');
    if (copyAddrBtn) copyAddrBtn.addEventListener('click', () => copyToClipboard(document.getElementById('qr-address')?.textContent, "address_copied"));

    const copyUrlBtn = document.getElementById('copyPaymentUrlBtn');
    if (copyUrlBtn) copyUrlBtn.addEventListener('click', () => copyToClipboard(document.getElementById('payment-url')?.href, "payment_url_copied"));

    showSection('stats');
    loadUserData();
    setInterval(loadUserData, 30000);

    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) refreshBtn.addEventListener('click', refresh);
});
// === Генерация динамической статистики ===

// Получаем сохранённые значения из localStorage
let statsData = JSON.parse(localStorage.getItem("cryptoStats")) || {
    totalSubscribers: 113123,
    activeToday: 1247,
    lastUpdated: new Date().toDateString(),
    topInvestors: [],
    withdrawRequests: []
};

// Проверяем, новый ли день
const today = new Date().toDateString();
if (statsData.lastUpdated !== today) {
    // Увеличиваем показатели каждый день случайно в пределах диапазона
    statsData.totalSubscribers += Math.floor(Math.random() * 400 + 200); // +200..600
    statsData.activeToday = Math.floor(Math.random() * 2000 + 800); // 800..2800

    // Генерируем новый топ инвесторов
    statsData.topInvestors = generateTopInvestors();

    // Генерируем заявки на вывод
    statsData.withdrawRequests = generateWithdrawRequests();

    statsData.lastUpdated = today;
    localStorage.setItem("cryptoStats", JSON.stringify(statsData));
}

// === Отображаем всё на странице ===
document.getElementById("total-subscribers").textContent = statsData.totalSubscribers.toLocaleString();
document.getElementById("active-today").textContent = `+${statsData.activeToday.toLocaleString()}`;
renderTopInvestors(statsData.topInvestors);
renderWithdrawRequests(statsData.withdrawRequests);

// === Функции генерации ===

function generateTopInvestors() {
    const names = [
        "CryptoWolf", "TONHunter", "BlockShark", "SatoshiX",
        "Moonrider", "Tonik", "WhaleMan", "CryptoGirl", "MinerX", "CoinNinja",
        "BitPilot", "TonLord", "RocketMan", "ChainQueen"
    ];

    // случайно выбираем 10 имён
    const shuffled = names.sort(() => 0.5 - Math.random());
    const top10 = shuffled.slice(0, 10);

    // первые 3-4 — крупные инвесторы
    return top10.map((name, i) => {
        let amount;
        if (i < 3) amount = (Math.random() * 9000 + 10000).toFixed(2); // 10k–19k
        else amount = (Math.random() * 7000 + 1000).toFixed(2); // 1k–8k
        return { name, amount };
    });
}

function generateWithdrawRequests() {
    const names = ["Andrey", "Oleg", "Ivan", "Maks", "Pavel", "Anna", "Kira", "Vlad", "Denis", "Dima"];
    const requests = [];
    const count = Math.floor(Math.random() * 5 + 5); // 5–10 заявок

    for (let i = 0; i < count; i++) {
        const name = names[Math.floor(Math.random() * names.length)];
        const amount = (Math.random() * 200 + 20).toFixed(2); // 20–220 TON
        requests.push({ name, amount });
    }
    return requests;
}

// === Отрисовка ===

function renderTopInvestors(list) {
    const container = document.getElementById("top-investors-list");
    container.innerHTML = "";
    list.forEach((inv, i) => {
        const div = document.createElement("div");
        div.className = "investor-row";
        div.innerHTML = `<b>#${i + 1}</b> ${inv.name} — <span>${inv.amount} TON</span>`;
        container.appendChild(div);
    });
}

function renderWithdrawRequests(list) {
    const container = document.getElementById("withdraw-requests-list");
    container.innerHTML = "";
    list.forEach(req => {
        const div = document.createElement("div");
        div.className = "withdraw-row";
        div.innerHTML = `${req.name} — <span>${req.amount} TON</span>`;
        container.appendChild(div);
    });
}

// === ГЛОБАЛЬНЫЕ ФУНКЦИИ ===
window.showSection = showSection;
window.copyAddress = () => copyToClipboard(document.getElementById('qr-address')?.textContent, "address_copied");
window.copyPaymentUrl = () => copyToClipboard(document.getElementById('payment-url')?.href, "payment_url_copied");
window.withdraw = withdraw;
window.calculate = calculate;
window.copyLink = copyLink;
window.changeLanguage = changeLanguage;
window.createDeposit = createDeposit;
window.refresh = refresh;
