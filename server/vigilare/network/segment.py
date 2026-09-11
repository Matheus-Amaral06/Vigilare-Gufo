from dataclasses import dataclass
from ipaddress import IPv4Address, IPv4Network


@dataclass
class SegmentoQuarentena:
    """
    Representa um segmento lógico de rede de quarentena.

    Nesta etapa a classe descreve a configuração do segmento.
    A criação da infraestrutura Linux será adicionada
    posteriormente, sem alterar diretamente a interface física
    da rede existente.
    """

    nome: str
    interface: str
    subrede: IPv4Network
    gateway: IPv4Address
    internet: bool = False

    def resumo(self):
        """
        Retorna um resumo das características do segmento.
        """
        return {
            "nome": self.nome,
            "interface": self.interface,
            "subrede": str(self.subrede),
            "gateway": str(self.gateway),
            "internet": self.internet,
        }

    def hosts_disponiveis(self):
        """
        Retorna a quantidade de endereços utilizáveis
        para dispositivos dentro da sub-rede.

        O primeiro endereço é reservado para a rede
        e o último é reservado para broadcast.
        """
        return self.subrede.num_addresses - 2

    def pertence(self, endereco):
        """
        Verifica se um endereço IPv4 pertence à sub-rede.
        """
        endereco = IPv4Address(endereco)

        return endereco in self.subrede
