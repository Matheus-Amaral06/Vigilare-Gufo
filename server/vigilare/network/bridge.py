from ipaddress import IPv4Address, IPv4Network

from vigilare.utils.system import (
    executar_comando,
    executar_comando_seguro,
)


def bridge_existe(nome):
    resultado = executar_comando_seguro([
        "ip",
        "link",
        "show",
        nome,
    ])

    return resultado.returncode == 0


def criar_bridge(nome):
    if bridge_existe(nome):
        return nome

    executar_comando([
        "sudo",
        "ip",
        "link",
        "add",
        nome,
        "type",
        "bridge",
    ])

    return nome


def ativar_bridge(nome):
    if not bridge_existe(nome):
        raise ValueError(
            f"A bridge '{nome}' nao existe."
        )

    executar_comando([
        "sudo",
        "ip",
        "link",
        "set",
        nome,
        "up",
    ])


def configurar_gateway(nome_bridge, subrede):
    if not bridge_existe(nome_bridge):
        raise ValueError(
            f"A bridge '{nome_bridge}' nao existe."
        )

    if not isinstance(subrede, IPv4Network):
        raise TypeError(
            "A sub-rede deve ser um objeto IPv4Network."
        )

    gateway = IPv4Address(
        int(subrede.network_address) + 1
    )

    resultado = executar_comando([
        "sudo",
        "ip",
        "-4",
        "addr",
        "show",
        "dev",
        nome_bridge,
    ])

    endereco_gateway = f"{gateway}/{subrede.prefixlen}"

    enderecos_atuais = []

    for linha in resultado.stdout.splitlines():
        linha = linha.strip()

        if linha.startswith("inet "):
            endereco = linha.split()[1]
            enderecos_atuais.append(endereco)

    for endereco in enderecos_atuais:
        if endereco != endereco_gateway:
            executar_comando([
                "sudo",
                "ip",
                "addr",
                "del",
                endereco,
                "dev",
                nome_bridge,
            ])

    if endereco_gateway not in enderecos_atuais:
        executar_comando([
            "sudo",
            "ip",
            "addr",
            "add",
            endereco_gateway,
            "dev",
            nome_bridge,
        ])

    return gateway


def remover_bridge(nome):
    if not bridge_existe(nome):
        return

    executar_comando([
        "sudo",
        "ip",
        "link",
        "delete",
        nome,
        "type",
        "bridge",
    ])


def criar_bridge_quarentena(
    nome="gufo-br0",
    subrede=None,
):
    criar_bridge(nome)
    ativar_bridge(nome)

    gateway = None

    if subrede is not None:
        gateway = configurar_gateway(
            nome,
            subrede,
        )

    return {
        "bridge": nome,
        "gateway": (
            str(gateway)
            if gateway is not None
            else None
        ),
    }
