// === script.js — ДИНАМИЧЕСКИЕ ДАННЫЕ БЕЗ ИЗМЕНЕНИЯ БАЛАНСА ===
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

// === ГЕНЕРАТОР СЛУЧАЙНЫХ ДАННЫХ ===
class DataGenerator {
    static generateTopInvestors(count = 10) {
        const names = [
            "CryptoWolf", "TONHunter", "BlockShark", "SatoshiX", "Moonrider", 
            "Tonik", "WhaleMan", "CryptoGirl", "MinerX", "CoinNinja",
            "BitPilot", "TonLord", "RocketMan", "ChainQueen", "CryptoKing",
            "DigitalBull", "TonWhale", "BlockMaster", "CoinHunter", "ProfitSeeker"
        ];
        
        const shuffled = [...names].sort(() => Math.random() - 0.5);
        return shuffled.slice(0, count).map((name, index) => {
            let amount;
            if (index < 3) amount = (Math.random() * 15000 + 5000).toFixed(2);
            else if (index < 7) amount = (Math.random() * 4000 + 1000).toFixed(2);
            else amount = (Math.random() * 900 + 100).toFixed(2);
            
            return {
                name,
                amount: parseFloat(amount),
                change: (Math.random() - 0.3) * 10
            };
        }).sort((a, b) => b.amount - a.amount);
    }

    static generateWithdrawRequests(count = 8) {
        const names = ["Andrey", "Oleg", "Ivan", "Maks", "Pavel", "Anna", "Kira", "Vlad", "Denis", "Dima", "Sergey", "Maria"];
        const statuses = ["completed", "pending", "processing"];
        
        return Array.from({length: count}, () => {
            const name = names[Math.floor(Math.random() * names.length)];
            const amount = (Math.random() * 500 + 10).toFixed(2);
            const status = statuses[Math.floor(Math.random() * statuses.length)];
            const hoursAgo = Math.floor(Math.random() * 24);
            
            return {
                name,
                amount: parseFloat(amount),
                status,
                timestamp: Date.now() - (hoursAgo * 60 * 60 * 1000),
                address: this.generateTONAddress()
            };
        }).sort((a, b) => b.timestamp - a.timestamp);
    }

    static generateTONAddress() {
        const prefixes = ['kQ', 'UQ', 'EQ'];
        const prefix = prefixes[Math.floor(Math.random() * prefixes.length)];
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let address = prefix;
        for (let i = 0; i < 46; i++) {
            address += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return address;
    }

    static generateCommunityStats() {
        const baseSubscribers = 113123;
        const baseActive = 1247;
        
        const subscriberChange = Math.floor(Math.random() * 200 - 50);
        const activeChange = Math.floor(Math.random() * 100 - 20);
        
        return {
            totalSubscribers: baseSubscribers + subscriberChange,
            activeToday: Math.max(800, baseActive + activeChange),
            onlineNow: Math.floor(Math.random() * 300 + 200)
        };
    }
}

// === ДИНАМИЧЕСКОЕ ОБНОВЛЕНИЕ ДАННЫХ ===
class DynamicDataManager {
    constructor() {
        this.updateIntervals = {};
        this.currentData = this.loadInitialData();
    }

    loadInitialData() {
        const saved = localStorage.getItem("cryptoDynamicData");
        if (saved) {
            return JSON.parse(saved);
        }

        return {
            lastUpdated: Date.now(),
            topInvestors: DataGenerator.generateTopInvestors(),
            withdrawRequests: DataGenerator.generateWithdrawRequests(),
            communityStats: DataGenerator.generateCommunityStats()
        };
    }

    saveData() {
        this.currentData.lastUpdated = Date.now();
        localStorage.setItem("cryptoDynamicData", JSON.stringify(this.currentData));
    }

    startDynamicUpdates() {
        // Обновление топа инвесторов каждые 2 минуты
        this.updateIntervals.topInvestors = setInterval(() => {
            this.updateTopInvestors();
        }, 120000);

        // Обновление заявок на вывод каждую минуту
        this.updateIntervals.withdrawRequests = setInterval(() => {
            this.updateWithdrawRequests();
        }, 60000);

        // Обновление статистики сообщества каждые 30 секунд
        this.updateIntervals.community = setInterval(() => {
            this.updateCommunityStats();
        }, 30000);

        console.log("Динамические обновления запущены");
    }

    stopDynamicUpdates() {
        Object.values(this.updateIntervals).forEach(interval => {
            clearInterval(interval);
        });
        this.updateIntervals = {};
    }

    updateTopInvestors() {
        const currentInvestors = this.currentData.topInvestors;
        
        const updatedInvestors = currentInvestors.map(investor => {
            const change = (Math.random() - 0.4) * 8;
            const newAmount = Math.max(100, investor.amount * (1 + change / 100));
            
            return {
                ...investor,
                amount: parseFloat(newAmount.toFixed(2)),
                change: parseFloat(change.toFixed(1))
            };
        }).sort((a, b) => b.amount - a.amount);

        if (Math.random() < 0.1 && updatedInvestors.length < 15) {
            const newInvestors = DataGenerator.generateTopInvestors(1);
            updatedInvestors.push(...newInvestors);
            updatedInvestors.sort((a, b) => b.amount - a.amount).slice(0, 15);
        }

        this.currentData.topInvestors = updatedInvestors;
        this.renderTopInvestors();
        this.saveData();
    }

    updateWithdrawRequests() {
        const currentRequests = this.currentData.withdrawRequests;
        
        const updatedRequests = currentRequests.map(request => {
            if (request.status === 'pending' && Math.random() < 0.3) {
                return { ...request, status: 'processing' };
            }
            if (request.status === 'processing' && Math.random() < 0.2) {
                return { ...request, status: 'completed' };
            }
            return request;
        }).filter(request => {
            if (request.status === 'completed') {
                return Date.now() - request.timestamp < 24 * 60 * 60 * 1000;
            }
            return true;
        });

        if (Math.random() < 0.3) {
            const newRequests = DataGenerator.generateWithdrawRequests(1);
            updatedRequests.unshift(...newRequests);
            
            if (updatedRequests.length > 12) {
                updatedRequests.splice(12);
            }
        }

        this.currentData.withdrawRequests = updatedRequests;
        this.renderWithdrawRequests();
        this.saveData();
    }

    updateCommunityStats() {
        this.currentData.communityStats = DataGenerator.generateCommunityStats();
        this.renderCommunityStats();
        this.saveData();
    }

    // === ОТРИСОВКА ДАННЫХ ===
    renderTopInvestors() {
        const container = document.getElementById("top-investors-list");
        if (!container) return;

        const investors = this.currentData.topInvestors.slice(0, 10);
        
        container.innerHTML = investors.map((investor, index) => {
            const changeClass = investor.change >= 0 ? 'positive' : 'negative';
            const changeSymbol = investor.change >= 0 ? '↗' : '↘';
            
            return `
                <div class="investor-row">
                    <div class="investor-rank">#${index + 1}</div>
                    <div class="investor-name">${investor.name}</div>
                    <div class="investor-amount">${investor.amount.toLocaleString()} TON</div>
                    <div class="investor-change ${changeClass}">${changeSymbol} ${Math.abs(investor.change).toFixed(1)}%</div>
                </div>
            `;
        }).join('');
    }

    renderWithdrawRequests() {
        const container = document.getElementById("withdraw-requests-list");
        if (!container) return;

        const requests = this.currentData.withdrawRequests.slice(0, 10);
        
        container.innerHTML = requests.map(request => {
            const shortAddress = request.address.slice(0, 8) + '...' + request.address.slice(-8);
            const timeAgo = this.getTimeAgo(request.timestamp);
            const statusClass = request.status;
            
            return `
                <div class="withdraw-row ${statusClass}">
                    <div class="withdraw-user">${request.name}</div>
                    <div class="withdraw-amount">${request.amount} TON</div>
                    <div class="withdraw-address">${shortAddress}</div>
                    <div class="withdraw-status ${statusClass}">${this.getStatusText(request.status)}</div>
                    <div class="withdraw-time">${timeAgo}</div>
                </div>
            `;
        }).join('');
    }

    renderCommunityStats() {
        const stats = this.currentData.communityStats;
        
        const totalSubscribersEl = document.getElementById("total-subscribers");
        const activeTodayEl = document.getElementById("active-today");
        
        if (totalSubscribersEl) totalSubscribersEl.textContent = stats.totalSubscribers.toLocaleString();
        if (activeTodayEl) activeTodayEl.textContent = `+${stats.activeToday.toLocaleString()}`;
    }

    getTimeAgo(timestamp) {
        const diff = Date.now() - timestamp;
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        
        if (hours > 0) return `${hours}ч ${minutes}м назад`;
        return `${minutes}м назад`;
    }

    getStatusText(status) {
        const statusTexts = {
            'pending': 'Ожидание',
            'processing': 'В процессе', 
            'completed': 'Выполнен'
        };
        return statusTexts[status] || status;
    }

    // Инициализация и отображение начальных данных
    initialize() {
        this.renderTopInvestors();
        this.renderWithdrawRequests();
        this.renderCommunityStats();
        this.startDynamicUpdates();
    }
}

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
let dynamicDataManager = null;

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
            document.getElementById('balance').textContent = Number(data.balance).toFixed(4);
            document.getElementById('invested').textContent = Number(data.invested).toFixed(2);
            document.getElementById('earned').textContent = Number(data.earned).toFixed(4);
            document.getElementById('speed').textContent = data.speed;
            updateWithdrawInfo();
        }
    } catch (e) {
        showNotification('server_sleeping', 'error');
    }
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

            if (qrImg) qrImg.src = data.qr_code || "";
            if (qrAddress) qrAddress.textContent = data.address || "—";
            if (qrComment) qrComment.textContent = data.comment || "—";
            if (paymentUrl) {
                paymentUrl.href = data.payment_url || "#";
                paymentUrl.textContent = data.payment_url || "Открыть в кошельке";
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

// === ПРОВЕРКА ПЛАТЕЖА ===
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
// === КАЛЬКУЛЯТОР ДОХОДНОСТИ (локальный) ===
function calculateProfit() {
    const input = document.getElementById('calc-amount');
    const amount = parseFloat(input?.value) || 0;

    const results = {
        daily: 0,
        weekly: 0,
        monthly: 0,
        yearly: 0,
        bonus: 0
    };

    if (amount >= 1) {
        // Параметры из calculator.py
        const MONTHLY_RATE = 0.25;
        const BASE_MINING_DAYS = 90;
        const BONUS_PERCENT = 0.05;

        // 1. Инвестиционный доход в день
        const investmentDaily = amount * (MONTHLY_RATE / 30);

        // 2. Скорость майнинга: +1% за каждые 40 TON
        const acceleration = Math.floor(amount / 40) * 0.01;
        const miningSpeed = 1 + acceleration;

        // 3. Бесплатный майнинг в день
        const freeMiningDaily = (1 / BASE_MINING_DAYS) * miningSpeed;

        // 4. Общий доход в день
        const totalDaily = investmentDaily + freeMiningDaily;

        // 5. Бонус
        const bonus = amount * BONUS_PERCENT;

        // Рассчитываем периоды
        results.daily = totalDaily;
        results.weekly = totalDaily * 7;
        results.monthly = totalDaily * 30;
        results.yearly = totalDaily * 365;
        results.bonus = bonus;
    }

    // Обновляем интерфейс
    const set = (id, value, fixed = 4) => {
        const el = document.getElementById(id);
        if (el) el.textContent = value.toFixed(fixed) + ' TON';
    };

    set('calc-daily', results.daily, 6);
    set('calc-weekly', results.weekly, 6);
    set('calc-monthly', results.monthly, 4);
    set('calc-yearly', results.yearly, 2);
    document.getElementById('calc-bonus').textContent = '+' + results.bonus.toFixed(2) + ' TON';
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

    // Инициализация динамических данных
    dynamicDataManager = new DynamicDataManager();
    dynamicDataManager.initialize();

    showSection('stats');
    loadUserData();
    setInterval(loadUserData, 30000);

    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) refreshBtn.addEventListener('click', refresh);
});

// === ГЛОБАЛЬНЫЕ ФУНКЦИИ ===
window.showSection = showSection;
window.copyAddress = () => copyToClipboard(document.getElementById('qr-address')?.textContent, "address_copied");
window.copyPaymentUrl = () => copyToClipboard(document.getElementById('payment-url')?.href, "payment_url_copied");
window.withdraw = withdraw;
window.copyLink = copyLink;
window.changeLanguage = changeLanguage;
window.createDeposit = createDeposit;
window.refresh = refresh;
