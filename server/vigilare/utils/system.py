import subprocess


def executar_comando(comando):
    """
    Executa um comando do sistema.

    Retorna:
        subprocess.CompletedProcess
    """
    return subprocess.run(
        comando,
        check=True,
        capture_output=True,
        text=True,
    )


def executar_comando_seguro(comando):
    """
    Executa um comando do sistema sem gerar excecao
    quando o comando retorna codigo diferente de zero.

    Retorna:
        subprocess.CompletedProcess
    """
    return subprocess.run(
        comando,
        check=False,
        capture_output=True,
        text=True,
    )
