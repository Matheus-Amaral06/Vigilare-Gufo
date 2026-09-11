from vigilare.core.application import aplicar_configuracao
from vigilare.core.quarantine import montar_configuracao
from vigilare.network.interfaces import get_interfaces
from vigilare.utils.storage import carregar_json, salvar_json

NOME_BRIDGE_QUARENTENA = "gufo-br0"


def escolher_interface_saida():
    interfaces = get_interfaces()

    if not interfaces["ethernet"]:
        raise RuntimeError("Nenhuma interface Ethernet encontrada.")

    return interfaces["ethernet"][0]


def escolher_interface_quarentena():
    return NOME_BRIDGE_QUARENTENA


def perguntar_nome():
    while True:
        nome = input("Nome da rede: ").strip()

        if nome:
            return nome

        print("O nome da rede nao pode ser vazio.")


def perguntar_num_hosts():
    while True:
        valor = input("Quantidade de hosts: ").strip()

        try:
            num_hosts = int(valor)

            if num_hosts <= 0:
                raise ValueError

            return num_hosts

        except ValueError:
            print("Digite uma quantidade de hosts valida.")


def perguntar_internet():
    while True:
        resposta = input("Internet? (S/N): ").strip().upper()

        if resposta == "S":
            return True

        if resposta == "N":
            return False

        print("Digite S para Sim ou N para Nao.")


def confirmar_aplicacao():
    while True:
        resposta = input("\nAplicar esta configuracao? (S/N): ").strip().upper()

        if resposta == "S":
            return True

        if resposta == "N":
            return False

        print("Digite S para Sim ou N para Nao.")


def exibir_configuracao(configuracao):
    print("\n=== Configuracao da Rede ===")
    print(f"Nome: {configuracao['nome']}")
    print(f"Interface da quarentena: {configuracao['interface']}")
    print(f"Interface de saida: {configuracao['interface_saida']}")
    print(f"Rede-mae: {configuracao['rede_mae']}")
    print(f"Sub-rede: {configuracao['subrede']}")
    print(f"Gateway: {configuracao['gateway']}")
    print(f"Hosts solicitados: {configuracao['hosts_solicitados']}")
    print(f"Hosts disponiveis: {configuracao['hosts_disponiveis']}")
    print(f"Internet: {'Sim' if configuracao['internet'] else 'Nao'}")
    print(f"DHCP: {'Ativo' if configuracao['dhcp']['ativo'] else 'Inativo'}")
    print(f"Firewall: {'Ativo' if configuracao['firewall'] else 'Inativo'}")
    print(f"NAT: {'Ativo' if configuracao['nat'] else 'Inativo'}")
    print(f"Isolamento: {'Ativo' if configuracao['isolamento'] else 'Inativo'}")


def main():
    print("=== Vigilare-Gufo ===")
    print("Gerenciador de redes de quarentena\n")

    nome = perguntar_nome()
    num_hosts = perguntar_num_hosts()
    internet = perguntar_internet()

    interface_saida = escolher_interface_saida()
    interface_quarentena = escolher_interface_quarentena()

    print(f"\nInterface da quarentena: {interface_quarentena}")
    print(f"Interface de saida: {interface_saida}")

    alocacoes = carregar_json("data/redes_alocadas.json")

    configuracao = montar_configuracao(
        nome=nome,
        num_hosts=num_hosts,
        interface_quarentena=interface_quarentena,
        interface_saida=interface_saida,
        alocacoes=alocacoes,
        internet=internet,
    )

    exibir_configuracao(configuracao)

    if not confirmar_aplicacao():
        print("\nConfiguracao cancelada. Nenhuma alteracao foi aplicada.")
        return

    print("\nAplicando configuracao...")

    aplicar_configuracao(configuracao)

    alocacoes.append(configuracao)
    salvar_json("data/redes_alocadas.json", alocacoes)

    print("\nConfiguracao aplicada com sucesso.")


if __name__ == "__main__":
    main()
