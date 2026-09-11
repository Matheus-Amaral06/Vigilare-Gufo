from vigilare.utils.system import (
    executar_comando,
    executar_comando_seguro,
)


def interface_existe(nome):
    """
    Verifica se uma interface de rede existe no sistema.
    """
    resultado = executar_comando_seguro(
        [
            "ip",
            "link",
            "show",
            nome,
        ]
    )

    return resultado.returncode == 0


def criar_interface_dummy(nome):
    """
    Cria uma interface virtual do tipo dummy.
    """
    if interface_existe(nome):
        raise RuntimeError(
            f"A interface '{nome}' ja existe."
        )

    executar_comando(
        [
            "sudo",
            "ip",
            "link",
            "add",
            nome,
            "type",
            "dummy",
        ]
    )


def ativar_interface(nome):
    """
    Ativa uma interface de rede existente.
    """
    if not interface_existe(nome):
        raise ValueError(
            f"A interface '{nome}' nao existe."
        )

    executar_comando(
        [
            "sudo",
            "ip",
            "link",
            "set",
            nome,
            "up",
        ]
    )


def desativar_interface(nome):
    """
    Desativa uma interface de rede existente.
    """
    if not interface_existe(nome):
        raise ValueError(
            f"A interface '{nome}' nao existe."
        )

    executar_comando(
        [
            "sudo",
            "ip",
            "link",
            "set",
            nome,
            "down",
        ]
    )


def remover_interface(nome):
    """
    Remove uma interface de rede existente.
    """
    if not interface_existe(nome):
        raise ValueError(
            f"A interface '{nome}' nao existe."
        )

    executar_comando(
        [
            "sudo",
            "ip",
            "link",
            "delete",
            nome,
        ]
    )


def criar_interface_quarentena(nome="gufo-quarantine"):
    """
    Cria e ativa a interface virtual da quarentena.

    Retorna:
        str: nome da interface criada.
    """
    criar_interface_dummy(nome)
    ativar_interface(nome)

    return nome


def criar_bridge(nome):
    """
    Cria uma bridge Linux.
    """
    if interface_existe(nome):
        raise RuntimeError(
            f"A bridge '{nome}' ja existe."
        )

    executar_comando(
        [
            "sudo",
            "ip",
            "link",
            "add",
            nome,
            "type",
            "bridge",
        ]
    )


def ativar_bridge(nome):
    """
    Ativa uma bridge existente.
    """
    if not interface_existe(nome):
        raise ValueError(
            f"A bridge '{nome}' nao existe."
        )

    executar_comando(
        [
            "sudo",
            "ip",
            "link",
            "set",
            nome,
            "up",
        ]
    )


def remover_bridge(nome):
    """
    Remove uma bridge existente.
    """
    if not interface_existe(nome):
        raise ValueError(
            f"A bridge '{nome}' nao existe."
        )

    executar_comando(
        [
            "sudo",
            "ip",
            "link",
            "delete",
            nome,
            "type",
            "bridge",
        ]
    )


def criar_infraestrutura_quarentena(
    nome_bridge="gufo-br0",
):
    """
    Cria a infraestrutura Linux inicial da quarentena.

    Nesta etapa:
        1. cria a bridge;
        2. ativa a bridge.

    A bridge ainda nao possui interfaces conectadas.
    """
    criar_bridge(nome_bridge)
    ativar_bridge(nome_bridge)

    return nome_bridge
