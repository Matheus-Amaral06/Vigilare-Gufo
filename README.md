# Vigilare-Gufo

Sistema de gerenciamento e automação de redes de quarentena para ambientes Linux.

## Sobre o projeto

O Vigilare-Gufo é um projeto acadêmico desenvolvido para demonstrar como uma aplicação pode automatizar a criação e o gerenciamento de segmentos de rede isolados.

A proposta é permitir que o usuário crie uma rede de quarentena informando apenas:

- Nome da rede;
- Quantidade de hosts;
- Se a rede terá acesso à Internet.

A partir dessas informações, o Vigilare calcula automaticamente uma sub-rede disponível e configura os recursos necessários para o funcionamento da quarentena.

## Objetivo

O projeto busca demonstrar, de forma prática, conceitos de:

- IPv4 e subnetting;
- Alocação automática de endereços;
- DHCP;
- Gateway;
- Roteamento;
- NAT;
- Firewall;
- Isolamento de redes;
- Interfaces virtuais;
- Linux networking;
- Automação de infraestrutura.

## Como funciona

O fluxo principal do Vigilare é:

```text
Usuário
   |
   v
Criar quarentena
   |
   +--> Nome da rede
   |
   +--> Quantidade de hosts
   |
   +--> Internet: Sim/Não
   |
   v
Vigilare
   |
   +--> Detecta redes existentes
   |
   +--> Escolhe uma rede privada disponível
   |
   +--> Calcula a sub-rede
   |
   +--> Define o gateway
   |
   +--> Cria a bridge
   |
   +--> Configura DHCP
   |
   +--> Configura firewall
   |
   +--> Configura roteamento
   |
   +--> Configura NAT quando necessário
   |
   v
Quarentena ativa
