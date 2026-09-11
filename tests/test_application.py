from unittest.mock import patch


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

    with (
        patch("vigilare.core.application.criar_bridge_quarentena") as mock_bridge,
        patch("vigilare.core.application.configurar_routing") as mock_routing,
        patch("vigilare.core.application.salvar_configuracao_dnsmasq") as mock_dnsmasq,
        patch("vigilare.core.application.ativar_dhcp") as mock_dhcp,
        patch("vigilare.core.application.configurar_firewall") as mock_firewall,
    ):
        resultado = __import__(
            "vigilare.core.application",
            fromlist=["aplicar_configuracao"],
        ).aplicar_configuracao(configuracao)

    assert resultado is True

    mock_bridge.assert_called_once()
    mock_routing.assert_called_once_with(True)
    mock_dnsmasq.assert_called_once_with(configuracao)
    mock_dhcp.assert_called_once()
    mock_firewall.assert_called_once_with(
        subrede=__import__("ipaddress").ip_network("172.23.0.0/28"),
        interface_saida="enp3s0",
        internet=True,
    )
