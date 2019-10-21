regonapi
========

Client of the `'API REGON' <https://api.stat.gov.pl/Home/RegonApi>`_ (v BIR1.1) - internet database of the GUS - Główny Urząd Statystyczny (ang. The Central Statistical Office). Enables searching for detailed information about Polish companies based on selected identifiers, such as:

- NIP - Tax ID,
- REGON - National Business Registry Number
- KRS - National Court Register Number

`GUS (Główny Urząd Statystyczny) REGON <https://wyszukiwarkaregon.stat.gov.pl/appBIR/index.aspx>`_ Internet Database client which allows to get detailed information about company based on NIP, Regon or KRS number.

Requirements
------------

- python >= 3.6
- zeep
- lxml

It requires an **API key** to obtainable as described on the help page `Registration <https://api.stat.gov.pl/Home/RegonApi>`_.

*Note:* The client can be tested in sandbox mode without entering the API key. In this case, the information returned by API will be partially anonymized.


Quickstart
----------

Installation
~~~~~~~~~~~~~

Install the package via ``pip`` **(not yet)**:

.. code-block:: bash

    pip install regonapi

Install the package from github

.. code-block:: bash

    pip install git+https://github.com/bigzbig/regonapi@master

or using `requirements.txt` file

.. code-block:: bash

    -e git+git://github.com/bigzbig/regonapi@master#egg=regonapi

Usage
-----

API initialization
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from regonapi import RegonAPI

    api = RegonAPI(api_key='my_api_key')

If you don't specify the API key, you'll work in sandbox mode

.. code-block:: python

    from regonapi import RegonAPI

    api = RegonAPI()


Returns the base company data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use `nip`, `regon` or `krs` as a lookup parameter.

.. code-block:: python

    api.find_by(nip='0684711351'):
    

output

*Note:* Even for a single NIP or REGON number, the method can return more than one entry (maximum three)

.. code-block::

    [
        {
            "data_zakonczenia_dzialalnosci": None,
            "gmina": "M. Rzeszów",
            "kod_pocztowy": "35-617",
            "miejscowosc": "Rzeszów",
            "nazwa": "Zmyślona Firma",
            "nip": "0684711351",
            "nr_lokalu": "4",
            "nr_nieruchomosci": "39",
            "powiat": "m. Rzeszów",
            "regon": "156073624",
            "silos_id": "1",
            "status_nip": None,
            "typ": "F",
            "ulica": "ul. Zmyślona",
            "wojewodztwo": "PODKARPACKIE",
        },
        # ... can be more
    ]

Returns PKD codes
~~~~~~~~~~~~~~~~~

.. code-block:: python

    api.get_pkd(nip='0684711351')

output

.. code-block::

    [
        {
            "kod": "6311Z",
            "nazwa": "PRZETWARZANIE DANYCH; ZARZĄDZANIE STRONAMI INTERNETOWYMI I PODOBNA DZIAŁALNOŚĆ",
            "przewazajace": False,
        },
        {
            "kod": "6202Z",
            "nazwa": "DZIAŁALNOŚĆ ZWIĄZANA Z DORADZTWEM W ZAKRESIE INFORMATYKI",
            "przewazajace": False,
        },
        {
            "kod": "6201Z",
            "nazwa": "DZIAŁALNOŚĆ ZWIĄZANA Z OPROGRAMOWANIEM",
            "przewazajace": True
        },
        # ... more
    ]

Returns full report
~~~~~~~~~~~~~~~~~~~ 

The kind of report depends on the type of company. The type of company and other data necessary to get the full report are returned by the previously presented **find_by** method.


.. code-block:: python

    data = api.find_by(nip='0684711351')
    api.get_full_report(data[0])


output

*Note:* Output depends on the type of report and is not normalized

.. code-block::

    
    {
        "ad_siedz_kod_pocztowy": "35617",
        "ad_siedz_kraj_nazwa": "POLSKA",
        "ad_siedz_kraj_symbol": "PL",
        "ad_siedz_miejscowosc_nazwa": "Rzeszów",
        "ad_siedz_miejscowosc_symbol": "0974133",
        "ad_siedz_nietypowe_miejsce_lokalizacji": None,
        "ad_siedz_numer_lokalu": "4",
        "ad_siedz_numer_nieruchomosci": "39",
        "ad_siedz_ulica_nazwa": "ul. Zmyślona",
        "ad_siedz_ulica_symbol": "24490",
        "ad_siedz_wojewodztwo_nazwa": "PODKARPACKIE",
        "ad_siedz_wojewodztwo_symbol": "18",
        "adres_email": "office@example.com",
        "adres_stronyinternetowej": "www.example.com",
        "data_orzeczenia_o_upadlosci": None,
        "data_powstania": "2016-07-08",
        "data_rozpoczecia_dzialalnosci": "2016-07-11",
        "data_zaistnienia_zmiany_dzialalnosci": "2019-10-02",
        "data_zakonczenia_dzialalnosci": None,
        "data_zawieszenia_dzialalnosci": None,
        "nazwa": "Zmyślona Firma",   
        "nie_podjeto_dzialalnosci": "false",
        "numer_faksu": None,
        "numer_telefonu": None, 
        "numer_wewnetrzny_telefonu": None,
        "organ_rejestrowy_nazwa": "MINISTER PRZEDSIĘBIORCZOŚCI I TECHNOLOGII",
        "organ_rejestrowy_symbol": "121000000",
        "rodzaj_rejestru_nazwa": "CENTRALNA EWIDENCJA I INFORMACJA O DZIAŁALNOŚCI GOSPODARCZEJ",
        "rodzaj_rejestru_symbol": "151",
        # ... and many more
    }
    

Retrives address from basic data (helper)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    data = api.find_by(nip='0684711351')
    address = api.get_address(data[0])

output

.. code-block::

    {
        "adres": "ul. Zmyślona 39/4",
        "gmina": "M. Rzeszów",
        "kod_pocztowy": "35-617",
        "miejscowosc": "Rzeszów",
        "nr_lokalu": "4",
        "nr_nieruchomosci": "39",
        "powiat": "m. Rzeszów",
        "ulica": "ul. Zmyślona",
        "wojewodztwo": "PODKARPACKIE",
    }

Retrives contact data from full report (helper)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The method not only extracts contact details, but also normalizes field names. If the given field is missing in the full report, it returns the field with the value `None`.

.. code-block:: python

    data = api.find_by(nip='0684711351')
    details = api.get_full_report(data[0])
    contact = api.get_contact(details)

output

.. code-block::

    {
        "email": "office@example.com",
        "nr_faksu": None,
        "nr_telefonu": None,
        "nr_wewnetrzny_telefonu": None,
        "www": "www.example.com",
    }
