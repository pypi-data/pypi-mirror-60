import datetime
import random
import re
import time
from math import ceil
from typing import Optional

import pytz
from bs4 import BeautifulSoup

from .client import Client
from .exceptions import EmptyFile, StpException

LOCAL_FORMAT = '%d/%m/%Y'


def random_gen() -> str:
    return str(random.randint(10 ** 15, 10 ** 16 - 1))


def remove_header(data: str) -> str:
    if data != '':
        return re.split('\n', data, 1)[1]
    return data


def get_today() -> datetime:
    utc_moment_naive = datetime.datetime.utcnow()
    utc_moment = utc_moment_naive.replace(tzinfo=pytz.utc)
    local_now = utc_moment.astimezone(pytz.timezone('America/Mexico_City'))
    return local_now.replace(tzinfo=None)


def validate_date(date: str):
    if date:
        try:
            date = datetime.datetime.strptime(date, LOCAL_FORMAT)
            now = get_today()
            if date > now:
                raise ValueError('Date cannot be greater than today')
        except ValueError:
            raise ValueError('Incorrect format date')


def verify_response(data: str, eval_empty: bool):
    if eval_empty and data == '':
        raise EmptyFile('The transaction file obtained is empty')

    if data and data[:2] != 'id':
        raise StpException(
            'An error has occurred obtaining the transaction file'
        )


def extract(
    from_: str, to: str, delay: int, days: Optional[int] = None
) -> dict:
    current_day = False
    now = get_today()
    if not from_ and days and to:
        to_date = datetime.datetime.strptime(to, LOCAL_FORMAT)
        from_date = to_date - datetime.timedelta(days=days)
        from_ = from_date.strftime(LOCAL_FORMAT)
    elif not from_ and not to and not days:
        days = 1
    elif from_ and days and not to:
        from_date = datetime.datetime.strptime(from_, LOCAL_FORMAT)
        to_date = from_date + datetime.timedelta(days=days)
        if now < to_date:
            to = now.strftime(LOCAL_FORMAT)
        else:
            to = to_date.strftime(LOCAL_FORMAT)

    validate_date(from_)
    validate_date(to)
    if not from_ and to:
        raise ValueError(
            'You cannot leave the "from" param in '
            'blank when set the "to" param'
        )
    elif from_ and not to:
        start_date = from_
        now = get_today()
        final_date = now.strftime(LOCAL_FORMAT)
    elif not from_ and not to:
        now = get_today()
        final_date = now.strftime(LOCAL_FORMAT)
        start_date = now - datetime.timedelta(days=days)
        start_date = start_date.strftime(LOCAL_FORMAT)
    else:
        start_date = from_
        final_date = to

    if days == 1 and not from_ and not to:
        current_day = True

    client = Client()

    # Sent Orders
    client.get(
        f'?wicket:interface=:2:mainBorder:menu:panel:menuSpei:panel:men'
        f'uConsultaOrdenes:tabs-container:tabs:1:link:'
        f'{client.interface}:ILinkListener::'
    )

    if not current_day:
        # Setting dates
        client.post(
            f'?wicket:interface=:2:mainBorder:menu:panel:menuSpei:panel:men'
            f'uConsultaOrdenes:panel:commonPanelBorder:enviadasPanel:histor'
            f'icosForm:btnBuscar:{client.interface}:IActivePageBehaviorList'
            f'ener:0:&wicket:ignoreIfNotActive=true&random=0.{random_gen()}',
            {
                'fechaInicialField:efDateTextField': start_date,
                'fechaFinalField:efDateTextField': final_date,
            },
        )

        # aux request
        client.get(
            f'?wicket:interface=:2:mainBorder:menu:panel:menuSpei:panel:men'
            f'uConsultaOrdenes:panel:commonPanelBorder:enviadasPanel:histor'
            f'icosForm:panelInferior:filter-form:dataTable:topToolbars:2:to'
            f'olbar:tableDataCell:exportTextLink:{client.interface}:IBehavi'
            f'orListener:0:-1&ramdom=0.{random_gen()}',
            increment_interface=False,
        )

        # Download request
        time.sleep(delay)
        response = client.get(
            f'?wicket:interface=:2:mainBorder:menu:panel:menuSpei:panel:men'
            f'uConsultaOrdenes:panel:commonPanelBorder:enviadasPanel:histor'
            f'icosForm:panelInferior:filter-form:dataTable:topToolbars:2:to'
            f'olbar:tableDataCell:hiddenExportTextLink:'
            f'{client.interface}:ILinkListener::'
        )

        verify_response(response, True)
        transactions = response

        # Received Orders
        client.get(
            f'?wicket:interface=:2:mainBorder:menu:panel:menuSpei:panel:men'
            f'uConsultaOrdenes:tabs-container:tabs:2:link:{client.interface}'
            f':ILinkListener::'
        )

        # Setting dates
        client.post(
            f'?wicket:interface=:2:mainBorder:menu:panel:menuSpei:panel:menu'
            f'ConsultaOrdenes:panel:commonPanelBorder:recibidasPanel:histori'
            f'cosForm:btnBuscar:{client.interface}:IActivePageBehaviorListen'
            f'er:0:&wicket:ignoreIfNotActive=true&random=0.{random_gen()}',
            {
                'fechaInicialField:efDateTextField': start_date,
                'fechaFinalField:efDateTextField': final_date,
            },
        )

        client.get(
            f'?wicket:interface=:2:mainBorder:menu:panel:menuSpei:panel:men'
            f'uConsultaOrdenes:panel:commonPanelBorder:recibidasPanel:histo'
            f'ricosForm:panelInferior:filter-form:dataTable:topToolbars:2:t'
            f'oolbar:tableDataCell:exportTextLink:{client.interface}:IBehav'
            f'iorListener:0:-1&random=0.{random_gen()}',
            increment_interface=False,
        )

        # Download request
        time.sleep(delay)
        response = client.get(
            f'?wicket:interface=:2:mainBorder:menu:panel:menuSpei:panel:men'
            f'uConsultaOrdenes:panel:commonPanelBorder:recibidasPanel:histo'
            f'ricosForm:panelInferior:filter-form:dataTable:topToolbars:2:t'
            f'oolbar:tableDataCell:hiddenExportTextLink:{client.interface}:'
            f'ILinkListener::'
        )

        verify_response(response, False)
        transactions += remove_header(response)
    else:
        client.post(
            f'?wicket:interface=:2:mainBorder:menu:panel:menuSpei:panel:men'
            f'uConsultaOrdenes:panel:commonPanelBorder:enviadasPanel:histor'
            f'icosForm:btnBuscar:{client.interface}:IActivePageBehaviorList'
            f'ener:0:&wicket:ignoreIfNotActive=true&random=0.{random_gen()}',
            dict(historicoActualBox='on'),
        )

        client.get(
            f'?wicket:interface=:2:mainBorder:menu:panel:menuSpei:panel:men'
            f'uConsultaOrdenes:panel:commonPanelBorder:enviadasPanel:histor'
            f'icosForm:panelInferior:filter-form:dataTable:topToolbars:2:to'
            f'olbar:tableDataCell:exportTextLink:{client.interface}:IBehavi'
            f'orListener:0:-1&ramdom=0.{random_gen()}',
            increment_interface=False,
        )

        time.sleep(delay)
        response = client.get(
            f'?wicket:interface=:2:mainBorder:menu:panel:menuSpei:panel:men'
            f'uConsultaOrdenes:panel:commonPanelBorder:enviadasPanel:histor'
            f'icosForm:panelInferior:filter-form:dataTable:topToolbars:2:to'
            f'olbar:tableDataCell:hiddenExportTextLink:'
            f'{client.interface}:ILinkListener::'
        )

        verify_response(response, False)
        transactions = response

        # Received Orders
        client.get(
            f'?wicket:interface=:2:mainBorder:menu:panel:menuSpei:panel:men'
            f'uConsultaOrdenes:tabs-container:tabs:2:link:{client.interface}'
            f':ILinkListener::'
        )

        client.post(
            f'?wicket:interface=:2:mainBorder:menu:panel:menuSpei:panel:men'
            f'uConsultaOrdenes:panel:commonPanelBorder:recibidasPanel:histor'
            f'icosForm:btnBuscar:{client.interface}:IActivePageBehaviorList'
            f'ener:0:&wicket:ignoreIfNotActive=true&random=0.{random_gen()}',
            dict(historicoActualBox='on'),
        )

        client.get(
            f'?wicket:interface=:2:mainBorder:menu:panel:menuSpei:panel:men'
            f'uConsultaOrdenes:panel:commonPanelBorder:recibidasPanel:histor'
            f'icosForm:panelInferior:filter-form:dataTable:topToolbars:2:to'
            f'olbar:tableDataCell:exportTextLink:{client.interface}:IBehavi'
            f'orListener:0:-1&ramdom=0.{random_gen()}',
            increment_interface=False,
        )

        time.sleep(delay)
        response = client.get(
            f'?wicket:interface=:2:mainBorder:menu:panel:menuSpei:panel:men'
            f'uConsultaOrdenes:panel:commonPanelBorder:recibidasPanel:histor'
            f'icosForm:panelInferior:filter-form:dataTable:topToolbars:2:to'
            f'olbar:tableDataCell:hiddenExportTextLink:'
            f'{client.interface}:ILinkListener::'
        )

        verify_response(response, False)
        transactions += remove_header(response)

    # Get Balance
    client.get(
        f'?wicket:interface=:2:mainBorder:menu:panel:menuSpei:tabs-container:'
        f'tabs:7:link:{client.interface}:ILinkListener::'
    )
    time.sleep(2)
    response = client.get(
        f'?wicket:interface=:2:mainBorder:menu:panel:menuSpei:panel:menuCuent'
        f'as:tabs-container:tabs:1:link:{client.interface}:ILinkListener::'
    )

    soup = BeautifulSoup(response, features='html.parser')
    text = soup.get_text().replace('\n', '')
    start = re.search('Saldo Disponible:', text).end()
    end = re.search('Ordenes Recibidas', text).start()
    balance_float = text[start:end].replace(',', '')
    balance = ceil(float(balance_float) * 100)

    client.get(
        f'?wicket:interface=:2:mainBorder:menu:panel:menuSpei:tabs-container:'
        f'tabs:5:link:{client.interface}:ILinkListener::'
    )
    response = dict(transactions=transactions, balance=balance)
    return response
