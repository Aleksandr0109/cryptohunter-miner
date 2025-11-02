// === script.js — ПОЛНАЯ ПРОДАКШЕН ВЕРСИЯ С МУЛЬТИЯЗЫЧНОСТЬЮ ===
console.log("CryptoHunter Miner WebApp загружен");

const tg = window.Telegram?.WebApp;

// Конфигурация из переменных окружения
const CONFIG = {
    API_BASE: window.location.origin,
    MIN_INVEST: 1,
    MIN_WITHDRAW: 1,
    DAILY_RATE: 0.25,
    BONUS_PERCENT: 5,
    REFERRAL_LEVEL1: 5,
    REFERRAL_LEVEL2: 2,
    BOT_USERNAME: 'cruptos023bot'
};

// Система перевода
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
        "min_withdraw_error": "Минимальная сумма вывода 1 TON",
        "insufficient_funds": "Недостаточно средств для вывода",
        "withdraw_success": "Запрос на вывод успешно отправлен!",
        "payment_confirmed": "Платеж подтвержден! Бонус:",
        "payment_pending": "Платеж еще не подтвержден",
        "no_pending_payments": "Нет ожидающих платежей",
        "referral_copied": "Реферальная ссылка скопирована!",
        "connection_error": "Ошибка соединения"
    },
    en: {
        // Basic elements
        "invest": "Invest",
        "withdraw": "Withdraw",
        "your_balance": "YOUR BALANCE",
        "invested": "Invested",
        "earned": "Earned",
        "speed": "Speed",
        "detailed_stats": "Detailed Statistics",
        "referral_program": "Referral Program",
        "back": "Back",
        
        // Detailed statistics
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
        
        // Referral program
        "direct_referrals": "direct referrals",
        "level_2": "Level 2",
        "earned_ton": "Earned TON",
        "your_referral_link": "Your referral link:",
        "copy_link": "Copy link",
        
        // Investing
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
        
        // Withdrawal
        "withdraw_funds": "Withdraw Funds",
        "available_for_withdraw": "Available for withdrawal:",
        "ton_wallet_address": "TON wallet address:",
        "withdraw_amount": "Withdrawal amount (TON):",
        
        // Placeholders
        "min_ton": "Minimum 1 TON",
        "enter_amount": "Enter amount",
        "wallet_placeholder": "Starts with kQ, UQ or EQ",
        
        // Notifications
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
        "connection_error": "Connection error"
    }
};

let currentLanguage = 'ru';
let currentUserData = null;

// === ПОЛУЧИТЬ initData ===
function getInitData() {
    return tg?.initData || '';
}

// === СМЕНА ЯЗЫКА ===
function changeLanguage(lang) {
    if (currentLanguage === lang) return;
    
    currentLanguage = lang;
    
    // Обновляем активную кнопку языка
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(`lang-${lang}`).classList.add('active');
    
    // Обновляем все тексты
    updateAllTexts();
    
    // Сохраняем язык в localStorage
    localStorage.setItem('preferredLanguage', lang);
}

// === ОБНОВЛЕНИЕ ВСЕХ ТЕКСТОВ ===
function updateAllTexts() {
    // Обновляем тексты с data-i18n
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[currentLanguage][key]) {
            element.textContent = translations[currentLanguage][key];
        }
    });
    
    // Обновляем плейсхолдеры
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
    
    if (id === 'stats') {
        loadUserData();
    } else if (id === 'dashboard') {
        loadDashboardData();
    } else if (id === 'referral') {
        loadReferralData();
    } else if (id === 'withdraw') {
        updateWithdrawInfo();
    } else if (id === 'invest') {
        const qrSection = document.getElementById('qr-section');
        if (qrSection) qrSection.style.display = 'none';
    }
}

// === УВЕДОМЛЕНИЯ ===
function showNotification(msgKey, type = 'info') {
    const n = document.getElementById('notification');
    if (n) {
        const message = translations[currentLanguage][msgKey] || msgKey;
        n.textContent = message;
        n.className = 'notification';
        n.style.background = type === 'error' ? '#ff4444' : '#00ffcc';
        n.classList.add('show');
        setTimeout(() => n.classList.remove('show'), 3000);
    }
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
            
            document.getElementById('balance').textContent = Number(userData.balance).toFixed(4);
            document.getElementById('invested').textContent = Number(userData.invested).toFixed(2);
            document.getElementById('earned').textContent = Number(userData.earned).toFixed(4);
            document.getElementById('speed').textContent = userData.speed;
            
            updateWithdrawInfo();
        }
    } catch (e) {
        console.error('Ошибка загрузки:', e);
        showNotification('server_sleeping', 'error');
    }
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
            document.getElementById('dash-monthly-inv').textContent = (dashData.daily_investment * 30).toFixed(2) + ' TON';
            
            document.getElementById('dash-speed').textContent = `${dashData.speed.toFixed(0)}%`;
            document.getElementById('dash-daily-free').textContent = dashData.daily_free.toFixed(4) + ' TON';
            document.getElementById('dash-days-per-ton').textContent = dashData.days_per_ton.toFixed(1) + ' ' + (currentLanguage === 'ru' ? 'дней' : 'days');
            document.getElementById('dash-accumulated').textContent = dashData.balance.toFixed(2) + ' TON';
            
            document.getElementById('dash-total-daily').textContent = dashData.total_daily.toFixed(4) + ' TON';
            document.getElementById('dash-hourly').textContent = dashData.hourly.toFixed(4) + ' TON';
            
            const withdrawStatus = dashData.can_withdraw ? 
                (currentLanguage === 'ru' ? "✅ Готово" : "✅ Ready") : 
                (currentLanguage === 'ru' ? "❌ Не готово" : "❌ Not ready");
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
            
            const refLink = `https://t.me/${CONFIG.BOT_USERNAME}?start=ref_${refData.user_id}`;
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
        showNotification(`Введите сумму от ${CONFIG.MIN_INVEST} TON`, 'error');
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
            <div class="calc-result-item">
                <span>${translations[currentLanguage]['day']}</span>
                <b>${daily.toFixed(4)} TON</b>
            </div>
            <div class="calc-result-item">
                <span>${translations[currentLanguage]['week']}</span>
                <b>${(daily * 7).toFixed(4)} TON</b>
            </div>
            <div class="calc-result-item">
                <span>${translations[currentLanguage]['month']}</span>
                <b>${monthly.toFixed(4)} TON</b>
            </div>
            <div class="calc-result-item">
                <span>${translations[currentLanguage]['year']}</span>
                <b>${yearly.toFixed(4)} TON</b>
            </div>
            <div class="calc-result-item">
                <span>${translations[currentLanguage]['investment_bonus']}</span>
                <b>+${bonus.toFixed(2)} TON</b>
            </div>
        `;
    }
    showNotification('calc_local', 'info');
}

function updateCalculatorResults(amount, data) {
    const calcResult = document.getElementById('calc-result');
    if (calcResult) {
        calcResult.innerHTML = `
            <div class="calc-result-item">
                <span>${translations[currentLanguage]['day']}</span>
                <b>${data.daily.toFixed(4)} TON</b>
            </div>
            <div class="calc-result-item">
                <span>${translations[currentLanguage]['week']}</span>
                <b>${(data.daily * 7).toFixed(4)} TON</b>
            </div>
            <div class="calc-result-item">
                <span>${translations[currentLanguage]['month']}</span>
                <b>${data.monthly.toFixed(4)} TON</b>
            </div>
            <div class="calc-result-item">
                <span>${translations[currentLanguage]['year']}</span>
                <b>${data.yearly.toFixed(4)} TON</b>
            </div>
            <div class="calc-result-item">
                <span>${translations[currentLanguage]['investment_bonus']}</span>
                <b>+${(amount * CONFIG.BONUS_PERCENT / 100).toFixed(2)} TON</b>
            </div>
        `;
    }
}

// === ГЕНЕРАЦИЯ QR ДЛЯ ОПЛАТЫ ===
window.generateQR = async function() {
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
        const response = await fetch("/api/qr", {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "X-Telegram-WebApp-Init-Data": getInitData()
            },
            body: JSON.stringify({ amount }),
        });

        if (!response.ok) {
            throw new Error("Ошибка при получении QR");
        }

        const data = await response.json();

        if (data.qr_code) {
            const qrSection = document.getElementById("qr-section");
            const qrImg = document.getElementById("qr-img");
            const qrAddress = document.getElementById("qr-address");

            qrImg.src = data.qr_code;
            qrAddress.textContent = data.address || "—";
            qrSection.style.display = "block";

            qrSection.scrollIntoView({ behavior: 'smooth' });
            
            console.log("✅ QR-код успешно загружен!");
            showNotification("qr_ready", "success");
        } else {
            showNotification("Ошибка: сервер не вернул QR-код.", "error");
        }
    } catch (err) {
        console.error("Ошибка запроса:", err);
        showNotification("Не удалось получить QR-код.", "error");
    }
};

// === КОПИРОВАНИЕ АДРЕСА ===
window.copyAddress = function() {
    const address = document.getElementById('qr-address');
    if (address && address.textContent && address.textContent !== '—') {
        navigator.clipboard.writeText(address.textContent).then(function() {
            showNotification('address_copied', 'success');
        }).catch(function() {
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

// === ПРОВЕРКА ПЛАТЕЖА ===
window.checkPayment = async function() {
    try {
        const res = await fetch(`${CONFIG.API_BASE}/api/check`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Telegram-WebApp-Init-Data': getInitData()
            }
        });
        
        if (res.ok) {
            const result = await res.json();
            
            if (result.status === 'success') {
                const message = currentLanguage === 'ru' 
                    ? `✅ Платеж подтвержден! Бонус: ${result.bonus.toFixed(4)} TON`
                    : `✅ Payment confirmed! Bonus: ${result.bonus.toFixed(4)} TON`;
                showNotification(message, 'success');
                loadUserData();
                loadDashboardData();
            } else if (result.status === 'pending') {
                showNotification('payment_pending', 'info');
            } else {
                showNotification('no_pending_payments', 'info');
            }
        }
    } catch (e) {
        showNotification('connection_error', 'error');
    }
};

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

// === АВТОМАТИЧЕСКИЙ ЗАПУСК ===
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing app...');
    
    // Загружаем сохраненный язык
    const savedLanguage = localStorage.getItem('preferredLanguage') || 'ru';
    changeLanguage(savedLanguage);
    
    // Инициализация кнопки копирования адреса
    const copyAddressBtn = document.getElementById('copyAddressBtn');
    if (copyAddressBtn) {
        copyAddressBtn.addEventListener('click', copyAddress);
    }
    
    // Показываем главный экран и загружаем данные
    showSection('stats');
    loadUserData();
    
    // Автообновление каждые 30 секунд
    setInterval(loadUserData, 30000);
});

// Глобальные функции
window.showSection = showSection;
window.checkPayment = checkPayment;
window.copyAddress = copyAddress;
window.withdraw = withdraw;
window.calculate = calculate;
window.copyLink = copyLink;
window.changeLanguage = changeLanguage;