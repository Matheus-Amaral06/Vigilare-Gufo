from vigilare.core.allocator import (
    alocar_subrede,
    escolher_bloco_privado,
    obter_redes_ocupadas,
)
from vigilare.network.interfaces import obter_todas_redes_existentes
from vigilare.network.segment import SegmentoQuarentena
from vigilare.services.dhcp import criar_configuracao_dhcp


def escolher_rede_mae(alocacoes):
    redes_existentes = obter_todas_redes_existentes()
    redes_alocadas = obter_redes_ocupadas(alocacoes)
    redes_ocupadas = redes_existentes + redes_alocadas

    return escolher_bloco_privado(redes_ocupadas)


def calcular_gateway(subrede):
    return subrede.network_address + 1


def criar_subrede(rede_mae, num_hosts, alocacoes):
    return alocar_subrede(rede_mae, num_hosts, alocacoes)


def criar_segmento(
    nome,
    interface_quarentena,
    subrede,
    gateway,
    internet=False,
):
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
    rede_mae = escolher_rede_mae(alocacoes)

    subrede = criar_subrede(
        rede_mae,
        num_hosts,
        alocacoes,
    )

    gateway = calcular_gateway(subrede)

    segmento = criar_segmento(
        nome=nome,
        interface_quarentena=interface_quarentena,
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
        "hosts_disponiveis": segmento.hosts_disponiveis(),
        "dhcp": dhcp,
        "firewall": False,
        "nat": internet,
        "isolamento": True,
        "interface_saida": interface_saida,
    })

    return configuracao
