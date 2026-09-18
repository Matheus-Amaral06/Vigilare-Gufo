#!/usr/bin/env bash

set -euo pipefail

echo "========================================"
echo "        VIGILARE - INSTALADOR"
echo "========================================"
echo

if [[ "${EUID}" -eq 0 ]]; then
    echo "Nao execute este instalador como root."
    echo "Execute normalmente: ./install.sh"
    exit 1
fi

if ! command -v sudo >/dev/null 2>&1; then
    echo "ERRO: sudo nao esta instalado."
    exit 1
fi

if ! sudo -v; then
    echo "ERRO: nao foi possivel validar o sudo."
    exit 1
fi

if [[ ! -f /etc/os-release ]]; then
    echo "ERRO: nao foi possivel identificar a distribuicao Linux."
    exit 1
fi

source /etc/os-release

case "${ID:-}" in
    arch)
        echo "Distribuicao detectada: Arch Linux"
        echo

        PACOTES=(
            iproute2
            iptables
            dnsmasq
            dhcpcd
            iputils
        )

        echo "Instalando dependencias do sistema..."
        sudo pacman -Sy --needed "${PACOTES[@]}"

        echo
        echo "Criando diretorio do dnsmasq..."
        sudo mkdir -p /etc/dnsmasq.d

        echo
        echo "Configurando carregamento das configuracoes do Vigilare..."

        DNSMASQ_CONF="/etc/dnsmasq.conf"
        DIRETIVA="conf-dir=/etc/dnsmasq.d/,*.conf"

        if ! sudo grep -Eq "^[[:space:]]*${DIRETIVA//\*/\\*}[[:space:]]*$" "$DNSMASQ_CONF"; then
            if sudo grep -Eq "^[[:space:]]*#[[:space:]]*conf-dir=/etc/dnsmasq\\.d/,\\*\\.conf[[:space:]]*$" "$DNSMASQ_CONF"; then
                sudo sed -i \
                    's|^[[:space:]]*#[[:space:]]*conf-dir=/etc/dnsmasq\.d/,\*\.conf[[:space:]]*$|conf-dir=/etc/dnsmasq.d/,*.conf|' \
                    "$DNSMASQ_CONF"
            else
                echo "conf-dir=/etc/dnsmasq.d/,*.conf" | sudo tee -a "$DNSMASQ_CONF" >/dev/null
            fi
        fi

        echo
        echo "Validando configuracao do dnsmasq..."
        sudo dnsmasq --test

        echo
        echo "Habilitando o servico dnsmasq..."
        sudo systemctl enable dnsmasq

        echo
        echo "========================================"
        echo "Instalacao concluida!"
        echo "========================================"
        echo
        echo "Dependencias instaladas:"
        printf '  - %s\n' "${PACOTES[@]}"
        echo
        echo "O dnsmasq foi preparado para carregar:"
        echo "  /etc/dnsmasq.d/*.conf"
        echo
        echo "Nenhuma quarentena foi criada."
        echo "Nenhuma regra de firewall foi adicionada."
        echo "Nenhuma rota foi alterada."
        echo
        echo "Agora use:"
        echo "  poetry install"
        echo "  poetry run vigilare"
        ;;

    *)
        echo "ERRO: distribuicao nao suportada: ${ID:-desconhecida}"
        echo
        echo "Por enquanto, o instalador suporta:"
        echo "  - Arch Linux"
        exit 1
        ;;
esac
