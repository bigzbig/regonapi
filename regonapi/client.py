import logging
from typing import Optional

from lxml import objectify
from lxml.etree import XMLSyntaxError
from requests import Session
from zeep import Client as ZeepClient
from zeep import Transport

logger = logging.getLogger(__name__)


WSDL = (
    "https://wyszukiwarkaregon.stat.gov.pl/wsBIR/wsdl/UslugaBIRzewnPubl-ver11-prod.wsdl"
)
ENDPOINT = "https://wyszukiwarkaregon.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc"

WSDL_SANDBOX = "https://wyszukiwarkaregontest.stat.gov.pl/wsBIR/wsdl/UslugaBIRzewnPubl-ver11-test.wsdl"
ENDPOINT_SANDBOX = (
    "https://wyszukiwarkaregontest.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc"
)
APIKEY_SANDBOX = "abcde12345abcde12345"


DETAILED_REPORT_NAMES_BY_TYPE = {
    # podmiot osoby fizycznej prowadzącej działalność gospodarczą
    "F": {
        # działalność podlegającą wpisowi do CEIDG
        "1": "BIR11OsFizycznaDzialalnoscCeidg",
        # działalność rolnicza (gospodarstwo rolne, działy specjaln eprodukcji rolnej)
        "2": "BIR11OsFizycznaDzialalnoscRolnicza",
        # działalność inna (komornik, notariusz, agroturystyka – o ile nie wpisane do CEIDG)
        "3": "BIR11OsFizycznaDzialalnoscPozostala",
        # działalność skreślona z rejestru REGON przed datą 08.11.2014 (w poprzednim systemie inform.)
        "4": "BIR11OsFizycznaDzialalnoscSkreslonaDo20141108",
    },
    # jednostka lokalna podmiotu osoby fizycznej
    "LF": "BIR11JednLokalnaOsFizycznej",
    # osoba prawna oraz jednostka organizacyjna niemająca osobowości prawnej
    # ma przypisaną wartość SilosID równą 6 - w dokumentacji opisana jako - wartość techniczna,
    # bez znaczenia merytorycznego; istnieje wyłącznie dla zachowania spójności struktury
    "P": "BIR11OsPrawna",
    # jednostka lokalna osoby prawnej
    "LP": "BIR11JednLokalnaOsPrawnej",
}

PKD_REPORT_TYPE = {
    "F": "PublDaneRaportDzialalnosciFizycznej",
    "P": "PublDaneRaportDzialalnosciPrawnej",
}


class Client(object):

    headers = {}

    def __init__(self, api_key: Optional[str] = None):

        wsdl = WSDL if api_key else WSDL_SANDBOX
        self.endpoint = ENDPOINT if api_key else ENDPOINT_SANDBOX
        self.api_key = api_key or APIKEY_SANDBOX

        transport = Transport(session=Session())
        transport.session.headers = self.headers
        self.client = ZeepClient(wsdl, transport=transport)
        self.service = None

    def _call(self, action: str, *args, **kwargs) -> str:
        if not self.service:
            self.service = self.client.create_service(
                "{http://tempuri.org/}e3", self.endpoint
            )
            self.headers.update({"sid": self._login()})

        service = getattr(self.service, action)
        return service(*args, **kwargs)

    def _login(self) -> str:
        return self._call("Zaloguj", self.api_key)

    def search(
        self,
        *,
        nip: Optional[str] = None,
        regon: Optional[str] = None,
        krs: Optional[str] = None,
    ) -> str:
        if not any([nip, regon, krs]):
            raise AttributeError(
                "At least one parameter (nip, regon, krs) is required."
            )
        if nip:
            search_params = {"Nip": nip}
        elif regon:
            search_params = {"Regon": regon}
        else:
            search_params = {"Krs": krs}
        return self.validate_result(self._call("DaneSzukajPodmioty", search_params))

    def get_full_report(
        self, regon: str, company_type: str, silos_id: Optional[int] = None
    ) -> str:
        report_name = DETAILED_REPORT_NAMES_BY_TYPE.get(company_type)
        if isinstance(report_name, dict):
            report_name = report_name[silos_id]
        return self.validate_result(
            self._call("DanePobierzPelnyRaport", regon, report_name)
        )

    def get_pkd_raport(self, regon: str, company_type: str) -> str:
        report_type = (
            PKD_REPORT_TYPE[company_type]
            if company_type in PKD_REPORT_TYPE
            else PKD_REPORT_TYPE["F"]
        )

        return self.validate_result(
            self._call("DanePobierzPelnyRaport", regon, report_type)
        )

    @staticmethod
    def validate_result(result: str) -> str:
        if not result:
            raise ValueError(f"Empty result - probably problem with authorisation")

        try:
            result_object = objectify.fromstring(result)
        except XMLSyntaxError:
            raise ValueError(f"Unexpected response: {result}")

        if not hasattr(result_object, "dane"):
            raise ValueError(f"Unexpected response: {result}")

        if hasattr(result_object.dane, "ErrorCode"):
            raise ValueError(
                f"code: {result_object.dane.ErrorCode} - {result_object.dane.ErrorMessageEn}"
            )

        return result
