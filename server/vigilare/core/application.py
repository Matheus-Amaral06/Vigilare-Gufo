import ipaddress

from vigilare.network.bridge import (
    criar_bridge_quarentena,
    remover_bridge,
)
from vigilare.network.lab import (
    preparar_cliente_virtual,
    limpar_cliente_virtual,
)
from vigilare.network.tester import (
    testar_conectividade,
    teste_aprovado,
)
from vigilare.security.firewall import (
    bloquear_saida,
    desbloquear_rede,
    desativar_nat,
    configurar_firewall,
)
from vigilare.services.dhcp import (
    ativar_dhcp,
    remover_configuracao_dnsmasq,
    salvar_configuracao_dnsmasq,
)
from vigilare.services.routing import (
    configurar_routing,
    ipv4_forward_ativo,
    habilitar_ipv4_forward,
    desabilitar_ipv4_forward,
)


def restaurar_ipv4_forward(estado_anterior):
    estado_atual = ipv4_forward_ativo()

    if estado_anterior and not estado_atual:
        habilitar_ipv4_forward()
    elif not estado_anterior and estado_atual:
        desabilitar_ipv4_forward()


def desfazer_firewall(subrede, interface_saida, internet):
    if internet:
        bloquear_saida(subrede, interface_saida)
        desativar_nat(subrede, interface_saida)
    else:
        desbloquear_rede(subrede)


def aplicar_configuracao(configuracao, alocacoes=None):
    if alocacoes is None:
        alocacoes = []

    subrede = ipaddress.ip_network(configuracao["subrede"])
    internet = configuracao["internet"]
    interface_saida = configuracao["interface_saida"]
    nome_bridge = configuracao["interface"]

    estado_forward_anterior = ipv4_forward_ativo()

    bridge_criada = False
    routing_configurado = False
    dhcp_configurado = False

    try:
        resultado_bridge = criar_bridge_quarentena(
            nome=nome_bridge,
            subrede=subrede,
        )

        bridge_criada = resultado_bridge["bridge_criada"]

        alocacoes_com_nova_quarentena = [
            *alocacoes,
            configuracao,
        ]

        configurar_routing(alocacoes_com_nova_quarentena)
        routing_configurado = True

        salvar_configuracao_dnsmasq(configuracao)
        dhcp_configurado = True

        ativar_dhcp()

        configurar_firewall(
            subrede=subrede,
            interface_saida=interface_saida,
            internet=internet,
        )

        configuracao["dhcp"]["ativo"] = True
        configuracao["firewall"] = True
        configuracao["nat"] = internet
        configuracao["isolamento"] = True

        return True

    except Exception:
        try:
            desfazer_firewall(
                subrede=subrede,
                interface_saida=interface_saida,
                internet=internet,
            )
        except Exception:
            pass

        if dhcp_configurado:
            try:
                remover_configuracao_dnsmasq(configuracao)
                ativar_dhcp()
            except Exception:
                pass

        if routing_configurado:
            try:
                configurar_routing(alocacoes)
            except Exception:
                pass

        try:
            restaurar_ipv4_forward(estado_forward_anterior)
        except Exception:
            pass

        if bridge_criada:
            try:
                remover_bridge(nome_bridge)
            except Exception:
                pass

        raise


def remover_configuracao(configuracao, alocacoes=None):
    if alocacoes is None:
        alocacoes = []

    subrede = ipaddress.ip_network(configuracao["subrede"])
    internet = configuracao["internet"]
    interface_saida = configuracao["interface_saida"]
    nome_bridge = configuracao["interface"]

    alocacoes_restantes = [
        alocacao
        for alocacao in alocacoes
        if alocacao is not configuracao
        and alocacao.get("subrede") != configuracao.get("subrede")
    ]

    desfazer_firewall(
        subrede=subrede,
        interface_saida=interface_saida,
        internet=internet,
    )

    remover_configuracao_dnsmasq(configuracao)

    ativar_dhcp()

    configurar_routing(alocacoes_restantes)

    remover_bridge(nome_bridge)

    configuracao["dhcp"]["ativo"] = False
    configuracao["firewall"] = False
    configuracao["nat"] = False
    configuracao["isolamento"] = False

    return True


def testar_quarentena(configuracao):
    namespace = None

    try:
        cliente = preparar_cliente_virtual(configuracao)

        namespace = cliente["namespace"]

        resultado = testar_conectividade(
            namespace=namespace,
            gateway=configuracao["gateway"],
        )

        return {
            "sucesso": teste_aprovado(
                resultado,
                internet=configuracao["internet"],
            ),
            "testes": resultado,
            "cliente": cliente,
        }

    finally:
        limpar_cliente_virtual()
