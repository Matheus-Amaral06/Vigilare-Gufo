import subprocess
from ipaddress import IPv4Address, IPv4Network
from pathlib import Path

from vigilare.utils.system import executar_comando


ARQUIVO_DNSMASQ = Path("/etc/dnsmasq.d/gufo.conf")
SERVICO_DNSMASQ = "dnsmasq"


def calcular_faixa_dhcp(subrede):
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

    return IPv4Address(primeiro_dhcp), IPv4Address(ultimo_host)


def criar_configuracao_dhcp(subrede, gateway, dns=None):
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
        "port=0",
        f"dhcp-range={inicio},{fim},{mascara},12h",
        f"dhcp-option=3,{gateway}",
    ]

    dns = dhcp.get("dns")

    if dns:
        linhas.append(f"dhcp-option=6,{dns}")

    return "\n".join(linhas) + "\n"


def salvar_configuracao_dnsmasq(configuracao):
    conteudo = gerar_configuracao_dnsmasq(configuracao)

    resultado = subprocess.run(
        [
            "sudo",
            "tee",
            str(ARQUIVO_DNSMASQ),
        ],
        input=conteudo,
        text=True,
        capture_output=True,
        check=False,
    )

    if resultado.returncode != 0:
        raise PermissionError(
            "Permissao negada ao escrever a configuracao do dnsmasq."
        )

    return ARQUIVO_DNSMASQ


def ativar_dhcp():
    executar_comando([
        "sudo",
        "systemctl",
        "restart",
        SERVICO_DNSMASQ,
    ])

    return True
