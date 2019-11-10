import os

import pytest
from vcr import VCR

from regonapi.api import RegonAPI
from tests.utils import (
    check_structure_base_data,
    check_structure_address,
    check_structure_pkd,
    check_structure_contact,
    check_structure_report_f1,
    check_structure_report_f2,
    check_structure_report_f3,
    check_structure_report_p,
    check_structure_report_lp,
)

vcr = VCR(
    path_transformer=VCR.ensure_suffix(".yaml"),
    cassette_library_dir=os.path.join("tests", "cassettes"),
)


@pytest.fixture
def api():
    return RegonAPI(api_key=None)


def test_required_lookup(api):
    with pytest.raises(
        AttributeError, match=r"At least one parameter \(nip, regon, krs\) is required."
    ):
        api.find_by()


@vcr.use_cassette
def test_not_found(api):
    with pytest.raises(
        ValueError, match=r"No data found for the specified search criteria."
    ):
        api.find_by(nip="1112223344")


@vcr.use_cassette
def test_structure_responses_f1(api):
    for data in api.find_by(nip="8991051697"):
        check_structure_base_data(data)
        address = api.get_address(data)
        check_structure_address(address)
        pkd = api.get_pkd(data)[0]
        check_structure_pkd(pkd)
        details = api.get_full_report(data)
        contact = api.get_contact(details)
        check_structure_contact(contact)
        check_structure_report_f1(details)


@vcr.use_cassette
def test_structure_responses_f2_f3(api):
    for data in api.find_by(nip="8841496742"):
        check_structure_base_data(data)
        address = api.get_address(data)
        check_structure_address(address)
        pkd = api.get_pkd(data)[0]
        check_structure_pkd(pkd)
        details = api.get_full_report(data)
        contact = api.get_contact(details)
        check_structure_contact(contact)
        if data["silos_id"] == "2":
            check_structure_report_f2(details)
        else:
            check_structure_report_f3(details)


@vcr.use_cassette
def test_structure_responses_p(api):
    for data in api.find_by(nip="5170359458"):
        check_structure_base_data(data)
        address = api.get_address(data)
        check_structure_address(address)
        pkd = api.get_pkd(data)[0]
        check_structure_pkd(pkd)
        details = api.get_full_report(data)
        contact = api.get_contact(details)
        check_structure_contact(contact)
        check_structure_report_p(details)


@vcr.use_cassette
def test_structure_responses_lp(api):
    for data in api.find_by(regon="27659249800038"):
        check_structure_base_data(data)
        address = api.get_address(data)
        check_structure_address(address)
        pkd = api.get_pkd(data)[0]
        check_structure_pkd(pkd)
        details = api.get_full_report(data)
        contact = api.get_contact(details)
        check_structure_contact(contact)
        check_structure_report_lp(details)
