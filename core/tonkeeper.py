# core/tonkeeper.py — РАБОЧАЯ ВЕРСИЯ
import asyncio
import aiohttp
import qrcode
import secrets
import string
import logging
from datetime import datetime, timedelta
from io import BytesIO
import base64
from tonsdk.contract.wallet import Wallets, WalletVersionEnum
from tonsdk.utils import to_nano, Address
from sqlalchemy import select

from config import TONKEEPER_MNEMONIC, TONKEEPER_API_KEY, TONCENTER_BASE_URL
from core.database import AsyncSessionLocal
from core.models import PendingDeposit

class TonkeeperAPI:
    def __init__(self):
        self.mnemonics = (TONKEEPER_MNEMONIC or "").strip().split()
        self.api_key = TONKEEPER_API_KEY or ""
        self.base_url = TONCENTER_BASE_URL or "https://toncenter.com/api/v3"
        self.api_key_header = {"X-API-Key": self.api_key} if self.api_key else {}
        self.wallet = self._create_wallet()
        logging.info(f"✅ TonkeeperAPI инициализирован, кошелек: {self.wallet.address.to_string() if self.wallet else 'None'}")

    def _create_wallet(self):
        if len(self.mnemonics) != 24:
            logging.error("❌ Неверная мнемоника TON кошелька")
            return None
        try:
            _, _, _, wallet = Wallets.from_mnemonics(
                self.mnemonics, WalletVersionEnum.v4r2, workchain=0
            )
            return wallet
        except Exception as e:
            logging.error(f"❌ Ошибка создания кошелька: {e}")
            return None

    async def get_address(self):
        """Основной адрес кошелька"""
        if not self.wallet:
            return "EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c"
        return self.wallet.address.to_string(is_bounceable=False, is_url_safe=True)

    def _generate_payment_comment(self, user_id: int):
        """Генерация уникального комментария для платежа"""
        chars = string.ascii_letters + string.digits
        random_part = ''.join(secrets.choice(chars) for _ in range(12))
        return f"ref_{user_id}_{random_part}"

    async def create_payment_request(self, user_id: int, amount: float):
        """Создание запроса на оплату с уникальным комментарием"""
        try:
            base_address = await self.get_address()
            comment = self._generate_payment_comment(user_id)
            amount_nano = int(amount * 1e9)
            
            # Сохраняем в базу
            async with AsyncSessionLocal() as db:
                deposit = PendingDeposit(
                    user_id=user_id,
                    amount=amount,
                    comment=comment,
                    address=base_address,
                    expires_at=datetime.utcnow() + timedelta(hours=24)
                )
                db.add(deposit)
                await db.commit()
                await db.refresh(deposit)

            # Формируем URL для оплаты
            payment_url = f"ton://transfer/{base_address}?amount={amount_nano}&text={comment}"
            
            return {
                "url": payment_url,
                "address": base_address,
                "comment": comment,
                "qr_code": self.generate_qr_code(payment_url),
                "deposit_id": deposit.id
            }
        except Exception as e:
            logging.error(f"❌ Ошибка создания платежа: {e}")
            raise

    def generate_qr_code(self, payment_url: str):
        """Генерация QR-кода"""
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(payment_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode()
        except Exception as e:
            logging.error(f"❌ Ошибка генерации QR: {e}")
            return None

    async def check_payment_status(self, user_id: int, deposit_id: int = None):
        """Проверка статуса платежа"""
        try:
            async with AsyncSessionLocal() as db:
                # Ищем pending депозит
                query = select(PendingDeposit).where(
                    PendingDeposit.user_id == user_id,
                    PendingDeposit.status == "pending"
                )
                if deposit_id:
                    query = query.where(PendingDeposit.id == deposit_id)
                
                deposit = (await db.execute(query)).scalar_one_or_none()
                
                if not deposit:
                    return {"status": "not_found"}
                
                if deposit.status == "completed":
                    return {"status": "completed", "amount": float(deposit.amount)}
                
                # Проверяем транзакции
                transactions = await self._get_recent_transactions()
                
                for tx in transactions:
                    if self._is_matching_transaction(tx, deposit.comment, deposit.amount):
                        # Платеж найден!
                        deposit.status = "completed"
                        deposit.completed_at = datetime.utcnow()
                        await db.commit()
                        
                        return {
                            "status": "completed", 
                            "amount": float(deposit.amount),
                            "tx_hash": tx.get("hash")
                        }
                
                # Проверяем просрочку
                if deposit.expires_at < datetime.utcnow():
                    deposit.status = "expired"
                    await db.commit()
                    return {"status": "expired"}
                
                return {"status": "pending"}
                
        except Exception as e:
            logging.error(f"❌ Ошибка проверки платежа: {e}")
            return {"status": "error"}

    async def _get_recent_transactions(self, limit: int = 50):
        """Получение последних транзакций кошелька"""
        try:
            address = await self.get_address()
            url = f"{self.base_url}/transactions"
            params = {
                "address": address,
                "limit": limit,
                "archival": True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.api_key_header) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("transactions", [])
                    else:
                        logging.error(f"TON Center error: {resp.status}")
                        return []
        except Exception as e:
            logging.error(f"❌ Ошибка получения транзакций: {e}")
            return []

    def _is_matching_transaction(self, tx: dict, expected_comment: str, expected_amount: float):
        """Проверяет, подходит ли транзакция под наш депозит"""
        try:
            in_msg = tx.get("in_msg", {})
            
            # Проверяем комментарий
            tx_comment = in_msg.get("message", "")
            if tx_comment != expected_comment:
                return False
            
            # Проверяем сумму (в нанотонах)
            tx_amount = int(in_msg.get("value", 0))
            expected_nano = int(expected_amount * 1e9)
            
            # Допускаем небольшую разницу из-за комиссий
            return tx_amount >= expected_nano * 0.99  # 99% от суммы
            
        except Exception as e:
            logging.error(f"❌ Ошибка проверки транзакции: {e}")
            return False

    async def get_balance(self):
        """Получение баланса кошелька"""
        try:
            address = await self.get_address()
            url = f"{self.base_url}/getAddressInformation"
            params = {"address": address}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.api_key_header) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        balance_nano = int(data.get("balance", 0))
                        return balance_nano / 1e9
                    return 0.0
        except Exception as e:
            logging.error(f"❌ Ошибка получения баланса: {e}")
            return 0.0

# Глобальный инстанс
tonkeeper = TonkeeperAPI()
