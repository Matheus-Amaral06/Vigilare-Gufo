from scapy.all import ARP , Ether, srp, conf
print ("Olá Mundo")
class ScanRede:
	def __init__(self, faixa_ip: str,interface: str, timeout: int = 2):
		self.faixa_ip = faixa_ip
		self.timeout = timeout
		self.interface = interface
	def pacote(self):
		ether = Ether(dst="ff:ff:ff:ff:ff:ff")
		arp = ARP(pdst=self.faixa_ip)
		return ether / arp
	def scan(self) -> list[dict[str, str]]:
		pacote = self.pacote()
		respostas, _ =srp(pacote, timeout=self.timeout, iface=self.interface, verbose=False)
		dispositivos = []
		for enviado, recebido in respostas:
			dispositivos.append({
				'ip': recebido.psrc,
				'mac': recebido.hwsrc
			})
		return dispositivos
def obter() -> str:
	ip_gateway = conf.route.route("0.0.0.0")
	ip_roteador = ip_gateway[2]
	interface_ativa = conf.iface.name if hasattr(conf.iface, 'name') else str(conf.iface)
	partes = ip_roteador.split('.')
	faixa_rede = f"{partes[0]}.{partes[1]}.{partes[2]}.0/24"
	return faixa_rede, interface_ativa
if __name__ == "__main__":
	rede = obter()
	rede_detectada, iface_detectada = obter()
	scanner = ScanRede(faixa_ip=rede_detectada, interface=iface_detectada, timeout=5)
	print(f"ESCANEANDO A REDE {scanner.faixa_ip}...\n")
	alvos = scanner.scan()
	print("DISPOSITIVOS ENCONTRADOS")
	print("IP\t\t\tENDEREÇO MAC")
	print("-" * 40)
	for dispositivo in alvos:
		print(f"{dispositivo['ip']}\t\t{dispositivo['mac']}")

