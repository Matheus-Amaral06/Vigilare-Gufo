from vigilare.utils.system import executar_comando


def ipv4_forward_ativo():
    """
    Verifica se o encaminhamento IPv4 está ativo no sistema.
    """
    resultado = executar_comando(
        [
            "sysctl",
            "-n",
            "net.ipv4.ip_forward",
        ]
    )

    return resultado.stdout.strip() == "1"


def habilitar_ipv4_forward():
    """
    Ativa o encaminhamento IPv4 no Linux.
    """
    executar_comando(
        [
            "sudo",
            "sysctl",
            "-w",
            "net.ipv4.ip_forward=1",
        ]
    )


def desabilitar_ipv4_forward():
    """
    Desativa o encaminhamento IPv4 no Linux.
    """
    executar_comando(
        [
            "sudo",
            "sysctl",
            "-w",
            "net.ipv4.ip_forward=0",
        ]
    )


def existe_quarentena_com_internet(alocacoes):
    """
    Verifica se existe pelo menos uma quarentena
    configurada com acesso à Internet.
    """
    return any(
        alocacao.get("internet", False)
        for alocacao in alocacoes
    )


def configurar_routing(alocacoes):
    """
    Configura o encaminhamento IPv4 de acordo
    com as quarentenas existentes.

    O ip_forward é um recurso global do sistema.
    Portanto, ele só pode ser desativado quando
    nenhuma quarentena precisar de roteamento.
    """
    if existe_quarentena_com_internet(alocacoes):
        habilitar_ipv4_forward()
        return True

    desabilitar_ipv4_forward()
    return False
