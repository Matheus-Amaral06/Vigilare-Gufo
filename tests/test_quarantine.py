import ipaddress
from unittest.mock import patch

from vigilare.core.quarantine import (
    calcular_gateway,
    criar_segmento,
    criar_subrede,
    escolher_rede_mae,
    gerar_nome_bridge,
    montar_configuracao,
)


def test_calcular_gateway():
    subrede = ipaddress.ip_network("172.23.0.0/28")

    gateway = calcular_gateway(subrede)

    assert gateway == ipaddress.ip_address("172.23.0.1")


def test_criar_segmento():
    subrede = ipaddress.ip_network("172.23.0.0/28")
    gateway = ipaddress.ip_address("172.23.0.1")

    segmento = criar_segmento(
        nome="teste",
        interface_quarentena="gufo-br0",
        subrede=subrede,
        gateway=gateway,
        internet=True,
    )

    assert segmento.nome == "teste"
    assert segmento.interface == "gufo-br0"
    assert segmento.subrede == subrede
    assert segmento.gateway == gateway
    assert segmento.internet is True
    assert segmento.hosts_disponiveis() == 14


def test_criar_subrede():
    rede_mae = ipaddress.ip_network("172.23.0.0/16")

    subrede = criar_subrede(
        rede_mae,
        10,
        [],
    )

    assert subrede == ipaddress.ip_network(
        "172.23.0.0/28"
    )


def test_criar_subrede_evitar_rede_ocupada():
    rede_mae = ipaddress.ip_network("172.23.0.0/16")

    alocacoes = [
        {
            "subrede": "172.23.0.0/28",
        }
    ]

    subrede = criar_subrede(
        rede_mae,
        10,
        alocacoes,
    )

    assert subrede == ipaddress.ip_network(
        "172.23.0.16/28"
    )


def test_escolher_rede_mae():
    alocacoes = [
        {
            "subrede": "172.16.0.0/28",
        },
        {
            "subrede": "172.17.0.0/28",
        },
    ]

    rede_mae = escolher_rede_mae(
        alocacoes
    )

    assert rede_mae == ipaddress.ip_network(
        "172.18.0.0/16"
    )


def test_gerar_nome_bridge_primeira_quarentena():
    alocacoes = []

    nome = gerar_nome_bridge(
        alocacoes
    )

    assert nome == "gufo-br0"


def test_gerar_nome_bridge_segunda_quarentena():
    alocacoes = [
        {
            "interface": "gufo-br0",
        }
    ]

    nome = gerar_nome_bridge(
        alocacoes
    )

    assert nome == "gufo-br1"


def test_gerar_nome_bridge_terceira_quarentena():
    alocacoes = [
        {
            "interface": "gufo-br0",
        },
        {
            "interface": "gufo-br1",
        },
    ]

    nome = gerar_nome_bridge(
        alocacoes
    )

    assert nome == "gufo-br2"


def test_gerar_nome_bridge_reutiliza_primeiro_indice_livre():
    alocacoes = [
        {
            "interface": "gufo-br0",
        },
        {
            "interface": "gufo-br2",
        },
    ]

    nome = gerar_nome_bridge(
        alocacoes
    )

    assert nome == "gufo-br1"


def test_montar_configuracao():
    alocacoes = []

    with patch(
        "vigilare.core.quarantine.obter_todas_redes_existentes",
        return_value=[],
    ):
        configuracao = montar_configuracao(
            nome="teste",
            num_hosts=10,
            interface_quarentena="gufo-br0",
            interface_saida="enp3s0",
            alocacoes=alocacoes,
            internet=True,
        )

    assert configuracao["nome"] == "teste"
    assert configuracao["interface"] == "gufo-br0"
    assert configuracao["subrede"] == "172.16.0.0/28"
    assert configuracao["gateway"] == "172.16.0.1"
    assert configuracao["hosts_solicitados"] == 10
    assert configuracao["hosts_disponiveis"] == 14
    assert configuracao["internet"] is True
    assert configuracao["dhcp"]["ativo"] is False
    assert configuracao["firewall"] is False
    assert configuracao["nat"] is True
    assert configuracao["isolamento"] is True


def test_montar_configuracao_gera_bridge_automaticamente():
    alocacoes = []

    with patch(
        "vigilare.core.quarantine.obter_todas_redes_existentes",
        return_value=[],
    ):
        configuracao = montar_configuracao(
            nome="teste",
            num_hosts=10,
            interface_quarentena=None,
            interface_saida="enp3s0",
            alocacoes=alocacoes,
            internet=True,
        )

    assert configuracao["interface"] == "gufo-br0"


def test_montar_configuracao_segunda_bridge_automaticamente():
    alocacoes = [
        {
            "interface": "gufo-br0",
            "subrede": "172.16.0.0/28",
        }
    ]

    with patch(
        "vigilare.core.quarantine.obter_todas_redes_existentes",
        return_value=[],
    ):
        configuracao = montar_configuracao(
            nome="teste-2",
            num_hosts=10,
            interface_quarentena=None,
            interface_saida="enp3s0",
            alocacoes=alocacoes,
            internet=True,
        )

    assert configuracao["interface"] == "gufo-br1"


def test_montar_configuracao_sem_internet():
    alocacoes = []

    with patch(
        "vigilare.core.quarantine.obter_todas_redes_existentes",
        return_value=[],
    ):
        configuracao = montar_configuracao(
            nome="teste-sem-internet",
            num_hosts=10,
            interface_quarentena="gufo-br0",
            interface_saida="enp3s0",
            alocacoes=alocacoes,
            internet=False,
        )

    assert configuracao["nome"] == "teste-sem-internet"
    assert configuracao["interface"] == "gufo-br0"
    assert configuracao["internet"] is False
    assert configuracao["nat"] is False
    assert configuracao["firewall"] is False
    assert configuracao["isolamento"] is True
    assert configuracao["dhcp"]["ativo"] is False
