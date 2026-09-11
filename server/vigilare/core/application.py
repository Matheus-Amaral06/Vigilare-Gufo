import ipaddress

from vigilare.network.bridge import criar_bridge_quarentena
from vigilare.security.firewall import configurar_firewall
from vigilare.services.dhcp import (
    ativar_dhcp,
    salvar_configuracao_dnsmasq,
)
from vigilare.services.routing import configurar_routing


def aplicar_configuracao(configuracao):
    subrede = ipaddress.ip_network(
        configuracao["subrede"]
    )
    internet = configuracao["internet"]
    interface_saida = configuracao["interface_saida"]

    criar_bridge_quarentena(
        nome=configuracao["interface"],
        subrede=subrede,
    )

    configurar_routing(internet)

    salvar_configuracao_dnsmasq(configuracao)
    ativar_dhcp()

    configurar_firewall(
        subrede=subrede,
        interface_saida=interface_saida,
        internet=internet,
    )

    return True
