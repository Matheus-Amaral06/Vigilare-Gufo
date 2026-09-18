import ipaddress
import subprocess
import time

from vigilare.utils.system import (
    executar_comando,
    executar_comando_seguro,
)

NAMESPACE_CLIENTE = "gufo-client-ns"
INTERFACE_HOST = "gufo-vhost"
INTERFACE_CLIENTE = "gufo-vcli"


def namespace_existe(nome=NAMESPACE_CLIENTE):
    resultado = executar_comando_seguro([
        "sudo",
        "ip",
        "netns",
        "list",
    ])

    if resultado.returncode != 0:
        return False

    for linha in resultado.stdout.splitlines():
        nome_encontrado = linha.split()[0]
        if nome_encontrado == nome:
            return True

    return False


def interface_existe(nome):
    resultado = executar_comando_seguro([
        "ip",
        "link",
        "show",
        nome,
    ])
    return resultado.returncode == 0


def interface_no_namespace_existe(
    nome,
    namespace=NAMESPACE_CLIENTE,
):
    resultado = executar_comando_seguro([
        "sudo",
        "ip",
        "netns",
        "exec",
        namespace,
        "ip",
        "link",
        "show",
        nome,
    ])
    return resultado.returncode == 0


def criar_namespace(nome=NAMESPACE_CLIENTE):
    if namespace_existe(nome):
        return False

    executar_comando([
        "sudo",
        "ip",
        "netns",
        "add",
        nome,
    ])
    return True


def criar_veth(
    interface_host=INTERFACE_HOST,
    interface_cliente=INTERFACE_CLIENTE,
):
    if interface_existe(interface_host):
        raise RuntimeError(
            f"A interface '{interface_host}' ja existe."
        )

    executar_comando([
        "sudo",
        "ip",
        "link",
        "add",
        interface_host,
        "type",
        "veth",
        "peer",
        "name",
        interface_cliente,
    ])


def conectar_veth_bridge(
    interface_host,
    bridge,
):
    if not interface_existe(interface_host):
        raise ValueError(
            f"A interface '{interface_host}' nao existe."
        )

    if not interface_existe(bridge):
        raise ValueError(
            f"A bridge '{bridge}' nao existe."
        )

    executar_comando([
        "sudo",
        "ip",
        "link",
        "set",
        interface_host,
        "master",
        bridge,
    ])

    executar_comando([
        "sudo",
        "ip",
        "link",
        "set",
        interface_host,
        "up",
    ])


def mover_interface_para_namespace(
    interface_cliente=INTERFACE_CLIENTE,
    namespace=NAMESPACE_CLIENTE,
):
    if not interface_existe(interface_cliente):
        raise ValueError(
            f"A interface '{interface_cliente}' nao existe."
        )

    if not namespace_existe(namespace):
        raise ValueError(
            f"O namespace '{namespace}' nao existe."
        )

    executar_comando([
        "sudo",
        "ip",
        "link",
        "set",
        interface_cliente,
        "netns",
        namespace,
    ])


def ativar_interface_cliente(
    interface_cliente=INTERFACE_CLIENTE,
    namespace=NAMESPACE_CLIENTE,
):
    if not namespace_existe(namespace):
        raise ValueError(
            f"O namespace '{namespace}' nao existe."
        )

    executar_comando([
        "sudo",
        "ip",
        "netns",
        "exec",
        namespace,
        "ip",
        "link",
        "set",
        "lo",
        "up",
    ])

    if not interface_no_namespace_existe(
        interface_cliente,
        namespace,
    ):
        raise ValueError(
            f"A interface '{interface_cliente}' nao existe "
            f"no namespace '{namespace}'."
        )

    executar_comando([
        "sudo",
        "ip",
        "netns",
        "exec",
        namespace,
        "ip",
        "link",
        "set",
        interface_cliente,
        "up",
    ])


def parar_dhcp(
    interface_cliente=INTERFACE_CLIENTE,
    namespace=NAMESPACE_CLIENTE,
):
    if not namespace_existe(namespace):
        return False

    executar_comando_seguro([
        "sudo",
        "ip",
        "netns",
        "exec",
        namespace,
        "pkill",
        "dhcpcd",
    ])

    time.sleep(0.5)

    return True


def iniciar_dhcp(
    interface_cliente=INTERFACE_CLIENTE,
    namespace=NAMESPACE_CLIENTE,
):
    if not namespace_existe(namespace):
        raise ValueError(
            f"O namespace '{namespace}' nao existe."
        )

    if not interface_no_namespace_existe(
        interface_cliente,
        namespace,
    ):
        raise ValueError(
            f"A interface '{interface_cliente}' nao existe "
            f"no namespace '{namespace}'."
        )

    parar_dhcp(
        interface_cliente=interface_cliente,
        namespace=namespace,
    )

    processo = subprocess.Popen(
        [
            "sudo",
            "ip",
            "netns",
            "exec",
            namespace,
            "dhcpcd",
            "--nohook",
            "resolv.conf",
            interface_cliente,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    time.sleep(0.5)

    if processo.poll() is not None:
        stdout, stderr = processo.communicate()

        mensagem = stderr.strip() or stdout.strip()

        if mensagem:
            raise RuntimeError(
                "O dhcpcd encerrou imediatamente: "
                f"{mensagem}"
            )

        raise RuntimeError(
            "O dhcpcd encerrou imediatamente "
            "sem informar o motivo."
        )

    return processo


def obter_ipv4_cliente(
    interface_cliente=INTERFACE_CLIENTE,
    namespace=NAMESPACE_CLIENTE,
):
    resultado = executar_comando_seguro([
        "sudo",
        "ip",
        "netns",
        "exec",
        namespace,
        "ip",
        "-4",
        "addr",
        "show",
        "dev",
        interface_cliente,
    ])

    if resultado.returncode != 0:
        return None

    for linha in resultado.stdout.splitlines():
        linha = linha.strip()

        if not linha.startswith("inet "):
            continue

        endereco_cidr = linha.split()[1]
        return ipaddress.ip_interface(endereco_cidr)

    return None


def aguardar_ipv4_cliente(
    interface_cliente=INTERFACE_CLIENTE,
    namespace=NAMESPACE_CLIENTE,
    timeout=15,
):
    inicio = time.monotonic()

    while time.monotonic() - inicio < timeout:
        endereco = obter_ipv4_cliente(
            interface_cliente=interface_cliente,
            namespace=namespace,
        )

        if endereco is not None:
            return endereco

        time.sleep(0.5)

    raise TimeoutError(
        "O cliente virtual nao recebeu um endereco IPv4 "
        "via DHCP dentro do tempo esperado."
    )


def preparar_cliente_virtual(
    configuracao,
    namespace=NAMESPACE_CLIENTE,
    interface_host=INTERFACE_HOST,
    interface_cliente=INTERFACE_CLIENTE,
):
    bridge = configuracao["interface"]

    limpar_cliente_virtual(
        namespace=namespace,
        interface_host=interface_host,
    )

    criar_namespace(namespace)

    criar_veth(
        interface_host=interface_host,
        interface_cliente=interface_cliente,
    )

    conectar_veth_bridge(
        interface_host=interface_host,
        bridge=bridge,
    )

    mover_interface_para_namespace(
        interface_cliente=interface_cliente,
        namespace=namespace,
    )

    ativar_interface_cliente(
        interface_cliente=interface_cliente,
        namespace=namespace,
    )

    iniciar_dhcp(
        interface_cliente=interface_cliente,
        namespace=namespace,
    )

    endereco = aguardar_ipv4_cliente(
        interface_cliente=interface_cliente,
        namespace=namespace,
    )

    return {
        "namespace": namespace,
        "interface_host": interface_host,
        "interface_cliente": interface_cliente,
        "bridge": bridge,
        "ipv4": str(endereco.ip),
        "cidr": str(endereco),
    }


def limpar_cliente_virtual(
    namespace=NAMESPACE_CLIENTE,
    interface_host=INTERFACE_HOST,
):
    if namespace_existe(namespace):
        parar_dhcp(namespace=namespace)

        executar_comando_seguro([
            "sudo",
            "ip",
            "netns",
            "delete",
            namespace,
        ])

    if interface_existe(interface_host):
        executar_comando_seguro([
            "sudo",
            "ip",
            "link",
            "delete",
            interface_host,
        ])

    return True

