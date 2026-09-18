from ipaddress import IPv4Address, IPv4Network

from vigilare.utils.system import (
    executar_comando,
    executar_comando_seguro,
)


def bridge_existe(nome):
    """
    Verifica se uma bridge/interface existe no sistema.
    """
    resultado = executar_comando_seguro([
        "ip",
        "link",
        "show",
        nome,
    ])

    return resultado.returncode == 0


def criar_bridge(nome):
    """
    Cria uma bridge caso ela ainda não exista.

    Retorna:
        dict:
            nome: nome da bridge
            criada: True se foi criada agora,
                    False se já existia.
    """
    if bridge_existe(nome):
        return {
            "nome": nome,
            "criada": False,
        }

    executar_comando([
        "sudo",
        "ip",
        "link",
        "add",
        nome,
        "type",
        "bridge",
    ])

    return {
        "nome": nome,
        "criada": True,
    }


def ativar_bridge(nome):
    """
    Ativa uma bridge existente.
    """
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
    """
    Configura o primeiro endereço utilizável da sub-rede
    como gateway da bridge.

    Remove outros endereços IPv4 da bridge antes de
    configurar o gateway correto.
    """
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

    endereco_gateway = (
        f"{gateway}/{subrede.prefixlen}"
    )

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
    """
    Remove uma bridge existente.

    Se a bridge não existir, nenhuma ação é realizada.
    """
    if not bridge_existe(nome):
        return False

    executar_comando([
        "sudo",
        "ip",
        "link",
        "delete",
        nome,
        "type",
        "bridge",
    ])

    return True


def criar_bridge_quarentena(
    nome="gufo-br0",
    subrede=None,
):
    """
    Cria e ativa a bridge de uma quarentena.

    Retorna informações sobre a infraestrutura criada,
    incluindo se a bridge foi criada durante esta operação.
    """
    resultado_bridge = criar_bridge(nome)

    ativar_bridge(nome)

    gateway = None

    if subrede is not None:
        gateway = configurar_gateway(
            nome,
            subrede,
        )

    return {
        "bridge": nome,
        "bridge_criada": resultado_bridge["criada"],
        "gateway": (
            str(gateway)
            if gateway is not None
            else None
        ),
    }
