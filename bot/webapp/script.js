// bot/webapp/script.js — ФИНАЛЬНЫЙ
const tg = window.Telegram?.WebApp;

if (!tg) {
  document.body.innerHTML = "<h1 style='color:red; text-align:center'>Ошибка: Открой через Telegram!</h1>";
} else {
  tg.ready();
  tg.expand();

  let userData = {};

  function showSection(id) {
    document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
    document.getElementById(id).style.display = 'block';
    if (id === 'stats') loadUserData();
  }

  async function loadUserData() {
    if (!tg.initData) {
      document.getElementById('balance').textContent = "Нет данных";
      return;
    }
    try {
      const res = await fetch('/api/user', {
        method: 'POST',
        headers: { 'X-Telegram-WebApp-Init-Data': tg.initData }
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      userData = await res.json();

      document.getElementById('balance').textContent = userData.balance.toFixed(4);
      document.getElementById('invested').textContent = userData.invested;
      document.getElementById('earned').textContent = userData.earned;
      document.getElementById('speed').textContent = userData.speed;
      document.getElementById('ref-link').textContent = `https://t.me/cruptos023bot?start=${userData.user_id}`;
    } catch (e) {
      console.error(e);
      document.getElementById('balance').textContent = "Ошибка";
    }
  }

  window.calculate = async function() {
    const amount = parseFloat(document.getElementById('calc-amount').value);
    if (!amount || amount < 1) return tg.showAlert('Минимум 1 TON');

    const res = await fetch('/api/calc', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount })
    });
    const data = await res.json();

    document.getElementById('calc-result').innerHTML = `
      <p>День: <b>${data.daily.toFixed(4)}</b> TON</p>
      <p>Месяц: <b>${data.monthly.toFixed(4)}</b> TON</p>
      <p>Год: <b>${data.yearly.toFixed(4)}</b> TON</p>
    `;
  };

  window.generateQR = async function() {
    const amount = parseFloat(document.getElementById('invest-amount').value);
    if (!amount || amount < 1) return tg.showAlert('Минимум 1 TON');

    const res = await fetch('/api/qr', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount })
    });
    const data = await res.json();

    const canvas = document.getElementById('qr-canvas');
    document.getElementById('qr-container').style.display = 'block';
    QRCode.toCanvas(canvas, data.url, { width: 200 });
  };

  window.withdraw = async function() {
    const address = document.getElementById('withdraw-address').value.trim();
    if (!address.startsWith('kQ')) return tg.showAlert('Адрес должен начинаться с kQ');

    const res = await fetch('/api/withdraw', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ address })
    });
    const data = await res.json();
    document.getElementById('withdraw-status').textContent = data.message;
  };

  window.copyLink = function() {
    const link = document.getElementById('ref-link').textContent;
    navigator.clipboard.writeText(link).then(() => {
      tg.showPopup({ message: "Ссылка скопирована!" });
    });
  };

  // === СТАРТ ===
  loadUserData();
  showSection('stats');
}