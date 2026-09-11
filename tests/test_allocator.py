import ipaddress

import pytest

from vigilare.core.allocator import (
    alocar_subrede,
    prefixo_necessario,
)


def test_prefixo_para_20_hosts():
    rede_mae = ipaddress.ip_network("172.16.0.0/16")

    prefixo = prefixo_necessario(
        20,
        rede_mae,
    )

    assert prefixo == 27


def test_prefixo_para_50_hosts():
    rede_mae = ipaddress.ip_network("172.16.0.0/16")

    prefixo = prefixo_necessario(
        50,
        rede_mae,
    )

    assert prefixo == 26


def test_alocar_subrede():
    rede_mae = ipaddress.ip_network("172.16.0.0/16")

    subrede = alocar_subrede(
        rede_mae,
        20,
        [],
    )

    assert subrede == ipaddress.ip_network("172.16.0.0/27")


def test_nao_reutilizar_subrede_ocupada():
    rede_mae = ipaddress.ip_network("172.16.0.0/16")

    alocacoes = [
        {
            "subrede": "172.16.0.0/27"
        }
    ]

    subrede = alocar_subrede(
        rede_mae,
        20,
        alocacoes,
    )

    assert subrede == ipaddress.ip_network("172.16.0.32/27")


def test_quantidade_de_hosts_invalida():
    rede_mae = ipaddress.ip_network("172.16.0.0/16")

    with pytest.raises(ValueError):
        prefixo_necessario(
            0,
            rede_mae,
        )
