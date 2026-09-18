from unittest.mock import patch

from vigilare.services.routing import (
    configurar_routing,
    existe_quarentena_com_internet,
)


def test_existe_quarentena_com_internet():
    alocacoes = [
        {
            "nome": "quarentena-sem-internet",
            "internet": False,
        },
        {
            "nome": "quarentena-com-internet",
            "internet": True,
        },
    ]

    assert existe_quarentena_com_internet(
        alocacoes
    ) is True


def test_nao_existe_quarentena_com_internet():
    alocacoes = [
        {
            "nome": "quarentena-1",
            "internet": False,
        },
        {
            "nome": "quarentena-2",
            "internet": False,
        },
    ]

    assert existe_quarentena_com_internet(
        alocacoes
    ) is False


def test_routing_habilita_forward_se_alguma_quarentena_tem_internet():
    alocacoes = [
        {
            "nome": "quarentena-sem-internet",
            "internet": False,
        },
        {
            "nome": "quarentena-com-internet",
            "internet": True,
        },
    ]

    with (
        patch(
            "vigilare.services.routing.habilitar_ipv4_forward"
        ) as mock_habilitar,
        patch(
            "vigilare.services.routing.desabilitar_ipv4_forward"
        ) as mock_desabilitar,
    ):
        resultado = configurar_routing(
            alocacoes
        )

    assert resultado is True
    mock_habilitar.assert_called_once()
    mock_desabilitar.assert_not_called()


def test_routing_desabilita_forward_se_nenhuma_tem_internet():
    alocacoes = [
        {
            "nome": "quarentena-1",
            "internet": False,
        },
        {
            "nome": "quarentena-2",
            "internet": False,
        },
    ]

    with (
        patch(
            "vigilare.services.routing.habilitar_ipv4_forward"
        ) as mock_habilitar,
        patch(
            "vigilare.services.routing.desabilitar_ipv4_forward"
        ) as mock_desabilitar,
    ):
        resultado = configurar_routing(
            alocacoes
        )

    assert resultado is False
    mock_habilitar.assert_not_called()
    mock_desabilitar.assert_called_once()


def test_routing_sem_quarentenas_desabilita_forward():
    with (
        patch(
            "vigilare.services.routing.habilitar_ipv4_forward"
        ) as mock_habilitar,
        patch(
            "vigilare.services.routing.desabilitar_ipv4_forward"
        ) as mock_desabilitar,
    ):
        resultado = configurar_routing([])

    assert resultado is False
    mock_habilitar.assert_not_called()
    mock_desabilitar.assert_called_once()
