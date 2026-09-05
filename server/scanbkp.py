from scapy.all import ARP , Ether, srp
print ("Olá Mundo")

rede = "192.168.0.1/24"

pacote = Ether(dst = "ff:ff:ff:ff:ff:ff")/ ARP (pdst=rede)

respostas, nao_respondidos = srp(pacote, timeout=2 , verbose=False)

for enviado, recebido in respostas:
    print(recebido.psrc, recebido.hwsrc)
