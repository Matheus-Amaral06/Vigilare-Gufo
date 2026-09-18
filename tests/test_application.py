import ipaddress
from unittest.mock import patch

import pytest


def test_aplicar_configuracao():
    configuracao = {
        "nome": "teste",
        "interface": "gufo-br0",
        "interface_saida": "enp3s0",
        "subrede": "172.23.0.0/28",
        "gateway": "172.23.0.1",
        "internet": True,
        "dhcp": {
            "ativo": False,
        },
    }

    resultado_bridge = {
        "bridge": "gufo-br0",
        "bridge_criada": True,
        "gateway": "172.23.0.1",
    }

    with (
        patch(
            "vigilare.core.application.ipv4_forward_ativo",
            return_value=False,
        ),
        patch(
            "vigilare.core.application.criar_bridge_quarentena",
            return_value=resultado_bridge,
        ) as mock_bridge,
        patch(
            "vigilare.core.application.configurar_routing",
        ) as mock_routing,
        patch(
            "vigilare.core.application.salvar_configuracao_dnsmasq",
        ) as mock_dnsmasq,
        patch(
            "vigilare.core.application.ativar_dhcp",
        ) as mock_dhcp,
        patch(
            "vigilare.core.application.configurar_firewall",
        ) as mock_firewall,
        patch(
            "vigilare.core.application.remover_bridge",
        ) as mock_remover_bridge,
        patch(
            "vigilare.core.application.bloquear_saida",
        ) as mock_bloquear_saida,
        patch(
            "vigilare.core.application.desbloquear_rede",
        ) as mock_desbloquear_rede,
        patch(
            "vigilare.core.application.desativar_nat",
        ) as mock_desativar_nat,
        patch(
            "vigilare.core.application.remover_configuracao_dnsmasq",
        ) as mock_remover_dnsmasq,
    ):
        from vigilare.core.application import (
            aplicar_configuracao,
        )

        resultado = aplicar_configuracao(
            configuracao
        )

    assert resultado is True

    mock_bridge.assert_called_once_with(
        nome="gufo-br0",
        subrede=ipaddress.ip_network(
            "172.23.0.0/28"
        ),
    )

    mock_routing.assert_called_once_with(
        [configuracao]
    )

    mock_dnsmasq.assert_called_once_with(
        configuracao
    )

    mock_dhcp.assert_called_once()

    mock_firewall.assert_called_once_with(
        subrede=ipaddress.ip_network(
            "172.23.0.0/28"
        ),
        interface_saida="enp3s0",
        internet=True,
    )

    mock_remover_bridge.assert_not_called()
    mock_bloquear_saida.assert_not_called()
    mock_desbloquear_rede.assert_not_called()
    mock_desativar_nat.assert_not_called()
    mock_remover_dnsmasq.assert_not_called()

    assert configuracao["dhcp"]["ativo"] is True
    assert configuracao["firewall"] is True
    assert configuracao["nat"] is True
    assert configuracao["isolamento"] is True


def test_aplicar_configuracao_faz_rollback():
    configuracao = {
        "nome": "teste-rollback",
        "interface": "gufo-br0",
        "interface_saida": "enp3s0",
        "subrede": "172.24.0.0/28",
        "gateway": "172.24.0.1",
        "internet": True,
        "dhcp": {
            "ativo": False,
        },
    }

    resultado_bridge = {
        "bridge": "gufo-br0",
        "bridge_criada": True,
        "gateway": "172.24.0.1",
    }

    erro = RuntimeError(
        "Falha simulada no DHCP."
    )

    with (
        patch(
            "vigilare.core.application.ipv4_forward_ativo",
            return_value=False,
        ),
        patch(
            "vigilare.core.application.criar_bridge_quarentena",
            return_value=resultado_bridge,
        ),
        patch(
            "vigilare.core.application.configurar_routing",
        ) as mock_routing,
        patch(
            "vigilare.core.application.salvar_configuracao_dnsmasq",
            side_effect=erro,
        ),
        patch(
            "vigilare.core.application.ativar_dhcp",
        ) as mock_dhcp,
        patch(
            "vigilare.core.application.remover_configuracao_dnsmasq",
        ) as mock_remover_dnsmasq,
        patch(
            "vigilare.core.application.configurar_firewall",
        ),
        patch(
            "vigilare.core.application.bloquear_saida",
        ) as mock_bloquear_saida,
        patch(
            "vigilare.core.application.desativar_nat",
        ) as mock_desativar_nat,
        patch(
            "vigilare.core.application.remover_bridge",
        ) as mock_remover_bridge,
        patch(
            "vigilare.core.application.desabilitar_ipv4_forward",
        ) as mock_desabilitar_forward,
    ):
        from vigilare.core.application import (
            aplicar_configuracao,
        )

        with pytest.raises(
            RuntimeError,
            match="Falha simulada no DHCP.",
        ):
            aplicar_configuracao(
                configuracao
            )

    assert mock_routing.call_count == 2

    mock_routing.assert_any_call(
        [configuracao]
    )

    mock_routing.assert_any_call(
        []
    )

    mock_dhcp.assert_not_called()

    mock_remover_dnsmasq.assert_not_called()

    mock_bloquear_saida.assert_called_once_with(
        ipaddress.ip_network(
            "172.24.0.0/28"
        ),
        "enp3s0",
    )

    mock_desativar_nat.assert_called_once_with(
        ipaddress.ip_network(
            "172.24.0.0/28"
        ),
        "enp3s0",
    )

    mock_remover_bridge.assert_called_once_with(
        "gufo-br0"
    )

    mock_desabilitar_forward.assert_not_called()


def test_aplicar_configuracao_nao_remove_bridge_existente():
    configuracao = {
        "nome": "teste-existente",
        "interface": "gufo-br0",
        "interface_saida": "enp3s0",
        "subrede": "172.25.0.0/28",
        "gateway": "172.25.0.1",
        "internet": True,
        "dhcp": {
            "ativo": False,
        },
    }

    resultado_bridge = {
        "bridge": "gufo-br0",
        "bridge_criada": False,
        "gateway": "172.25.0.1",
    }

    with (
        patch(
            "vigilare.core.application.ipv4_forward_ativo",
            return_value=False,
        ),
        patch(
            "vigilare.core.application.criar_bridge_quarentena",
            return_value=resultado_bridge,
        ),
        patch(
            "vigilare.core.application.configurar_routing",
        ),
        patch(
            "vigilare.core.application.salvar_configuracao_dnsmasq",
            side_effect=RuntimeError(
                "Falha simulada."
            ),
        ),
        patch(
            "vigilare.core.application.ativar_dhcp",
        ),
        patch(
            "vigilare.core.application.configurar_firewall",
        ),
        patch(
            "vigilare.core.application.bloquear_saida",
        ),
        patch(
            "vigilare.core.application.desativar_nat",
        ),
        patch(
            "vigilare.core.application.remover_configuracao_dnsmasq",
        ),
        patch(
            "vigilare.core.application.remover_bridge",
        ) as mock_remover_bridge,
    ):
        from vigilare.core.application import (
            aplicar_configuracao,
        )

        with pytest.raises(RuntimeError):
            aplicar_configuracao(
                configuracao
            )

    mock_remover_bridge.assert_not_called()


def test_rollback_remove_configuracao_dhcp():
    configuracao = {
        "nome": "teste-dhcp-rollback",
        "interface": "gufo-br0",
        "interface_saida": "enp3s0",
        "subrede": "172.26.0.0/28",
        "gateway": "172.26.0.1",
        "internet": True,
        "dhcp": {
            "ativo": False,
        },
    }

    resultado_bridge = {
        "bridge": "gufo-br0",
        "bridge_criada": True,
        "gateway": "172.26.0.1",
    }

    erro = RuntimeError(
        "Falha simulada no firewall."
    )

    with (
        patch(
            "vigilare.core.application.ipv4_forward_ativo",
            return_value=False,
        ),
        patch(
            "vigilare.core.application.criar_bridge_quarentena",
            return_value=resultado_bridge,
        ),
        patch(
            "vigilare.core.application.configurar_routing",
        ),
        patch(
            "vigilare.core.application.salvar_configuracao_dnsmasq",
        ),
        patch(
            "vigilare.core.application.ativar_dhcp",
        ),
        patch(
            "vigilare.core.application.configurar_firewall",
            side_effect=erro,
        ),
        patch(
            "vigilare.core.application.remover_configuracao_dnsmasq",
        ) as mock_remover_dnsmasq,
        patch(
            "vigilare.core.application.remover_bridge",
        ) as mock_remover_bridge,
        patch(
            "vigilare.core.application.bloquear_saida",
        ),
        patch(
            "vigilare.core.application.desativar_nat",
        ),
    ):
        from vigilare.core.application import (
            aplicar_configuracao,
        )

        with pytest.raises(
            RuntimeError,
            match="Falha simulada no firewall.",
        ):
            aplicar_configuracao(
                configuracao
            )

    mock_remover_dnsmasq.assert_called_once_with(
        configuracao
    )

    mock_remover_bridge.assert_called_once_with(
        "gufo-br0"
    )


def test_rollback_restaura_forward_desligado():
    configuracao = {
        "nome": "teste-forward-off",
        "interface": "gufo-br0",
        "interface_saida": "enp3s0",
        "subrede": "172.27.0.0/28",
        "gateway": "172.27.0.1",
        "internet": True,
        "dhcp": {
            "ativo": False,
        },
    }

    resultado_bridge = {
        "bridge": "gufo-br0",
        "bridge_criada": True,
        "gateway": "172.27.0.1",
    }

    with (
        patch(
            "vigilare.core.application.ipv4_forward_ativo",
            side_effect=[
                False,
                True,
            ],
        ),
        patch(
            "vigilare.core.application.criar_bridge_quarentena",
            return_value=resultado_bridge,
        ),
        patch(
            "vigilare.core.application.configurar_routing",
        ),
        patch(
            "vigilare.core.application.salvar_configuracao_dnsmasq",
            side_effect=RuntimeError(
                "Falha simulada."
            ),
        ),
        patch(
            "vigilare.core.application.bloquear_saida",
        ),
        patch(
            "vigilare.core.application.desativar_nat",
        ),
        patch(
            "vigilare.core.application.remover_bridge",
        ),
        patch(
            "vigilare.core.application.desabilitar_ipv4_forward",
        ) as mock_desabilitar,
    ):
        from vigilare.core.application import (
            aplicar_configuracao,
        )

        with pytest.raises(RuntimeError):
            aplicar_configuracao(
                configuracao
            )

    mock_desabilitar.assert_called_once()


def test_rollback_restaura_forward_ligado():
    configuracao = {
        "nome": "teste-forward-on",
        "interface": "gufo-br0",
        "interface_saida": "enp3s0",
        "subrede": "172.28.0.0/28",
        "gateway": "172.28.0.1",
        "internet": False,
        "dhcp": {
            "ativo": False,
        },
    }

    resultado_bridge = {
        "bridge": "gufo-br0",
        "bridge_criada": True,
        "gateway": "172.28.0.1",
    }

    with (
        patch(
            "vigilare.core.application.ipv4_forward_ativo",
            side_effect=[
                True,
                False,
            ],
        ),
        patch(
            "vigilare.core.application.criar_bridge_quarentena",
            return_value=resultado_bridge,
        ),
        patch(
            "vigilare.core.application.configurar_routing",
        ),
        patch(
            "vigilare.core.application.salvar_configuracao_dnsmasq",
            side_effect=RuntimeError(
                "Falha simulada."
            ),
        ),
        patch(
            "vigilare.core.application.desbloquear_rede",
        ),
        patch(
            "vigilare.core.application.remover_bridge",
        ),
        patch(
            "vigilare.core.application.habilitar_ipv4_forward",
        ) as mock_habilitar,
    ):
        from vigilare.core.application import (
            aplicar_configuracao,
        )

        with pytest.raises(RuntimeError):
            aplicar_configuracao(
                configuracao
            )

    mock_habilitar.assert_called_once()


def test_remover_configuracao_com_internet():
    configuracao = {
        "nome": "teste-remocao",
        "interface": "gufo-br0",
        "interface_saida": "enp3s0",
        "subrede": "172.29.0.0/28",
        "gateway": "172.29.0.1",
        "internet": True,
        "dhcp": {
            "ativo": True,
        },
    }

    alocacoes = [
        configuracao,
    ]

    with (
        patch(
            "vigilare.core.application.bloquear_saida",
        ) as mock_bloquear_saida,
        patch(
            "vigilare.core.application.desativar_nat",
        ) as mock_desativar_nat,
        patch(
            "vigilare.core.application.remover_configuracao_dnsmasq",
        ) as mock_remover_dnsmasq,
        patch(
            "vigilare.core.application.ativar_dhcp",
        ) as mock_ativar_dhcp,
        patch(
            "vigilare.core.application.configurar_routing",
        ) as mock_routing,
        patch(
            "vigilare.core.application.remover_bridge",
        ) as mock_remover_bridge,
    ):
        from vigilare.core.application import (
            remover_configuracao,
        )

        resultado = remover_configuracao(
            configuracao,
            alocacoes,
        )

    assert resultado is True

    mock_bloquear_saida.assert_called_once_with(
        ipaddress.ip_network(
            "172.29.0.0/28"
        ),
        "enp3s0",
    )

    mock_desativar_nat.assert_called_once_with(
        ipaddress.ip_network(
            "172.29.0.0/28"
        ),
        "enp3s0",
    )

    mock_remover_dnsmasq.assert_called_once_with(
        configuracao
    )

    mock_ativar_dhcp.assert_called_once()

    mock_routing.assert_called_once_with(
        []
    )

    mock_remover_bridge.assert_called_once_with(
        "gufo-br0"
    )

    assert configuracao["dhcp"]["ativo"] is False
    assert configuracao["firewall"] is False
    assert configuracao["nat"] is False
    assert configuracao["isolamento"] is False


def test_remover_configuracao_sem_internet():
    configuracao = {
        "nome": "teste-remocao-sem-internet",
        "interface": "gufo-br0",
        "interface_saida": "enp3s0",
        "subrede": "172.30.0.0/28",
        "gateway": "172.30.0.1",
        "internet": False,
        "dhcp": {
            "ativo": True,
        },
    }

    alocacoes = [
        configuracao,
    ]

    with (
        patch(
            "vigilare.core.application.desbloquear_rede",
        ) as mock_desbloquear_rede,
        patch(
            "vigilare.core.application.remover_configuracao_dnsmasq",
        ) as mock_remover_dnsmasq,
        patch(
            "vigilare.core.application.ativar_dhcp",
        ) as mock_ativar_dhcp,
        patch(
            "vigilare.core.application.configurar_routing",
        ) as mock_routing,
        patch(
            "vigilare.core.application.remover_bridge",
        ) as mock_remover_bridge,
    ):
        from vigilare.core.application import (
            remover_configuracao,
        )

        resultado = remover_configuracao(
            configuracao,
            alocacoes,
        )

    assert resultado is True

    mock_desbloquear_rede.assert_called_once_with(
        ipaddress.ip_network(
            "172.30.0.0/28"
        )
    )

    mock_remover_dnsmasq.assert_called_once_with(
        configuracao
    )

    mock_ativar_dhcp.assert_called_once()

    mock_routing.assert_called_once_with(
        []
    )

    mock_remover_bridge.assert_called_once_with(
        "gufo-br0"
    )

    assert configuracao["dhcp"]["ativo"] is False
    assert configuracao["firewall"] is False
    assert configuracao["nat"] is False
    assert configuracao["isolamento"] is False


def test_remover_configuracao_mantem_outra_quarentena_com_internet():
    configuracao_remover = {
        "nome": "quarentena-remover",
        "interface": "gufo-br0",
        "interface_saida": "enp3s0",
        "subrede": "172.31.0.0/28",
        "gateway": "172.31.0.1",
        "internet": True,
        "dhcp": {
            "ativo": True,
        },
    }

    configuracao_restante = {
        "nome": "quarentena-restante",
        "interface": "gufo-br1",
        "interface_saida": "enp3s0",
        "subrede": "172.32.0.0/28",
        "gateway": "172.32.0.1",
        "internet": True,
        "dhcp": {
            "ativo": True,
        },
    }

    alocacoes = [
        configuracao_remover,
        configuracao_restante,
    ]

    with (
        patch(
            "vigilare.core.application.bloquear_saida",
        ) as mock_bloquear_saida,
        patch(
            "vigilare.core.application.desativar_nat",
        ) as mock_desativar_nat,
        patch(
            "vigilare.core.application.remover_configuracao_dnsmasq",
        ) as mock_remover_dnsmasq,
        patch(
            "vigilare.core.application.ativar_dhcp",
        ) as mock_ativar_dhcp,
        patch(
            "vigilare.core.application.configurar_routing",
        ) as mock_routing,
        patch(
            "vigilare.core.application.remover_bridge",
        ) as mock_remover_bridge,
    ):
        from vigilare.core.application import (
            remover_configuracao,
        )

        resultado = remover_configuracao(
            configuracao_remover,
            alocacoes,
        )

    assert resultado is True

    mock_bloquear_saida.assert_called_once_with(
        ipaddress.ip_network(
            "172.31.0.0/28"
        ),
        "enp3s0",
    )

    mock_desativar_nat.assert_called_once_with(
        ipaddress.ip_network(
            "172.31.0.0/28"
        ),
        "enp3s0",
    )

    mock_remover_dnsmasq.assert_called_once_with(
        configuracao_remover
    )

    mock_ativar_dhcp.assert_called_once()

    mock_routing.assert_called_once_with(
        [
            configuracao_restante,
        ]
    )

    mock_remover_bridge.assert_called_once_with(
        "gufo-br0"
    )

    assert configuracao_remover["dhcp"]["ativo"] is False
    assert configuracao_remover["firewall"] is False
    assert configuracao_remover["nat"] is False
    assert configuracao_remover["isolamento"] is False
