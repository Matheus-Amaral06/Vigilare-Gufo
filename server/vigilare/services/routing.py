from vigilare.utils.system import executar_comando


def ipv4_forward_ativo():
    resultado = executar_comando(
        ["sysctl", "-n", "net.ipv4.ip_forward"]
    )
    return resultado.stdout.strip() == "1"


def habilitar_ipv4_forward():
    executar_comando(
        ["sudo", "sysctl", "-w", "net.ipv4.ip_forward=1"]
    )


def desabilitar_ipv4_forward():
    executar_comando(
        ["sudo", "sysctl", "-w", "net.ipv4.ip_forward=0"]
    )

def configurar_routing(internet):
    if internet:
        habilitar_ipv4_forward()
