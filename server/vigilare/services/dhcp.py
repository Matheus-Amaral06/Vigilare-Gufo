import subprocess
from ipaddress import IPv4Address, IPv4Network
from pathlib import Path

from vigilare.utils.system import executar_comando


DIRETORIO_DNSMASQ = Path("/etc/dnsmasq.d")
PREFIXO_ARQUIVO = "gufo-"
SERVICO_DNSMASQ = "dnsmasq"


def calcular_faixa_dhcp(subrede):
    """
    Calcula a faixa de endereços que será entregue pelo DHCP.

    O primeiro endereço utilizável da sub-rede é reservado
    para o gateway. O DHCP começa no endereço seguinte.
    """
    if not isinstance(subrede, IPv4Network):
        raise TypeError(
            "A sub-rede deve ser um objeto IPv4Network."
        )

    primeiro_host = subrede.network_address + 1
    ultimo_host = subrede.broadcast_address - 1

    if primeiro_host == ultimo_host:
        raise ValueError(
            "A sub-rede nao possui enderecos suficientes para DHCP."
        )

    primeiro_dhcp = primeiro_host + 1

    return (
        IPv4Address(primeiro_dhcp),
        IPv4Address(ultimo_host),
    )


def criar_configuracao_dhcp(
    subrede,
    gateway,
    dns="1.1.1.1",
):
    """
    Cria a configuração lógica do DHCP para uma sub-rede.
    """
    if not isinstance(subrede, IPv4Network):
        raise TypeError(
            "A sub-rede deve ser um objeto IPv4Network."
        )

    if not isinstance(gateway, IPv4Address):
        gateway = IPv4Address(gateway)

    if gateway not in subrede:
        raise ValueError(
            "O gateway nao pertence a sub-rede."
        )

    inicio, fim = calcular_faixa_dhcp(subrede)

    return {
        "ativo": False,
        "subrede": str(subrede),
        "gateway": str(gateway),
        "faixa_inicio": str(inicio),
        "faixa_fim": str(fim),
        "dns": dns,
    }


def gerar_configuracao_dnsmasq(configuracao):
    """
    Gera o conteúdo do arquivo de configuração
    do dnsmasq para uma quarentena.
    """
    dhcp = configuracao["dhcp"]

    subrede = dhcp["subrede"]
    gateway = dhcp["gateway"]
    inicio = dhcp["faixa_inicio"]
    fim = dhcp["faixa_fim"]
    interface = configuracao["interface"]

    mascara = IPv4Network(subrede).netmask

    linhas = [
        f"interface={interface}",
        "bind-interfaces",
        f"dhcp-range={inicio},{fim},{mascara},12h",
        f"dhcp-option=3,{gateway}",
    ]

    dns = dhcp.get("dns")

    if dns:
        linhas.append(
            f"dhcp-option=6,{dns}"
        )

    return "\n".join(linhas) + "\n"


def nome_arquivo_dnsmasq(configuracao):
    """
    Gera um nome determinístico para o arquivo da quarentena.

    Exemplo:
        172.16.0.0/28
        ↓
        gufo-172-16-0-0.conf
    """
    subrede = configuracao["subrede"]

    nome_seguro = (
        subrede
        .replace("/", "-")
        .replace(".", "-")
    )

    return DIRETORIO_DNSMASQ / (
        f"{PREFIXO_ARQUIVO}{nome_seguro}.conf"
    )


def salvar_configuracao_dnsmasq(configuracao):
    """
    Salva a configuração DHCP da quarentena em
    um arquivo próprio.
    """
    conteudo = gerar_configuracao_dnsmasq(
        configuracao
    )

    arquivo = nome_arquivo_dnsmasq(
        configuracao
    )

    resultado = subprocess.run(
        [
            "sudo",
            "tee",
            str(arquivo),
        ],
        input=conteudo,
        text=True,
        capture_output=True,
        check=False,
    )

    if resultado.returncode != 0:
        raise PermissionError(
            "Permissao negada ao escrever "
            "a configuracao do dnsmasq."
        )

    return arquivo


def remover_configuracao_dnsmasq(
    configuracao,
):
    """
    Remove somente o arquivo de configuração
    pertencente à quarentena informada.
    """
    arquivo = nome_arquivo_dnsmasq(
        configuracao
    )

    if not arquivo.exists():
        return False

    executar_comando([
        "sudo",
        "rm",
        "-f",
        str(arquivo),
    ])

    return True


def testar_configuracao_dnsmasq():
    """
    Valida a configuração atual do dnsmasq
    antes de reiniciar o serviço.
    """
    resultado = subprocess.run(
        [
            "sudo",
            "dnsmasq",
            "--test",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if resultado.returncode != 0:
        raise RuntimeError(
            "A configuracao do dnsmasq e invalida: "
            f"{resultado.stderr.strip()}"
        )

    return True


def ativar_dhcp():
    """
    Valida e reinicia o dnsmasq.
    """
    testar_configuracao_dnsmasq()

    executar_comando([
        "sudo",
        "systemctl",
        "restart",
        SERVICO_DNSMASQ,
    ])

    return True
