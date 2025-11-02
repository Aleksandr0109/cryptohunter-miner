# core/tonkeeper.py — v3.0: MAINNET + ЗАЩИТА + QR + ПЛАТЕЖИ
from tonsdk.contract.wallet import Wallets, WalletVersionEnum
from tonsdk.utils import to_nano, Address
import aiohttp
import qrcode
from io import BytesIO
import base64
import secrets
import string
import logging
from config import (
    TONKEEPER_MNEMONIC, TONKEEPER_API_KEY,
    TONCENTER_BASE_URL, TONCENTER_API_KEY
)

class TonkeeperAPI:
    def __init__(self):
        self.mnemonics = (TONKEEPER_MNEMONIC or "").strip().split()
        self.api_key = TONKEEPER_API_KEY or ""
        self.base_url = TONCENTER_BASE_URL or "https://toncenter.com/api/v3"
        self.api_key_header = {"X-API-Key": self.api_key} if self.api_key else {}
        self.wallet = self._create_wallet()
        self.payment_addresses = {}  # user_id -> payment info

    def _create_wallet(self):
        if len(self.mnemonics) != 24:
            logging.warning("TON: Мнемоника не 24 слова или пуста → кошелёк отключён")
            return None
        try:
            _, _, _, wallet = Wallets.from_mnemonics(
                self.mnemonics, WalletVersionEnum.v4r2, workchain=0
            )
            addr = wallet.address.to_string(True, True, False)  # mainnet
            logging.info(f"TON Wallet создан: {addr}")
            return wallet
        except Exception as e:
            logging.error(f"Ошибка создания TON кошелька: {e}")
            return None

    async def get_address(self):
        if not self.wallet:
            return "EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c"  # заглушка
        return self.wallet.address.to_string(True, True, False)  # mainnet

    async def generate_payment_address(self, user_id: int, amount: float = None):
        """Генерирует платежный адрес с комментарием"""
        if not self.wallet:
            return await self.get_address()

        try:
            comment = self._generate_payment_comment(user_id)
            base_address = await self.get_address()
            payment_url = f"{base_address}?amount={int(amount * 1e9) if amount else ''}&text={comment}".strip("&")
            
            self.payment_addresses[user_id] = {
                'address': base_address,
                'comment': comment,
                'amount': amount,
                'status': 'pending'
            }
            return payment_url
        except Exception as e:
            logging.error(f"Ошибка генерации адреса: {e}")
            return await self.get_address()

    def _generate_payment_comment(self, user_id: int):
        chars = string.ascii_letters + string.digits
        rand = ''.join(secrets.choice(chars) for _ in range(8))
        return f"pay_{user_id}_{rand}"

    def generate_qr_code(self, payment_address: str):
        """Генерирует QR-код (только адрес, без ?text)"""
        try:
            clean_address = payment_address.split('?')[0]
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(clean_address)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode()
        except Exception as e:
            logging.error(f"Ошибка QR: {e}")
            return None

    async def check_payment(self, user_id: int):
        """Проверяет, пришёл ли платёж"""
        if user_id not in self.payment_addresses or not self.wallet:
            return False

        payment = self.payment_addresses[user_id]
        try:
            transactions = await self.get_transactions()
            for tx in transactions:
                msg = tx.get('in_msg', {})
                if (msg.get('message') == payment['comment'] or
                    self._is_user_transaction(tx, user_id)):
                    payment['status'] = 'completed'
                    return True
            return False
        except Exception as e:
            logging.error(f"Ошибка проверки платежа: {e}")
            return False

    async def get_transactions(self, limit: int = 10):
        """Получает транзакции с TON Center"""
        address = await self.get_address()
        url = f"{self.base_url}/transactions?address={address}&limit={limit}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.api_key_header) as resp:
                data = await resp.json()
                return data.get('transactions', [])

    def _is_user_transaction(self, tx: dict, user_id: int):
        msg = tx.get('in_msg', {}).get('message', '')
        return f"pay_{user_id}_" in msg

    async def get_balance(self):
        """Баланс в TON"""
        if not self.wallet:
            return 0.0
        address = await self.get_address()
        url = f"{self.base_url}/addressInformation?address={address}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.api_key_header) as resp:
                data = await resp.json()
                return int(data.get("balance", 0)) / 1e9

    async def send_ton(self, to_address: str, amount_ton: float):
        """Отправка TON"""
        if not self.wallet:
            return {"error": "Wallet not initialized"}
        try:
            amount_nano = to_nano(amount_ton)
            seqno = await self.get_seqno()
            query = self.wallet.create_transfer_message(
                to_addr=Address(to_address).to_string(True, True, False),
                amount=amount_nano,
                seqno=seqno
            )
            boc = query["message"].to_boc().hex()
            url = f"{self.base_url}/message"
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json={"boc": boc}, headers=self.api_key_header) as resp:
                    return await resp.json()
        except Exception as e:
            logging.error(f"Ошибка отправки: {e}")
            return {"error": str(e)}

    async def get_seqno(self):
        """Получить seqno"""
        address = await self.get_address()
        url = f"{self.base_url}/addressInformation?address={address}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.api_key_header) as resp:
                data = await resp.json()
                return int(data.get("seqno", 0))
