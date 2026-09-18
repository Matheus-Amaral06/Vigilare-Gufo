# Arquitetura do Vigilare-Gufo

## 1. Visão geral

O Vigilare-Gufo é organizado em módulos responsáveis por diferentes partes do gerenciamento de uma rede de quarentena.

A aplicação utiliza Python para controlar recursos de rede do sistema Linux, como:

- Interfaces de rede;
- Bridges;
- IPv4;
- DHCP;
- Roteamento;
- Firewall;
- NAT;
- Network namespaces;
- Interfaces virtuais.

A arquitetura foi separada para evitar que toda a lógica do projeto fique concentrada em um único arquivo.

---

## 2. Fluxo geral

O fluxo principal da aplicação é:

```text
                    VIGILARE
                       |
                       v
                    TUI
                       |
                       v
              Core / Application
                       |
          +------------+------------+
          |            |            |
          v            v            v
      Network       Services     Security
          |            |            |
          v            v            v
       Bridge        DHCP       Firewall/NAT
          |
          v
    Segmento virtual
          |
          v
    Cliente virtual
