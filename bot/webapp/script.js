// === script.js — РАБОЧАЯ СИСТЕМА ОПЛАТЫ + МУЛЬТИЯЗЫЧНОСТЬ + АВТО-НАЧИСЛЕНИЯ + УЛУЧШЕНИЯ ===
console.log("CryptoHunter Miner WebApp загружен");
const tg = window.Telegram?.WebApp;

// Конфигурация
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

// === СИСТЕМА ПЕРЕВОДА ===
const translations = {
    ru: {
        // Основные элементы
        "invest": "Инвестировать",
        "withdraw": "Вывод",
        "your_balance": "ВАШ БАЛАНС",
        "invested": "Инвестировано",
        "earned": "Заработано",
        "speed": "Скорость",
        "detailed_stats": "Детальная статистика",
        "referral_program": "Реферальная программа",
        "back": "Назад",
      
        // Детальная статистика
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
      
        // Новые элементы
        "community": "СООБЩЕСТВО",
        "total_subscribers": "Всего подписчиков:",
        "active_today": "Активных сегодня:",
        "top_investors": "ТОП 10 ИНВЕСТОРОВ",
        "withdraw_requests": "ЗАЯВКИ НА ВЫВОД",
        "wallet": "Кошелек",
        "amount_ton": "Сумма TON",
        "status": "Статус",
      
        // Реферальная программа
        "direct_referrals": "прямых рефералов",
        "level_2": "2-й уровень",
        "earned_ton": "Заработано TON",
        "your_referral_link": "Ваша реферальная ссылка:",
        "copy_link": "Скопировать ссылку",
      
        // Инвестирование
        "investing": "Инвестирование",
        "investment_amount": "Сумма инвестиции (TON):",
        "generate_qr": "Сгенерировать QR для оплаты",
        "scan_qr": "Отсканируйте QR-код для оплаты:",
        "ton_address": "Адрес TON:",
        "copy_address": "Скопировать адрес",
        "profit_calculator": "Калькулятор доходности",
        "amount_for_calc": "Сумма для расчета:",
        "calculate_profit": "Рассчитать доходность",
        "investment_bonus": "Бонус за инвестицию:",
        "year": "Год:",
      
        // Вывод
        "withdraw_funds": "Вывод средств",
        "available_for_withdraw": "Доступно для вывода:",
        "ton_wallet_address": "Адрес TON кошелька:",
        "withdraw_amount": "Сумма вывода (TON):",
      
        // Плейсхолдеры
        "min_ton": "Минимум 1 TON",
        "enter_amount": "Введите сумму",
        "wallet_placeholder": "Начинается с kQ, UQ или EQ",
      
        // Уведомления
        "server_sleeping": "Сервер спит...",
        "calc_local": "Расчет выполнен локально",
        "qr_ready": "QR-код готов для сканирования!",
        "address_copied": "Адрес скопирован в буфер обмена!",
        "copy_error": "Не удалось скопировать адрес",
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
        "payment_checking_auto": "Автопроверка каждые 5 сек..."
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
        "copy_error": "Failed to copy address",
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
        "payment_checking_auto": "Auto-check every 5 sec..."
    }
};

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

// === ОБНОВЛЕНИЕ ВСЕХ ТЕКСТОВ ===
function updateAllTexts() {
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[currentLanguage][key]) {
            element.textContent = translations[currentLanguage][key];
        }
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        if (translations[currentLanguage][key]) {
            element.placeholder = translations[currentLanguage][key];
        }
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
    if (n) {
        const message = (translations[currentLanguage][msgKey] || msgKey) + (extra ? ` ${extra}` : '');
        n.textContent = message;
        n.className = 'notification';
        n.style.background = type === 'error' ? '#ff4444' : type === 'success' ? '#00ff88' : '#00ccff';
        n.classList.add('show');
        setTimeout(() => n.classList.remove('show'), 3000);
    }
}

// === АНИМАЦИЯ ЧИСЕЛ ===
function animateValue(id, end, duration = 600) {
    const element = document.getElementById(id);
    if (!element) return;
    const start = parseFloat(element.textContent) || 0;
    const range = end - start;
    const startTime = performance.now();
    function step(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const value = start + range * progress;
        element.textContent = value.toFixed(4);
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
            const userData = await res.json();
            currentUserData = userData;
            animateValue('balance', parseFloat(userData.balance));
            document.getElementById('invested').textContent = Number(userData.invested).toFixed(2);
            document.getElementById('earned').textContent = Number(userData.earned).toFixed(4);
            document.getElementById('speed').textContent = userData.speed;
            updateWithdrawInfo();
            startHourlyAccrual(); // ВКЛЮЧЕНО
        }
    } catch (e) {
        showNotification('server_sleeping', 'error');
    }
}

// === АВТО-НАЧИСЛЕНИЯ КАЖДЫЙ ЧАС ===
function startHourlyAccrual() {
    if (hourlyAccrualInterval) clearInterval(hourlyAccrualInterval);
    hourlyAccrualInterval = setInterval(() => {
        if (!currentUserData) return;
        const invested = parseFloat(currentUserData.invested) || 0;
        const hourlyRate = (invested * CONFIG.DAILY_RATE) / 24 / 100;
        const newBalance = (parseFloat(currentUserData.balance) || 0) + hourlyRate;
        currentUserData.balance = newBalance.toFixed(4);
        currentUserData.earned = (parseFloat(currentUserData.earned) || 0) + hourlyRate;
        animateValue('balance', newBalance);
        document.getElementById('earned').textContent = currentUserData.earned.toFixed(4);
        showNotification('accrued', 'success', `+${hourlyRate.toFixed(4)} TON`);
        if (document.getElementById('dashboard').classList.contains('active')) {
            loadDashboardData();
        }
    }, 60000); // 1 минута для теста, в проде: 3600000
}

// === ЗАГРУЗКА ДЕТАЛЬНОЙ СТАТИСТИКИ ===
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
            const dashData = await res.json();
            document.getElementById('dash-invested').textContent = `${dashData.invested.toFixed(2)} TON`;
            document.getElementById('dash-daily-inv').textContent = dashData.daily_investment.toFixed(3) + ' TON';
            document.getElementById('dash-weekly-inv').textContent = (dashData.daily_investment * 7).toFixed(3) + ' TON';
            document.getElementById('dash-monthly-iv').textContent = (dashData.daily_investment * 30).toFixed(2) + ' TON';
            document.getElementById('dash-speed').textContent = `${dashData.speed.toFixed(0)}%`;
            document.getElementById('dash-daily-free').textContent = dashData.daily_free.toFixed(4) + ' TON';
            document.getElementById('dash-days-per-ton').textContent = dashData.days_per_ton.toFixed(1) + ' ' + (currentLanguage === 'ru' ? 'дней' : 'days');
            document.getElementById('dash-accumulated').textContent = dashData.balance.toFixed(2) + ' TON';
            document.getElementById('dash-total-daily').textContent = dashData.total_daily.toFixed(4) + ' TON';
            document.getElementById('dash-hourly').textContent = dashData.hourly.toFixed(4) + ' TON';
            const withdrawStatus = dashData.can_withdraw ?
                (currentLanguage === 'ru' ? "Готово" : "Ready") :
                (currentLanguage === 'ru' ? "Не готово" : "Not ready");
            document.getElementById('dash-withdraw-status').textContent = withdrawStatus;
            const remaining = Math.max(0, CONFIG.MIN_WITHDRAW - dashData.balance);
            const minWithdrawText = currentLanguage === 'ru'
                ? `Минимум: ${CONFIG.MIN_WITHDRAW} TON (${remaining.toFixed(2)} TON осталось)`
                : `Minimum: ${CONFIG.MIN_WITHDRAW} TON (${remaining.toFixed(2)} TON left)`;
            document.getElementById('dash-min-withdraw').textContent = minWithdrawText;
        }
    } catch (e) {
        console.error('Ошибка загрузки дашборда:', e);
    }
}

// === ЗАГРУЗКА РЕФЕРАЛЬНЫХ ДАННЫХ ===
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
            const refData = await res.json();
            document.getElementById('ref-direct').textContent = refData.direct_count;
            document.getElementById('ref-level2').textContent = refData.level2_count;
            document.getElementById('ref-income').textContent = Number(refData.income).toFixed(2);
            const refLink = refData.link || `https://t.me/${CONFIG.BOT_USERNAME}?start=ref_${currentUserData?.user_id || 'unknown'}`;
            document.getElementById('ref-link').textContent = refLink;
        }
    } catch (e) {
        console.error('Ошибка загрузки реферальных данных:', e);
    }
}

// === КАЛЬКУЛЯТОР ДОХОДНОСТИ ===
window.calculate = async function() {
    const amount = parseFloat(document.getElementById('calc-amount').value);
    if (!amount || amount < CONFIG.MIN_INVEST) {
        showNotification('min_invest_error', 'error');
        return;
    }
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
    const monthly = daily * 30;
    const yearly = daily * 365;
    const bonus = amount * (CONFIG.BONUS_PERCENT / 100);
    const calcResult = document.getElementById('calc-result');
    if (calcResult) {
        calcResult.innerHTML = `
            <div class="calc-result-item"><span>${translations[currentLanguage]['day']}</span><b>${daily.toFixed(4)} TON</b></div>
            <div class="calc-result-item"><span>${translations[currentLanguage]['week']}</span><b>${(daily * 7).toFixed(4)} TON</b></div>
            <div class="calc-result-item"><span>${translations[currentLanguage]['month']}</span><b>${monthly.toFixed(4)} TON</b></div>
            <div class="calc-result-item"><span>${translations[currentLanguage]['year']}</span><b>${yearly.toFixed(4)} TON</b></div>
            <div class="calc-result-item"><span>${translations[currentLanguage]['investment_bonus']}</span><b>+${bonus.toFixed(2)} TON</b></div>
        `;
    }
    showNotification('calc_local', 'info');
}

function updateCalculatorResults(amount, data) {
    const calcResult = document.getElementById('calc-result');
    if (calcResult) {
        calcResult.innerHTML = `
            <div class="calc-result-item"><span>${translations[currentLanguage]['day']}</span>< fortnight>${data.daily.toFixed(4)} TON</b></div>
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
    if (!amount || isNaN(amount) || amount <= 0) {
        showNotification("enter_correct_amount", "error");
        return;
    }
    if (amount < CONFIG.MIN_INVEST) {
        showNotification("min_invest_error", "error");
        return;
    }
    try {
        showNotification("payment_checking", "info");
        const response = await fetch("/api/deposit", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Telegram-WebApp-Init-Data": getInitData()
            },
            body: JSON.stringify({ amount: parseFloat(amount) }),
        });
        if (!response.ok) throw new Error("Ошибка при создании депозита");
        const data = await response.json();
        if (data.success) {
            currentDepositId = data.deposit_id;
            const qrSection = document.getElementById("qr-section");
            const qrImg = document.getElementById("qr-img");
            const qrAddress = document.getElementById("qr-address");
            const qrComment = document.getElementById("qr-comment");
            const paymentUrl = document.getElementById("payment-url");
            const checkBtn = document.getElementById("checkPaymentBtn");

            qrImg.src = data.qr_code;
            qrAddress.textContent = data.address || "—";
            qrComment.textContent = data.comment || "—";
            paymentUrl.href = data.payment_url;
            paymentUrl.textContent = data.payment_url;

            qrSection.style.display = "block";
            qrSection.scrollIntoView({ behavior: 'smooth' });

            // Кнопка проверки
            if (checkBtn) {
                checkBtn.style.display = 'block';
                checkBtn.textContent = translations[currentLanguage].check_payment;
                checkBtn.onclick = () => checkPaymentManually();
            }

            showNotification("deposit_created", "success");
            showNotification("payment_checking_auto", "info");
            startPaymentChecking(currentDepositId);
        } else {
            showNotification("Ошибка создания депозита", "error");
        }
    } catch (err) {
        console.error("Ошибка запроса:", err);
        showNotification("connection_error", "error");
    }
};

// === РУЧНАЯ ПРОВЕРКА ПЛАТЕЖА ===
function checkPaymentManually() {
    if (!currentDepositId) return;
    showNotification("payment_checking", "info");
    fetch("/api/check-payment", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-Telegram-WebApp-Init-Data": getInitData()
        },
        body: JSON.stringify({ deposit_id: currentDepositId }),
    })
    .then(r => r.json())
    .then(result => {
        if (result.status === 'completed') {
            stopPaymentChecking();
            showNotification(`payment_confirmed ${result.bonus?.toFixed(4) || 0} TON`, 'success');
            loadUserData();
            loadDashboardData();
            setTimeout(() => {
                document.getElementById("qr-section").style.display = 'none';
                document.getElementById("checkPaymentBtn").style.display = 'none';
            }, 3000);
        } else {
            showNotification('payment_pending', 'info');
        }
    })
    .catch(() => showNotification('payment_error', 'error'));
}

// === ЗАПУСК ПРОВЕРКИ ПЛАТЕЖА ===
function startPaymentChecking(depositId) {
    stopPaymentChecking();
    paymentCheckInterval = setInterval(async () => {
        try {
            const response = await fetch("/api/check-payment", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Telegram-WebApp-Init-Data": getInitData()
                },
                body: JSON.stringify({ deposit_id: depositId }),
            });
            if (response.ok) {
                const result = await response.json();
                if (result.status === 'completed') {
                    stopPaymentChecking();
                    showNotification(`payment_confirmed ${result.bonus?.toFixed(4) || 0} TON`, 'success');
                    loadUserData();
                    loadDashboardData();
                    setTimeout(() => {
                        const qrSection = document.getElementById("qr-section");
                        if (qrSection) qrSection.style.display = 'none';
                        const btn = document.getElementById("checkPaymentBtn");
                        if (btn) btn.style.display = 'none';
                    }, 3000);
                } else if (result.status === 'expired') {
                    stopPaymentChecking();
                    showNotification('payment_expired', 'error');
                }
            }
        } catch (error) {
            console.error('Ошибка проверки платежа:', error);
        }
    }, 5000);
    setTimeout(() => stopPaymentChecking(), 25 * 60 * 1000);
}

// === ОСТАНОВКА ПРОВЕРКИ ПЛАТЕЖА ===
function stopPaymentChecking() {
    if (paymentCheckInterval) {
        clearInterval(paymentCheckInterval);
        paymentCheckInterval = null;
    }
}

// === КОПИРОВАНИЕ АДРЕСА ===
window.copyAddress = function() {
    const address = document.getElementById('qr-address');
    if (address && address.textContent && address.textContent !== '—') {
        navigator.clipboard.writeText(address.textContent).then(() => {
            showNotification('address_copied', 'success');
        }).catch(() => {
            showNotification('copy_error', 'error');
        });
    } else {
        showNotification('no_address', 'error');
    }
};

// === КОПИРОВАНИЕ ССЫЛКИ ОПЛАТЫ ===
window.copyPaymentUrl = function() {
    const paymentUrl = document.getElementById('payment-url');
    if (paymentUrl && paymentUrl.href) {
        navigator.clipboard.writeText(paymentUrl.href).then(() => {
            showNotification('address_copied', 'success');
        }).catch(() => {
            showNotification('copy_error', 'error');
        });
    } else {
        showNotification('no_address', 'error');
    }
};

// === ВЫВОД СРЕДСТВ ===
window.withdraw = async function() {
    const addr = document.getElementById('withdraw-address').value.trim();
    const amount = parseFloat(document.getElementById('withdraw-amount').value);
    const available = parseFloat(document.getElementById('withdraw-available').textContent);
    if (!addr) {
        showNotification('enter_wallet', 'error');
        return;
    }
    if (!addr.startsWith('kQ') && !addr.startsWith('UQ') && !addr.startsWith('EQ')) {
        showNotification('wallet_format_error', 'error');
        return;
    }
    if (!amount || amount < CONFIG.MIN_WITHDRAW) {
        showNotification('min_withdraw_error', 'error');
        return;
    }
    if (amount > available) {
        showNotification('insufficient_funds', 'error');
        return;
    }
    try {
        const res = await fetch(`${CONFIG.API_BASE}/api/withdraw`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Telegram-WebApp-Init-Data': getInitData()
            },
            body: JSON.stringify({ address: addr, amount })
        });
        const result = await res.json();
        const statusElement = document.getElementById('withdraw-status');
        if (res.ok) {
            if (statusElement) {
                statusElement.textContent = result.message || (currentLanguage === 'ru' ? 'Запрос на вывод отправлен' : 'Withdrawal request sent');
                statusElement.className = 'status-message status-success';
            }
            showNotification('withdraw_success', 'success');
            addWithdrawRequest(addr, amount);
            document.getElementById('withdraw-address').value = '';
            document.getElementById('withdraw-amount').value = '';
            setTimeout(() => {
                loadUserData();
                updateWithdrawInfo();
            }, 1000);
        } else {
            if (statusElement) {
                statusElement.textContent = result.detail || (currentLanguage === 'ru' ? 'Ошибка вывода' : 'Withdrawal error');
                statusElement.className = 'status-message status-error';
            }
            showNotification(result.detail || (currentLanguage === 'ru' ? 'Ошибка вывода' : 'Withdrawal error'), 'error');
        }
    } catch (e) {
        const statusElement = document.getElementById('withdraw-status');
        if (statusElement) {
            statusElement.textContent = currentLanguage === 'ru' ? 'Ошибка соединения' : 'Connection error';
            statusElement.className = 'status-message status-error';
        }
        showNotification('connection_error', 'error');
    }
};

// === ДОБАВЛЕНИЕ ЗАЯВКИ НА ВЫВОД ===
function addWithdrawRequest(wallet, amount) {
    const shortWallet = wallet.substring(0, 6) + '...' + wallet.substring(wallet.length - 4);
    const list = document.getElementById('withdraw-requests-list');
    if (list) {
        const item = document.createElement('div');
        item.className = 'withdraw-request-item';
        item.innerHTML = `<div>${shortWallet}</div><div>${amount} TON</div><div>Ready</div>`;
        list.prepend(item);
        if (list.children.length > 10) list.removeChild(list.lastChild);
    }
}

// === КОПИРОВАНИЕ РЕФЕРАЛЬНОЙ ССЫЛКИ ===
window.copyLink = function() {
    const linkElement = document.getElementById('ref-link');
    if (linkElement && linkElement.textContent) {
        navigator.clipboard.writeText(linkElement.textContent);
        showNotification('referral_copied', 'success');
    }
};

// === ОБНОВЛЕНИЕ ИНФОРМАЦИИ О ВЫВОДЕ ===
function updateWithdrawInfo() {
    if (currentUserData) {
        const availableElement = document.getElementById('withdraw-available');
        if (availableElement) {
            availableElement.textContent = Number(currentUserData.balance).toFixed(4);
        }
    }
}

// === КНОПКА ОБНОВИТЬ ===
window.refresh = function() {
    loadUserData();
    showNotification('refresh', 'info');
};

// === АВТОМАТИЧЕСКИЙ ЗАПУСК ===
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing app...');
    const savedLanguage = localStorage.getItem('preferredLanguage') || 'ru';
    changeLanguage(savedLanguage);
    const copyAddressBtn = document.getElementById('copyAddressBtn');
    if (copyAddressBtn) copyAddressBtn.addEventListener('click', copyAddress);
    const copyPaymentUrlBtn = document.getElementById('copyPaymentUrlBtn');
    if (copyPaymentUrlBtn) copyPaymentUrlBtn.addEventListener('click', copyPaymentUrl);
    showSection('stats');
    loadUserData();
    setInterval(loadUserData, 30000);
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) refreshBtn.addEventListener('click', refresh);
});

// Глобальные функции
window.showSection = showSection;
window.copyAddress = copyAddress;
window.copyPaymentUrl = copyPaymentUrl;
window.withdraw = withdraw;
window.calculate = calculate;
window.copyLink = copyLink;
window.changeLanguage = changeLanguage;
window.createDeposit = createDeposit;
window.refresh = refresh;
