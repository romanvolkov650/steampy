import base64

from generated.messages.AddItemsToCart_pb2 import Payload, Items, NavData
from requests import Session

from steampy.utils import login_required, create_cookie


class SteamStore:

    def __init__(self, session: Session) -> None:
        self._session = session
        self._steam_guard = None
        self._session_id = None
        self.was_login_executed = False
        self._access_token = None

    def set_steam_guard(self, steam_guard: dict) -> None:
        self._steam_guard = steam_guard

    def set_session_id(self, session_id: str) -> None:
        self._session_id = session_id

    def set_access_token(self, access_token: str):
        self._access_token = access_token
        self.was_login_executed = True

    @login_required
    def clear_cart(self):
        response = self._session.post(
            "https://api.steampowered.com/IAccountCartService/DeleteCart/v1?access_token="
            + self._access_token
        )
        return response.status_code == 200

    @login_required
    def add_game_to_cart(self, game_id: int):
        msg = Payload(
            country="UA",
            items=Items(packageid=game_id),
            nav_data=NavData(
                domain="store.steampowered.com",
                controller="store-navigation",
                method="",
                sub_method="",
                feature="",
                depth=0,
                country_code="",
                is_client=0,
                curator_data="",
                is_likely_bot=0,
                is_utm=0,
            ),
        )
        payload = {
            "access_token": self._access_token,
            "input_protobuf_encoded": base64.b64encode(msg.SerializeToString()).decode(
                "utf-8"
            ),
        }
        response = self._session.post(
            "https://api.steampowered.com/IAccountCartService/AddItemsToCart/v1",
            params=payload,
        )
        return response.status_code == 200

    @login_required
    def checkout_cart(self):
        transaction_id = self._init_transaction()
        if not transaction_id:
            return False
        self._get_final_price(transaction_id)
        self._finalize_transaction(transaction_id)
        return self._check_transaction_status(transaction_id)

    def _init_transaction(self, country_code: str = "UA") -> str:
        headers = {
            "Referer": "https://checkout.steampowered.com/checkout/?accountcart=1",
            "Origin": "https://checkout.steampowered.com",
        }
        data = {
            "gidShoppingCart": "-1",
            "gidReplayOfTransID": "-1",
            "bUseAccountCart": "1",
            "PaymentMethod": "steamaccount",
            "abortPendingTransactions": "0",
            "bHasCardInfo": "0",
            "CardNumber": "",
            "CardExpirationYear": "",
            "CardExpirationMonth": "",
            "FirstName": "",
            "LastName": "",
            "Address": "",
            "AddressTwo": "",
            "Country": country_code.upper(),
            "City": "",
            "State": "",
            "PostalCode": "",
            "Phone": "",
            "ShippingFirstName": "",
            "ShippingLastName": "",
            "ShippingAddress": "",
            "ShippingAddressTwo": "",
            "ShippingCountry": country_code.upper(),
            "ShippingCity": "",
            "ShippingState": "",
            "ShippingPostalCode": "",
            "ShippingPhone": "",
            "bIsGift": "0",
            "GifteeAccountID": "0",
            "GifteeEmail": "",
            "GifteeName": "",
            "GiftMessage": "",
            "Sentiment": "",
            "Signature": "",
            "ScheduledSendOnDate": "0",
            "BankAccount": "",
            "BankCode": "",
            "BankIBAN": "",
            "BankBIC": "",
            "TPBankID": "",
            "BankAccountID": "",
            "bSaveBillingAddress": "1",
            "gidPaymentID": "",
            "bUseRemainingSteamAccount": "1",
            "bPreAuthOnly": "0",
            "sessionid": self._session_id,
        }
        cookie = create_cookie(
            name="sessionid",
            cookie=self._session_id,
            domain="checkout.steampowered.com",
        )
        self._session.cookies.set(**cookie)

        response = self._session.post(
            "https://checkout.steampowered.com/checkout/inittransaction/",
            data=data,
            headers=headers,
        )
        return response.json()["transid"]

    def _get_final_price(self, transaction_id: str):
        params = {
            "count": 1,
            "transid": transaction_id,
            "purchasetype": "self",
            "microtxnid": -1,
            "cart": -1,
            "gidReplayOfTransID": -1,
        }
        headers = {
            "Referer": "https://checkout.steampowered.com/checkout/?accountcart=1",
        }
        self._session.get(
            "https://checkout.steampowered.com/checkout/getfinalprice/",
            params=params,
            headers=headers,
        )

    def _finalize_transaction(self, transaction_id: str):
        data = {
            "transid": transaction_id,
            "CardCVV2": "",
            "browserInfo": {
                "language": "en-US",
                "javaEnabled": "false",
                "colorDepth": 30,
                "screenHeight": 1080,
                "screenWidth": 1920,
            },
        }
        headers = {
            "Origin": "https://checkout.steampowered.com",
            "Referer": "https://checkout.steampowered.com/checkout/?accountcart=1",
        }
        response = self._session.post(
            "https://checkout.steampowered.com/checkout/finalizetransaction/",
            data=data,
            headers=headers,
        )

    def _check_transaction_status(self, transaction_id: str) -> bool:
        params = {
            "count": 1,
            "transid": transaction_id,
        }
        headers = {
            "Referer": "https://checkout.steampowered.com/checkout/?accountcart=1"
        }
        response = self._session.get(
            "https://checkout.steampowered.com/checkout/transactionstatus/?count=1&transid=283285009399822824",
            params=params,
            headers=headers,
        )
        return response.json()["success"] == 1
