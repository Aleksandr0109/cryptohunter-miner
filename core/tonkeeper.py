# core/tonkeeper.py
from tonsdk.contract.wallet import Wallets, WalletVersionEnum
from tonsdk.utils import to_nano, Address
import aiohttp
import qrcode
from io import BytesIO
import base64
import secrets
import string
from config import TONKEEPER_MNEMONIC, TONKEEPER_API_KEY

class TonkeeperAPI:
    def __init__(self):
        self.mnemonics = TONKEEPER_MNEMONIC.split()
        self.api_key = TONKEEPER_API_KEY
        self.wallet = self._create_wallet()
        self.payment_addresses = {}  # Храним временные адреса для пользователей

    def _create_wallet(self):
        _, _, _, wallet = Wallets.from_mnemonics(self.mnemonics, WalletVersionEnum.v4r2, workchain=0)
        return wallet

    async def get_address(self):
        return self.wallet.address.to_string(is_user_friendly=True, is_bounceable=True, is_test_only=True)

    async def generate_payment_address(self, user_id: int, amount: float = None):
        """Генерирует уникальный платежный адрес для пользователя"""
        try:
            # Создаем комментарий для идентификации платежа
            comment = self._generate_payment_comment(user_id)
            
            # Основной адрес кошелька
            base_address = await self.get_address()
            
            # Формируем адрес с комментарием
            payment_address = f"{base_address}?text={comment}"
            
            # Сохраняем информацию о платеже
            self.payment_addresses[user_id] = {
                'address': base_address,
                'comment': comment,
                'amount': amount,
                'status': 'pending'
            }
            
            return payment_address
            
        except Exception as e:
            print(f"Ошибка генерации платежного адреса: {e}")
            return await self.get_address()  # fallback на основной адрес

    def _generate_payment_comment(self, user_id: int):
        """Генерирует уникальный комментарий для платежа"""
        chars = string.ascii_letters + string.digits
        random_part = ''.join(secrets.choice(chars) for _ in range(8))
        return f"pay_{user_id}_{random_part}"

    def generate_qr_code(self, payment_address: str):
        """Генерирует QR-код для адреса"""
        try:
            # Убираем комментарий для чистого QR-кода (некоторые кошельки не понимают комментарии в QR)
            clean_address = payment_address.split('?')[0]
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(clean_address)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            
            # Конвертируем в base64 для отправки в Telegram
            qr_base64 = base64.b64encode(buffered.getvalue()).decode()
            return qr_base64
            
        except Exception as e:
            print(f"Ошибка генерации QR-кода: {e}")
            return None

    async def check_payment(self, user_id: int):
        """Проверяет поступление платежа для пользователя"""
        try:
            if user_id not in self.payment_addresses:
                return False
                
            payment_info = self.payment_addresses[user_id]
            transactions = await self.get_transactions()
            
            for tx in transactions:
                if (tx.get('in_msg', {}).get('message') == payment_info['comment'] or 
                    self._is_user_transaction(tx, user_id)):
                    payment_info['status'] = 'completed'
                    return True
                    
            return False
            
        except Exception as e:
            print(f"Ошибка проверки платежа: {e}")
            return False

    async def get_transactions(self, limit: int = 10):
        """Получает последние транзакции кошелька"""
        address = await self.get_address()
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://testnet.toncenter.com/api/v3/transactions?address={address}&limit={limit}",
                headers={"X-API-Key": self.api_key}
            ) as resp:
                data = await resp.json()
                return data.get('transactions', [])

    def _is_user_transaction(self, transaction: dict, user_id: int):
        """Определяет принадлежит ли транзакция пользователю"""
        # Дополнительная логика идентификации транзакций
        in_msg = transaction.get('in_msg', {})
        message = in_msg.get('message', '')
        return f"pay_{user_id}_" in message

    async def get_balance(self):
        address = await self.get_address()
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://testnet.toncenter.com/api/v3/addressInformation?address={address}",
                headers={"X-API-Key": self.api_key}
            ) as resp:
                data = await resp.json()
                return int(data["balance"]) / 1e9

    async def send_ton(self, to_address: str, amount_ton: float):
        wallet = self.wallet
        amount_nano = to_nano(amount_ton)
        seqno = await self.get_seqno()

        query = wallet.create_transfer_message(
            to_addr=Address(to_address).to_string(is_user_friendly=True, is_bounceable=True, is_test_only=True),
            amount=amount_nano,
            seqno=seqno
        )

        boc = query["message"].to_boc().hex()

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://testnet.toncenter.com/api/v3/message",
                json={"boc": boc},
                headers={"X-API-Key": self.api_key}
            ) as resp:
                return await resp.json()

    async def get_seqno(self):
        address = await self.get_address()
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://testnet.toncenter.com/api/v3/addressInformation?address={address}",
                headers={"X-API-Key": self.api_key}
            ) as resp:
                data = await resp.json()
                return int(data["seqno"])