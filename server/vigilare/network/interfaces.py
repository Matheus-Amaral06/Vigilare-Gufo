import ipaddress
from pathlib import Path

from vigilare.utils.system import executar_comando


def get_interfaces():
    """
    Identifica as interfaces de rede disponíveis no sistema.

    Retorna:
        dict: interfaces físicas separadas entre ethernet e wireless,
        além das interfaces virtuais.
    """
    interfaces = {
        "ethernet": [],
        "wireless": [],
        "virtual": [],
    }

    caminho = Path("/sys/class/net")

    if not caminho.exists():
        raise RuntimeError(
            "Nao foi possivel acessar /sys/class/net."
        )

    for iface_path in caminho.iterdir():
        iface = iface_path.name

        if iface == "lo":
            continue

        dispositivo = iface_path / "device"

        if not dispositivo.exists():
            interfaces["virtual"].append(iface)
            continue

        if (iface_path / "wireless").exists():
            interfaces["wireless"].append(iface)
        else:
            interfaces["ethernet"].append(iface)

    return interfaces


def listar_interfaces():
    """Exibe as interfaces de rede encontradas."""
    interfaces = get_interfaces()

    print("\nInterfaces encontradas:")

    print("\nEthernet:")
    for iface in interfaces["ethernet"] or ["  Nenhuma"]:
        print(f"  - {iface}")

    print("\nWireless:")
    for iface in interfaces["wireless"] or ["  Nenhuma"]:
        print(f"  - {iface}")

    print("\nVirtuais:")
    for iface in interfaces["virtual"] or ["  Nenhuma"]:
        print(f"  - {iface}")


def validar_interface(interface):
    """
    Verifica se uma interface existe no sistema.

    Levanta:
        ValueError se a interface nao existir.
    """
    interfaces = get_interfaces()

    todas = (
        interfaces["ethernet"]
        + interfaces["wireless"]
        + interfaces["virtual"]
    )

    if interface not in todas:
        raise ValueError(
            f"Interface '{interface}' nao encontrada."
        )


def obter_interface_saida_padrao(destino="1.1.1.1"):
    resultado = executar_comando([
        "ip",
        "route",
        "get",
        destino,
    ])

    partes = resultado.stdout.split()

    if "dev" not in partes:
        raise RuntimeError(
            "Nao foi possivel identificar a interface de saida."
        )

    indice_dev = partes.index("dev")

    if indice_dev + 1 >= len(partes):
        raise RuntimeError(
            "A rota nao informou uma interface de saida."
        )

    interface = partes[indice_dev + 1]

    validar_interface(interface)

    return interface


def obter_redes_existentes(interface):
    validar_interface(interface)

    resultado = executar_comando([
        "ip",
        "-4",
        "addr",
        "show",
        interface,
    ])

    redes = []

    for linha in resultado.stdout.splitlines():
        linha = linha.strip()

        if linha.startswith("inet "):
            ip_cidr = linha.split()[1]
            rede = ipaddress.ip_interface(ip_cidr).network
            redes.append(rede)

    return redes


def obter_todas_redes_existentes():
    interfaces = get_interfaces()

    todas_interfaces = (
        interfaces["ethernet"]
        + interfaces["wireless"]
        + interfaces["virtual"]
    )

    redes = []

    for interface in todas_interfaces:
        redes.extend(
            obter_redes_existentes(interface)
        )

    return redes
