import subprocess


def executar_ping(namespace, destino, quantidade=3):
    resultado = subprocess.run(
        [
            "sudo",
            "ip",
            "netns",
            "exec",
            namespace,
            "ping",
            "-c",
            str(quantidade),
            "-W",
            "2",
            destino,
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    return resultado.returncode == 0


def testar_gateway(namespace, gateway):
    return executar_ping(namespace, gateway)


def testar_internet(namespace):
    return executar_ping(namespace, "1.1.1.1")


def testar_dns(namespace):
    return executar_ping(namespace, "google.com")


def testar_conectividade(namespace, gateway):
    return {
        "gateway": testar_gateway(namespace, gateway),
        "internet": testar_internet(namespace),
        "dns": testar_dns(namespace),
    }


def teste_aprovado(resultado, internet):
    if not resultado["gateway"]:
        return False

    if internet:
        return resultado["internet"] and resultado["dns"]

    return not resultado["internet"] and not resultado["dns"]


teste_aprovado.__test__ = False
