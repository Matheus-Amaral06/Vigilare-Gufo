from vigilare.network.tester import teste_aprovado


def test_teste_aprovado_com_internet():
    resultado = {
        "gateway": True,
        "internet": True,
        "dns": True,
    }

    assert teste_aprovado(
        resultado,
        internet=True,
    ) is True


def test_teste_reprovado_com_internet_sem_acesso():
    resultado = {
        "gateway": True,
        "internet": False,
        "dns": False,
    }

    assert teste_aprovado(
        resultado,
        internet=True,
    ) is False


def test_teste_aprovado_sem_internet():
    resultado = {
        "gateway": True,
        "internet": False,
        "dns": False,
    }

    assert teste_aprovado(
        resultado,
        internet=False,
    ) is True


def test_teste_reprovado_sem_internet_com_acesso():
    resultado = {
        "gateway": True,
        "internet": True,
        "dns": True,
    }

    assert teste_aprovado(
        resultado,
        internet=False,
    ) is False


def test_teste_reprovado_gateway_indisponivel():
    resultado = {
        "gateway": False,
        "internet": False,
        "dns": False,
    }

    assert teste_aprovado(
        resultado,
        internet=False,
    ) is False
