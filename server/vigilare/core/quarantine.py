from vigilare.core.allocator import (
    alocar_subrede,
    escolher_bloco_privado,
    obter_redes_ocupadas,
)
from vigilare.network.interfaces import obter_todas_redes_existentes
from vigilare.network.segment import SegmentoQuarentena
from vigilare.services.dhcp import criar_configuracao_dhcp


PREFIXO_BRIDGE = "gufo-br"


def escolher_rede_mae(alocacoes):
    """
    Escolhe uma rede-mãe privada que não sobreponha
    redes existentes ou redes já alocadas pelo Vigilare.
    """
    redes_existentes = obter_todas_redes_existentes()
    redes_alocadas = obter_redes_ocupadas(alocacoes)
    redes_ocupadas = (
        redes_existentes + redes_alocadas
    )

    return escolher_bloco_privado(
        redes_ocupadas
    )


def calcular_gateway(subrede):
    """
    Define o primeiro endereço utilizável da sub-rede
    como gateway.
    """
    return subrede.network_address + 1


def criar_subrede(
    rede_mae,
    num_hosts,
    alocacoes,
):
    """
    Cria a primeira sub-rede disponível dentro
    da rede-mãe.
    """
    return alocar_subrede(
        rede_mae,
        num_hosts,
        alocacoes,
    )


def gerar_nome_bridge(alocacoes):
    """
    Gera o próximo nome de bridge do Vigilare.

    Exemplos:

        nenhuma quarentena → gufo-br0
        uma quarentena     → gufo-br1
        duas quarentenas   → gufo-br2

    O nome gerado será armazenado na configuração
    da quarentena.
    """
    indices = []

    for alocacao in alocacoes:
        interface = alocacao.get(
            "interface",
            "",
        )

        if not interface.startswith(
            PREFIXO_BRIDGE
        ):
            continue

        numero = interface[
            len(PREFIXO_BRIDGE):
        ]

        if numero.isdigit():
            indices.append(
                int(numero)
            )

    proximo_indice = 0

    while proximo_indice in indices:
        proximo_indice += 1

    return (
        f"{PREFIXO_BRIDGE}"
        f"{proximo_indice}"
    )


def criar_segmento(
    nome,
    interface_quarentena,
    subrede,
    gateway,
    internet=False,
):
    """
    Cria o objeto que representa o segmento
    lógico de quarentena.
    """
    return SegmentoQuarentena(
        nome=nome,
        interface=interface_quarentena,
        subrede=subrede,
        gateway=gateway,
        internet=internet,
    )


def montar_configuracao(
    nome,
    num_hosts,
    interface_quarentena,
    interface_saida,
    alocacoes,
    internet=False,
):
    """
    Monta toda a configuração lógica de uma
    nova quarentena.
    """
    if interface_quarentena is None:
        interface_quarentena = (
            gerar_nome_bridge(alocacoes)
        )

    rede_mae = escolher_rede_mae(
        alocacoes
    )

    subrede = criar_subrede(
        rede_mae,
        num_hosts,
        alocacoes,
    )

    gateway = calcular_gateway(
        subrede
    )

    segmento = criar_segmento(
        nome=nome,
        interface_quarentena=(
            interface_quarentena
        ),
        subrede=subrede,
        gateway=gateway,
        internet=internet,
    )

    dhcp = criar_configuracao_dhcp(
        subrede=subrede,
        gateway=gateway,
    )

    dhcp["ativo"] = False

    configuracao = segmento.resumo()

    configuracao.update({
        "rede_mae": str(rede_mae),
        "hosts_solicitados": num_hosts,
        "hosts_disponiveis": (
            segmento.hosts_disponiveis()
        ),
        "dhcp": dhcp,
        "firewall": False,
        "nat": internet,
        "isolamento": True,
        "interface_saida": interface_saida,
    })

    return configuracao
