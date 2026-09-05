from scapy.all import ARP,Ether,sniff
poetry run python -c "import scapy; pint ('Scapy')"
class Monitorar:
	def __init__(self, pacotes):
		pacotes = sniff(count=5)
		pacotes.summary
