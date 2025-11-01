# core/tonkeeper.py
from tonsdk.contract.wallet import Wallets, WalletVersionEnum
from tonsdk.utils import to_nano, Address
import aiohttp  # ← ИСПРАВЛЕНО
from config import TONKEEPER_MNEMONIC, TONKEEPER_API_KEY  # ← ИСПРАВЛЕНО

class TonkeeperAPI:
    def __init__(self):
        self.mnemonics = TONKEEPER_MNEMONIC.split()
        self.api_key = TONKEEPER_API_KEY
        self.wallet = self._create_wallet()

    def _create_wallet(self):
        _, _, _, wallet = Wallets.from_mnemonics(self.mnemonics, WalletVersionEnum.v4r2, workchain=0)
        return wallet

    async def get_address(self):
        return self.wallet.address.to_string(is_user_friendly=True, is_bounceable=True, is_test_only=True)

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