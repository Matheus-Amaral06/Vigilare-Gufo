import ipaddress


# Espaço privado usado pelo Vigilare para alocação
ESPACO_PRIVADO = ipaddress.ip_network("172.16.0.0/12")


def validar_num_hosts(num_hosts):
    """Valida a quantidade de hosts solicitada."""

    if not isinstance(num_hosts, int):
        raise TypeError("A quantidade de hosts deve ser um numero inteiro.")

    if num_hosts <= 0:
        raise ValueError("A quantidade de hosts deve ser maior que zero.")


def prefixo_necessario(num_hosts, rede_mae):
    """
    Calcula o prefixo CIDR necessário para a quantidade de hosts.

    Considera:
        - endereço de rede
        - endereço de broadcast
    """

    validar_num_hosts(num_hosts)

    total_enderecos = num_hosts + 2
    bits_host = (total_enderecos - 1).bit_length()
    prefixo = 32 - bits_host

    if prefixo > 30:
        raise ValueError(f"Quantidade de hosts invalida: {num_hosts}")

    if prefixo < rede_mae.prefixlen:
        raise ValueError(
            f"A rede solicitada e maior que a rede mae {rede_mae}."
        )

    return prefixo


def escolher_bloco_privado(redes_existentes):
    """
    Escolhe um /16 livre dentro do espaço privado 172.16.0.0/12.

    O bloco escolhido não pode sobrepor nenhuma rede existente.
    """

    for candidato in ESPACO_PRIVADO.subnets(new_prefix=16):
        if not any(candidato.overlaps(rede) for rede in redes_existentes):
            return candidato

    raise RuntimeError(
        "Nenhum bloco privado livre encontrado no espaco disponivel."
    )


def obter_redes_ocupadas(alocacoes):
    """
    Converte as redes armazenadas nas alocações
    para objetos IPv4Network.
    """

    redes = []

    for alocacao in alocacoes:
        try:
            redes.append(ipaddress.ip_network(alocacao["subrede"]))
        except (KeyError, ValueError) as erro:
            raise RuntimeError(
                f"Alocacao invalida encontrada: {alocacao}"
            ) from erro

    return redes


def alocar_subrede(rede_mae, num_hosts, alocacoes):
    """
    Encontra a primeira sub-rede livre dentro da rede-mãe.
    """

    prefixo = prefixo_necessario(num_hosts, rede_mae)
    redes_ocupadas = obter_redes_ocupadas(alocacoes)

    for candidata in rede_mae.subnets(new_prefix=prefixo):
        if not any(
            candidata.overlaps(ocupada)
            for ocupada in redes_ocupadas
        ):
            return candidata

    raise RuntimeError(
        "Nao ha espaco livre suficiente na rede de quarentena."
    )
