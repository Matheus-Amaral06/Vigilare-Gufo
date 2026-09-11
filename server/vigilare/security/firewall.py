from vigilare.utils.system import (
    executar_comando,
    executar_comando_seguro,
)


def regra_bloqueio_existe(subrede):
    resultado = executar_comando_seguro([
        "sudo",
        "iptables",
        "-C",
        "FORWARD",
        "-s",
        str(subrede),
        "-j",
        "DROP",
    ])

    return resultado.returncode == 0


def bloquear_rede(subrede):
    if regra_bloqueio_existe(subrede):
        return

    executar_comando([
        "sudo",
        "iptables",
        "-A",
        "FORWARD",
        "-s",
        str(subrede),
        "-j",
        "DROP",
    ])


def desbloquear_rede(subrede):
    while regra_bloqueio_existe(subrede):
        executar_comando([
            "sudo",
            "iptables",
            "-D",
            "FORWARD",
            "-s",
            str(subrede),
            "-j",
            "DROP",
        ])


def regra_nat_existe(subrede, interface_saida):
    resultado = executar_comando_seguro([
        "sudo",
        "iptables",
        "-t",
        "nat",
        "-C",
        "POSTROUTING",
        "-s",
        str(subrede),
        "-o",
        interface_saida,
        "-j",
        "MASQUERADE",
    ])

    return resultado.returncode == 0


def ativar_nat(subrede, interface_saida):
    if regra_nat_existe(subrede, interface_saida):
        return

    executar_comando([
        "sudo",
        "iptables",
        "-t",
        "nat",
        "-A",
        "POSTROUTING",
        "-s",
        str(subrede),
        "-o",
        interface_saida,
        "-j",
        "MASQUERADE",
    ])


def desativar_nat(subrede, interface_saida):
    while regra_nat_existe(subrede, interface_saida):
        executar_comando([
            "sudo",
            "iptables",
            "-t",
            "nat",
            "-D",
            "POSTROUTING",
            "-s",
            str(subrede),
            "-o",
            interface_saida,
            "-j",
            "MASQUERADE",
        ])


def regra_saida_existe(subrede, interface_saida):
    resultado = executar_comando_seguro([
        "sudo",
        "iptables",
        "-C",
        "FORWARD",
        "-s",
        str(subrede),
        "-o",
        interface_saida,
        "-j",
        "ACCEPT",
    ])

    return resultado.returncode == 0


def permitir_saida(subrede, interface_saida):
    desbloquear_rede(subrede)

    if regra_saida_existe(subrede, interface_saida):
        return

    executar_comando([
        "sudo",
        "iptables",
        "-A",
        "FORWARD",
        "-s",
        str(subrede),
        "-o",
        interface_saida,
        "-j",
        "ACCEPT",
    ])


def bloquear_saida(subrede, interface_saida):
    while regra_saida_existe(subrede, interface_saida):
        executar_comando([
            "sudo",
            "iptables",
            "-D",
            "FORWARD",
            "-s",
            str(subrede),
            "-o",
            interface_saida,
            "-j",
            "ACCEPT",
        ])


def configurar_firewall(subrede, interface_saida, internet):
    if internet:
        desbloquear_rede(subrede)
        permitir_saida(subrede, interface_saida)
        ativar_nat(subrede, interface_saida)
        return

    bloquear_saida(subrede, interface_saida)
    desativar_nat(subrede, interface_saida)
    bloquear_rede(subrede)
