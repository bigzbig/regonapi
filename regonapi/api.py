import logging
import re
from typing import Any, Dict, List, Optional

from lxml import objectify
from lxml.objectify import ObjectifiedElement

from .client import Client

logger = logging.getLogger(__name__)


class RegonAPI:
    def __init__(self, api_key: Optional[str] = None):
        self._client = Client(api_key=api_key)

    def _format(self, result: ObjectifiedElement, remove_prefix: bool = False) -> Dict[str, Any]:
        formatted_result = {}
        for field in result.getchildren():
            name = field.tag
            if remove_prefix:
                name = self._remove_prefix(name)
            name = self._underscore(name)
            formatted_result[name] = field.text
        return formatted_result

    def _normalize(self, result: Dict[str, Any], field_map: List) -> Dict[str, Any]:
        normalized_result = {}
        for field, alias, callback in field_map:
            if field not in result:
                logger.warning(f"Missing field {field} in result {result}")
                value = None
            else:
                value = result[field]

            if value is not None and callback:
                value = callback(value)

            normalized_result[alias or field] = value
        return normalized_result

    @staticmethod
    def _remove_prefix(name: str) -> str:
        return name.split("_", 1)[1]

    @staticmethod
    def _underscore(word: str) -> str:
        """
        Make an underscored, lowercase form from the expression in the string.

        Instead of this method you can use 'underscore' from the inflection library,
        but I didn't want to add a new requirement
        """
        word = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", word)
        word = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", word)
        word = word.replace("-", "_")
        return word.lower()

    def find_by(self, *, nip: str = None, regon: str = None, krs: str = None) -> List[Dict[str, Any]]:
        field_map = [
            ("data_zakonczenia_dzialalnosci", None, None),
            ("gmina", None, None),
            ("kod_pocztowy", None, None),
            ("miejscowosc", None, None),
            ("nazwa", None, None),
            ("nip", None, None),
            ("nr_lokalu", None, None),
            ("nr_nieruchomosci", None, None),
            ("powiat", None, None),
            ("regon", None, None),
            ("silos_id", None, None),
            ("status_nip", None, None),
            ("typ", None, None),
            ("ulica", None, None),
            ("wojewodztwo", None, None),
        ]
        result = self._client.search(nip=nip, regon=regon, krs=krs)
        # In this case the normalization was added only because the API sandbox returns a different data structure
        # for endpoint 'DaneSzukajPodmioty' than the production version. The 'Ulica' field is missing.
        return [self._normalize(self._format(item), field_map) for item in objectify.fromstring(result).dane]

    def get_full_report(self, company_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            result = self._client.get_full_report(
                regon=company_data["regon"], company_type=company_data["typ"], silos_id=company_data["silos_id"]
            )
        except KeyError:
            raise ValueError("The company_data parameter should be single item of result of method 'find_by'")
        return self._format(objectify.fromstring(result).dane, remove_prefix=True)

    def get_pkd(self, company_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        field_map = [
            ("pkd_kod", "kod", str),
            ("pkd_nazwa", "nazwa", str),
            ("pkd_przewazajace", "przewazajace", lambda v: bool(int(v))),
        ]
        try:
            result = self._client.get_pkd_raport(regon=company_data["regon"], company_type=company_data["typ"])
        except KeyError:
            raise ValueError("The company_data parameter should be single item of result of method 'find_by'")

        return [
            self._normalize(self._format(item, remove_prefix=True), field_map=field_map)
            for item in objectify.fromstring(result).dane
        ]

    def get_address(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            address = f"{company_data['ulica']} {company_data['nr_nieruchomosci']}"
            if company_data["nr_lokalu"]:
                address += f"/{company_data['nr_lokalu']}"

            return {
                "ulica": company_data["ulica"],
                "nr_nieruchomosci": company_data["nr_nieruchomosci"],
                "nr_lokalu": company_data["nr_lokalu"],
                "adres": address,
                "kod_pocztowy": company_data["kod_pocztowy"],
                "miejscowosc": company_data["miejscowosc"],
                "gmina": company_data["gmina"],
                "powiat": company_data["powiat"],
                "wojewodztwo": company_data["wojewodztwo"],
            }
        except KeyError:
            raise ValueError("The company_data parameter should be single item of result of method 'find_by'")

    def get_contact(self, full_report_data: Dict[str, Any]) -> Dict[str, Any]:
        if not ("regon9" in full_report_data or "regon14" in full_report_data):
            raise ValueError(
                "The full_report_data parameter should be single item of result of method 'get_full_report'"
            )
        return {
            "nr_telefonu": full_report_data.get("numer_telefonu"),
            "nr_wewnetrzny_telefonu": full_report_data.get("numer_wewnetrzny_telefonu"),
            "nr_faksu": full_report_data.get("numer_faksu"),
            "email": full_report_data.get("adres_email"),
            "www": full_report_data.get("adres_stronyinternetowej"),
        }
