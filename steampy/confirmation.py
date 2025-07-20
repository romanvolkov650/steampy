from __future__ import annotations

import enum
import json
import time
from datetime import datetime
from http import HTTPStatus
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup

from steampy import guard
from steampy.exceptions import ConfirmationExpected
from steampy.login import InvalidCredentials

if TYPE_CHECKING:
    import requests


class ConfirmationType(enum.Enum):
    UNKNOWN = 1
    TRADE = 2
    LISTING = 3
    API_KEY = 4  # TODO find api key value

    @classmethod
    def get(cls, v: int) -> "ConfirmationType":
        try:
            return cls(v)
        except ValueError:
            return cls.UNKNOWN


class Confirmation:
    def __init__(
        self,
        _id: int,
        nonce: str,
        creator_id: int,
        creation_time: datetime,
        _type: ConfirmationType,
        icon: str,
        multi: bool,
        headline: str,
        summary: str,
        warn: str | None,
        asset_ident_code: str | None = None,
    ) -> None:
        self.id = _id
        self.nonce = nonce
        self.creator_id = creator_id
        self.creation_time = creation_time
        self.type = _type
        self.icon = icon
        self.multi = multi
        self.headline = headline
        self.summary = summary
        self.warn = warn
        self.asset_ident_code = asset_ident_code


class Tag(enum.Enum):
    CONF = "conf"
    DETAILS = "details"
    ALLOW = "allow"
    CANCEL = "cancel"


class ConfirmationExecutor:
    CONF_URL = "https://steamcommunity.com/mobileconf"

    def __init__(
        self, identity_secret: str, my_steam_id: str, session: requests.Session
    ) -> None:
        self._my_steam_id = my_steam_id
        self._identity_secret = identity_secret
        self._session = session

    def send_trade_allow_request(self, trade_offer_id: str) -> dict:
        confirmations = self._get_confirmations()
        confirmation = self._select_trade_offer_confirmation(
            confirmations, trade_offer_id
        )
        return self._send_confirmation(confirmation)

    def confirm_sell_listing(self, asset_id: str) -> dict:
        confirmations = self._get_confirmations()
        confirmation = self._select_sell_listing_confirmation(confirmations, asset_id)
        return self._send_confirmation(confirmation)

    def cancel_all(self):
        confirmations = self._get_confirmations()
        for confirmation in confirmations:
            self._send_confirmation(confirmation, tag=Tag.CANCEL)

    def confirm_api_key_request(self, request_id: str) -> dict:
        confirmations = self._get_confirmations()
        confirmation = self._select_api_key_confirmation(confirmations, request_id)
        return self._send_confirmation(confirmation)

    def _send_confirmation(self, confirmation: Confirmation, tag=Tag.ALLOW) -> dict:
        params = self._create_confirmation_params(tag.value)
        params["op"] = tag.value
        params["cid"] = confirmation.id
        params["ck"] = confirmation.nonce
        headers = {"X-Requested-With": "XMLHttpRequest"}
        return self._session.get(
            f"{self.CONF_URL}/ajaxop", params=params, headers=headers
        ).json()

    def _get_confirmations(self) -> list[Confirmation]:
        confirmations = []
        confirmations_page = self._fetch_confirmations_page()
        if confirmations_page.status_code == HTTPStatus.OK:
            confirmations_json = json.loads(confirmations_page.text)
            for conf_data in confirmations_json["conf"]:
                conf = Confirmation(
                    _id=int(conf_data["id"]),
                    nonce=conf_data["nonce"],
                    creator_id=int(conf_data["creator_id"]),
                    creation_time=datetime.fromtimestamp(conf_data["creation_time"]),
                    _type=ConfirmationType.get(conf_data["type"]),
                    icon=conf_data["icon"],
                    multi=conf_data["multi"],
                    headline=conf_data["headline"],
                    summary=conf_data["summary"][0],
                    warn=conf_data["warn"],
                )
                confirmations.append(conf)
            return confirmations
        raise ConfirmationExpected

    def _fetch_confirmations_page(self) -> requests.Response:
        tag = Tag.CONF.value
        params = self._create_confirmation_params(tag)
        headers = {"X-Requested-With": "com.valvesoftware.android.steam.community"}
        response = self._session.get(
            f"{self.CONF_URL}/getlist", params=params, headers=headers
        )
        if (
            "Steam Guard Mobile Authenticator is providing incorrect Steam Guard codes."
            in response.text
        ):
            raise InvalidCredentials("Invalid Steam Guard file")
        return response

    def _fetch_confirmation_details_page(self, confirmation: Confirmation) -> str:
        tag = f"details{confirmation.id}"
        params = self._create_confirmation_params(tag)
        response = self._session.get(
            f"{self.CONF_URL}/details/{confirmation.id}", params=params
        )
        return response.json()["html"]

    def _create_confirmation_params(self, tag_string: str) -> dict:
        timestamp = int(time.time())
        confirmation_key = guard.generate_confirmation_key(
            self._identity_secret, tag_string, timestamp
        )
        android_id = guard.generate_device_id(self._my_steam_id)
        return {
            "p": android_id,
            "a": self._my_steam_id,
            "k": confirmation_key,
            "t": timestamp,
            "m": "android",
            "tag": tag_string,
        }

    def _select_trade_offer_confirmation(
        self, confirmations: list[Confirmation], trade_offer_id: str
    ) -> Confirmation:
        for confirmation in confirmations:
            confirmation_details_page = self._fetch_confirmation_details_page(
                confirmation
            )
            confirmation_id = self._get_confirmation_trade_offer_id(
                confirmation_details_page
            )
            if confirmation_id == trade_offer_id:
                return confirmation
        raise ConfirmationExpected

    def _select_sell_listing_confirmation(
        self, confirmations: list[Confirmation], asset_id: str
    ) -> Confirmation:
        for confirmation in confirmations:
            confirmation_details_page = self._fetch_confirmation_details_page(
                confirmation
            )
            confirmation_id = self._get_confirmation_sell_listing_id(
                confirmation_details_page
            )
            if confirmation_id == asset_id:
                return confirmation
        raise ConfirmationExpected

    @staticmethod
    def _select_api_key_confirmation(
        confirmations: list[Confirmation], request_id: str
    ) -> Confirmation:
        for confirmation in confirmations:
            if str(confirmation.creator_id) == str(request_id):
                return confirmation
        raise ConfirmationExpected

    @staticmethod
    def _get_confirmation_sell_listing_id(confirmation_details_page: str) -> str:
        soup = BeautifulSoup(confirmation_details_page, "html.parser")
        scr_raw = soup.select("script")[2].string.strip()
        scr_raw = scr_raw[scr_raw.index("'confiteminfo', ") + 16 :]
        scr_raw = scr_raw[: scr_raw.index(", UserYou")].replace("\n", "")
        return json.loads(scr_raw)["id"]

    @staticmethod
    def _get_confirmation_trade_offer_id(confirmation_details_page: str) -> str:
        soup = BeautifulSoup(confirmation_details_page, "html.parser")
        full_offer_id = soup.select(".tradeoffer")[0]["id"]
        return full_offer_id.split("_")[1]
