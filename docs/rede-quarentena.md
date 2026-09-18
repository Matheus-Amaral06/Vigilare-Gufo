# Rede de Quarentena

## 1. Conceito

No Vigilare-Gufo, uma quarentena é um **segmento lógico de rede criado no sistema Linux** para separar determinados clientes do restante da infraestrutura.

A quarentena possui:

- Sua própria sub-rede IPv4;
- Seu próprio gateway;
- Um serviço DHCP;
- Regras de firewall;
- NAT quando o acesso à Internet está habilitado;
- Uma interface virtual do tipo bridge.

A ideia é permitir que o administrador crie uma rede separada sem precisar configurar manualmente cada etapa.

---

## 2. Endereçamento IPv4

O Vigilare utiliza o espaço privado:

```text
172.16.0.0/12
