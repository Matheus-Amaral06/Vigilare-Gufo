import os
import sys
import termios
import tty

from vigilare.core.application import (
    aplicar_configuracao,
    remover_configuracao,
    testar_quarentena,
)
from vigilare.core.quarantine import montar_configuracao
from vigilare.network.interfaces import get_interfaces
from vigilare.utils.storage import carregar_json, salvar_json


ARQUIVO_ALOCACOES = "data/redes_alocadas.json"


def limpar_tela():
    os.system("clear")


def ler_tecla():
    fd = sys.stdin.fileno()
    configuracao_anterior = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        tecla = sys.stdin.read(1)

        if tecla == "\x1b":
            tecla += sys.stdin.read(2)

        return tecla

    finally:
        termios.tcsetattr(
            fd,
            termios.TCSADRAIN,
            configuracao_anterior,
        )


def pausar():
    print()
    print("Pressione qualquer tecla para continuar...")
    ler_tecla()


def cabecalho(titulo):
    limpar_tela()

    print("╔════════════════════════════════════════╗")
    print("║             VIGILARE - GUFO            ║")
    print("╚════════════════════════════════════════╝")
    print()
    print(f"  {titulo}")
    print()


def escolher_interface_saida():
    interfaces = get_interfaces()

    if not interfaces["ethernet"]:
        raise RuntimeError(
            "Nenhuma interface Ethernet encontrada."
        )

    return interfaces["ethernet"][0]


def perguntar_nome():
    while True:
        cabecalho("Criar quarentena")

        nome = input("  Nome da rede: ").strip()

        if nome:
            return nome

        print()
        print("  O nome da rede não pode ser vazio.")
        input(
            "  Pressione Enter para tentar novamente..."
        )


def perguntar_num_hosts():
    while True:
        cabecalho("Criar quarentena")

        valor = input(
            "  Quantidade de hosts: "
        ).strip()

        try:
            num_hosts = int(valor)

            if num_hosts <= 0:
                raise ValueError

            return num_hosts

        except ValueError:
            print()
            print(
                "  Digite uma quantidade de hosts válida."
            )
            input(
                "  Pressione Enter para tentar novamente..."
            )


def perguntar_internet():
    while True:
        cabecalho("Criar quarentena")

        print("  A quarentena terá acesso à Internet?")
        print()
        print("  [S] Sim")
        print("  [N] Não")
        print()

        resposta = input("  Escolha: ").strip().upper()

        if resposta == "S":
            return True

        if resposta == "N":
            return False

        print()
        print("  Digite S para Sim ou N para Não.")
        input(
            "  Pressione Enter para tentar novamente..."
        )


def exibir_configuracao(configuracao):
    cabecalho("Resumo da quarentena")

    print(
        f"  Nome:                "
        f"{configuracao['nome']}"
    )

    print(
        f"  Interface:           "
        f"{configuracao['interface']}"
    )

    print(
        f"  Interface de saída:  "
        f"{configuracao['interface_saida']}"
    )

    print(
        f"  Rede-mãe:             "
        f"{configuracao['rede_mae']}"
    )

    print(
        f"  Sub-rede:             "
        f"{configuracao['subrede']}"
    )

    print(
        f"  Gateway:              "
        f"{configuracao['gateway']}"
    )

    print(
        f"  Hosts solicitados:    "
        f"{configuracao['hosts_solicitados']}"
    )

    print(
        f"  Hosts disponíveis:    "
        f"{configuracao['hosts_disponiveis']}"
    )

    print(
        f"  Internet:             "
        f"{'Sim' if configuracao['internet'] else 'Não'}"
    )

    print()
    print("  Serviços:")
    print()

    print(
        f"    DHCP:       "
        f"{'Ativo' if configuracao['dhcp']['ativo'] else 'Inativo'}"
    )

    print(
        f"    Firewall:   "
        f"{'Ativo' if configuracao['firewall'] else 'Inativo'}"
    )

    print(
        f"    NAT:        "
        f"{'Ativo' if configuracao['nat'] else 'Inativo'}"
    )

    print(
        f"    Isolamento: "
        f"{'Ativo' if configuracao['isolamento'] else 'Inativo'}"
    )


def confirmar_aplicacao():
    print()
    print("  Aplicar esta configuração?")
    print()
    print("  [S] Sim")
    print("  [N] Não")
    print()

    while True:
        resposta = input(
            "  Escolha: "
        ).strip().upper()

        if resposta == "S":
            return True

        if resposta == "N":
            return False

        print(
            "  Digite S para Sim ou N para Não."
        )


def criar_quarentena():
    nome = perguntar_nome()
    num_hosts = perguntar_num_hosts()
    internet = perguntar_internet()

    try:
        interface_saida = escolher_interface_saida()
        alocacoes = carregar_json(
            ARQUIVO_ALOCACOES
        )

        configuracao = montar_configuracao(
            nome=nome,
            num_hosts=num_hosts,
            interface_quarentena=None,
            interface_saida=interface_saida,
            alocacoes=alocacoes,
            internet=internet,
        )

    except Exception as erro:
        cabecalho("Falha ao preparar quarentena")

        print(
            "  Não foi possível montar a configuração."
        )
        print()
        print(f"  Erro: {erro}")

        pausar()
        return

    exibir_configuracao(configuracao)

    if not confirmar_aplicacao():
        cabecalho("Operação cancelada")
        print("  Nenhuma alteração foi aplicada.")
        pausar()
        return

    cabecalho("Aplicando configuração")

    print(
        "  Criando a infraestrutura da quarentena..."
    )
    print()

    try:
        aplicar_configuracao(
            configuracao,
            alocacoes,
        )

        alocacoes.append(configuracao)

        salvar_json(
            ARQUIVO_ALOCACOES,
            alocacoes,
        )

    except Exception as erro:
        print()
        print(
            "  ERRO ao aplicar a configuração:"
        )
        print(f"  {erro}")
        print()
        print(
            "  A configuração não foi registrada"
        )
        print(
            "  nas alocações."
        )

        pausar()
        return

    print(
        "  Quarentena criada com sucesso!"
    )
    print()
    print(
        f"  Rede:      "
        f"{configuracao['subrede']}"
    )

    print(
        f"  Gateway:   "
        f"{configuracao['gateway']}"
    )

    print(
        f"  Interface: "
        f"{configuracao['interface']}"
    )

    print(
        f"  Internet:  "
        f"{'Sim' if configuracao['internet'] else 'Não'}"
    )

    pausar()


def listar_quarentenas():
    cabecalho("Quarentenas cadastradas")

    alocacoes = carregar_json(
        ARQUIVO_ALOCACOES
    )

    if not alocacoes:
        print(
            "  Nenhuma quarentena cadastrada."
        )
        pausar()
        return

    for indice, rede in enumerate(
        alocacoes,
        start=1,
    ):
        print(
            f"  [{indice}] "
            f"{rede.get('nome', 'Sem nome')}"
        )

        print(
            f"      Interface: "
            f"{rede.get('interface', 'N/A')}"
        )

        print(
            f"      Rede:      "
            f"{rede.get('subrede', 'N/A')}"
        )

        print(
            f"      Gateway:   "
            f"{rede.get('gateway', 'N/A')}"
        )

        print(
            f"      Internet:  "
            f"{'Sim' if rede.get('internet') else 'Não'}"
        )

        print()

    pausar()


def escolher_quarentena(alocacoes):
    while True:
        cabecalho("Selecionar quarentena")

        if not alocacoes:
            print(
                "  Nenhuma quarentena cadastrada."
            )
            pausar()
            return None

        for indice, configuracao in enumerate(
            alocacoes,
            start=1,
        ):
            print(
                f"  [{indice}] "
                f"{configuracao.get('nome', 'Sem nome')}"
            )

            print(
                f"      Rede:      "
                f"{configuracao.get('subrede', 'N/A')}"
            )

            print(
                f"      Interface: "
                f"{configuracao.get('interface', 'N/A')}"
            )

            print()

        print("  [0] Cancelar")
        print()

        resposta = input(
            "  Escolha: "
        ).strip()

        if resposta == "0":
            return None

        try:
            indice = int(resposta)

            if 1 <= indice <= len(alocacoes):
                return alocacoes[indice - 1]

        except ValueError:
            pass

        print()
        print(
            "  Escolha uma quarentena válida."
        )

        input(
            "  Pressione Enter para tentar novamente..."
        )


def confirmar_remocao(configuracao):
    cabecalho("Remover quarentena")

    print(
        f"  Nome:      "
        f"{configuracao.get('nome', 'Sem nome')}"
    )

    print(
        f"  Interface: "
        f"{configuracao.get('interface', 'N/A')}"
    )

    print(
        f"  Rede:      "
        f"{configuracao.get('subrede', 'N/A')}"
    )

    print(
        f"  Gateway:   "
        f"{configuracao.get('gateway', 'N/A')}"
    )

    print()
    print(
        "  ATENÇÃO: os recursos desta quarentena"
    )
    print(
        "  serão removidos do sistema."
    )

    print()
    print("  [S] Confirmar remoção")
    print("  [N] Cancelar")
    print()

    while True:
        resposta = input(
            "  Escolha: "
        ).strip().upper()

        if resposta == "S":
            return True

        if resposta == "N":
            return False

        print()
        print(
            "  Digite S para confirmar ou N para cancelar."
        )


def remover_quarentena():
    alocacoes = carregar_json(
        ARQUIVO_ALOCACOES
    )

    configuracao = escolher_quarentena(
        alocacoes
    )

    if configuracao is None:
        return

    if not confirmar_remocao(configuracao):
        cabecalho("Operação cancelada")
        print(
            "  Nenhuma alteração foi aplicada."
        )
        pausar()
        return

    cabecalho("Removendo quarentena")

    print(
        "  Removendo a infraestrutura da quarentena..."
    )
    print()

    try:
        remover_configuracao(
            configuracao,
            alocacoes,
        )

        alocacoes.remove(configuracao)

        salvar_json(
            ARQUIVO_ALOCACOES,
            alocacoes,
        )

    except Exception as erro:
        print()
        print(
            "  ERRO ao remover a quarentena:"
        )
        print(f"  {erro}")
        print()
        print(
            "  A configuração foi mantida"
        )
        print(
            "  nas alocações."
        )

        pausar()
        return

    print(
        "  Quarentena removida com sucesso!"
    )
    print()

    print(
        f"  Rede removida: "
        f"{configuracao.get('subrede', 'N/A')}"
    )

    print(
        f"  Interface removida: "
        f"{configuracao.get('interface', 'N/A')}"
    )

    pausar()


def exibir_resultado_teste(resultado):
    cabecalho("Resultado do teste")

    testes = resultado["testes"]

    print(
        "  Testes de conectividade:"
    )
    print()

    print(
        f"    Gateway:   "
        f"{'OK' if testes['gateway'] else 'FALHOU'}"
    )

    print(
        f"    Internet:  "
        f"{'OK' if testes['internet'] else 'FALHOU'}"
    )

    print(
        f"    DNS:       "
        f"{'OK' if testes['dns'] else 'FALHOU'}"
    )

    print()

    if resultado["sucesso"]:
        print(
            "  ╔══════════════════════════════════╗"
        )
        print(
            "  ║    QUARENTENA FUNCIONANDO       ║"
        )
        print(
            "  ╚══════════════════════════════════╝"
        )
    else:
        print(
            "  ╔══════════════════════════════════╗"
        )
        print(
            "  ║      TESTE COM FALHAS            ║"
        )
        print(
            "  ╚══════════════════════════════════╝"
        )

    cliente = resultado.get("cliente")

    if cliente:
        print()
        print("  Cliente virtual:")

        print(
            f"    IP:         "
            f"{cliente['ipv4']}"
        )

        print(
            f"    CIDR:       "
            f"{cliente['cidr']}"
        )

        print(
            f"    Interface:  "
            f"{cliente['interface_cliente']}"
        )


def testar_quarentena_tui():
    alocacoes = carregar_json(
        ARQUIVO_ALOCACOES
    )

    configuracao = escolher_quarentena(
        alocacoes
    )

    if configuracao is None:
        return

    cabecalho("Testando quarentena")

    print(
        f"  Quarentena: "
        f"{configuracao.get('nome', 'Sem nome')}"
    )

    print(
        f"  Rede:       "
        f"{configuracao.get('subrede', 'N/A')}"
    )

    print()
    print(
        "  Criando cliente virtual..."
    )
    print(
        "  Solicitando endereço via DHCP..."
    )
    print(
        "  Executando testes..."
    )
    print()

    try:
        resultado = testar_quarentena(
            configuracao
        )

    except Exception as erro:
        cabecalho("Falha no teste")

        print(
            "  Não foi possível concluir o teste."
        )
        print()
        print(f"  Erro: {erro}")

        pausar()
        return

    exibir_resultado_teste(resultado)

    pausar()


def menu_principal():
    opcoes = [
        "Criar quarentena",
        "Listar quarentenas",
        "Remover quarentena",
        "Testar quarentena",
        "Sair",
    ]

    selecionada = 0

    while True:
        cabecalho(
            "Gerenciador de redes de quarentena"
        )

        for indice, opcao in enumerate(opcoes):
            if indice == selecionada:
                print(f"  > {opcao}")
            else:
                print(f"    {opcao}")

        print()
        print(
            "  ↑ ↓ navegar | Enter selecionar"
        )

        tecla = ler_tecla()

        if tecla in ("\x1b[A", "w"):
            selecionada = (
                selecionada - 1
            ) % len(opcoes)

        elif tecla in ("\x1b[B", "s"):
            selecionada = (
                selecionada + 1
            ) % len(opcoes)

        elif tecla in ("\r", "\n"):
            return selecionada


def executar_tui():
    while True:
        opcao = menu_principal()

        if opcao == 0:
            criar_quarentena()

        elif opcao == 1:
            listar_quarentenas()

        elif opcao == 2:
            remover_quarentena()

        elif opcao == 3:
            testar_quarentena_tui()

        elif opcao == 4:
            limpar_tela()
            print(
                "Encerrando Vigilare-Gufo..."
            )
            break
