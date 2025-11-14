#!/usr/bin/env python3
"""
Script Python para Executar Testes Automatizados
Alternativa ao run_tests.ps1 para ambientes Unix/Linux
"""

import sys
import subprocess
import time
import requests
from pathlib import Path

# Cores para terminal
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    print(f"{Colors.CYAN}🧪 Testes Automatizados - Clínica Saúde+{Colors.ENDC}")
    print(f"{Colors.CYAN}========================================={Colors.ENDC}")
    print()

def check_python():
    """Verificar versão do Python"""
    print(f"{Colors.YELLOW}📦 Verificando Python...{Colors.ENDC}")
    version = sys.version.split()[0]
    print(f"{Colors.GREEN}✅ Python {version}{Colors.ENDC}")
    print()

def check_dependencies():
    """Verificar se dependências estão instaladas"""
    print(f"{Colors.YELLOW}📦 Verificando dependências...{Colors.ENDC}")
    
    try:
        import selenium
        import pytest
        print(f"{Colors.GREEN}✅ Dependências OK{Colors.ENDC}")
    except ImportError:
        print(f"{Colors.YELLOW}⚠️  Instalando dependências...{Colors.ENDC}")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "tests/requirements-tests.txt"])
        print(f"{Colors.GREEN}✅ Dependências instaladas{Colors.ENDC}")
    print()

def check_docker():
    """Verificar se Docker está rodando"""
    print(f"{Colors.YELLOW}🐳 Verificando Docker...{Colors.ENDC}")
    
    try:
        result = subprocess.run(["docker-compose", "ps"], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"{Colors.YELLOW}⚠️  Iniciando Docker...{Colors.ENDC}")
            subprocess.run(["docker-compose", "up", "-d"])
            time.sleep(10)
        print(f"{Colors.GREEN}✅ Docker OK{Colors.ENDC}")
    except FileNotFoundError:
        print(f"{Colors.RED}❌ Docker não encontrado{Colors.ENDC}")
        sys.exit(1)
    print()

def check_frontend():
    """Verificar se frontend está acessível"""
    print(f"{Colors.YELLOW}🌐 Verificando Frontend...{Colors.ENDC}")
    
    try:
        response = requests.get("http://localhost:80", timeout=5)
        print(f"{Colors.GREEN}✅ Frontend acessível (porta 80){Colors.ENDC}")
    except requests.exceptions.RequestException:
        print(f"{Colors.RED}❌ Frontend não está respondendo{Colors.ENDC}")
        print(f"{Colors.YELLOW}   Execute: docker-compose up -d{Colors.ENDC}")
        sys.exit(1)
    print()

def check_backend():
    """Verificar se backend está acessível"""
    print(f"{Colors.YELLOW}🔧 Verificando Backend...{Colors.ENDC}")
    
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        print(f"{Colors.GREEN}✅ Backend acessível (porta 8000){Colors.ENDC}")
    except requests.exceptions.RequestException:
        print(f"{Colors.RED}❌ Backend não está respondendo{Colors.ENDC}")
        print(f"{Colors.YELLOW}   Execute: docker-compose up -d{Colors.ENDC}")
        sys.exit(1)
    print()

def show_menu():
    """Exibir menu de opções"""
    print(f"{Colors.CYAN}Escolha uma opção:{Colors.ENDC}")
    print("1. Executar TODOS os testes")
    print("2. Executar testes de CADASTRO")
    print("3. Executar testes de LOGIN")
    print("4. Executar testes de AGENDAMENTO")
    print("5. Executar testes de CANCELAMENTO")
    print("6. Executar testes de REAGENDAMENTO")
    print("7. Executar testes de VISUALIZAÇÃO")
    print("8. Executar teste específico (por número)")
    print("9. Gerar relatório HTML")
    print("0. Sair")
    print()

def run_tests(option):
    """Executar testes baseado na opção"""
    
    commands = {
        "1": ["pytest", "tests/test_interface_completo.py", "-v"],
        "2": ["pytest", "tests/test_interface_completo.py::TestCadastroPaciente", "-v"],
        "3": ["pytest", "tests/test_interface_completo.py::TestLoginPaciente", "-v"],
        "4": ["pytest", "tests/test_interface_completo.py::TestAgendamentoConsulta", "-v"],
        "5": ["pytest", "tests/test_interface_completo.py::TestCancelamentoConsulta", "-v"],
        "6": ["pytest", "tests/test_interface_completo.py::TestReagendamentoConsulta", "-v"],
        "7": ["pytest", "tests/test_interface_completo.py::TestVisualizacaoConsultas", "-v"],
    }
    
    if option in commands:
        print(f"\n{Colors.CYAN}🚀 Executando testes...{Colors.ENDC}\n")
        subprocess.run(commands[option])
    elif option == "8":
        numero = input("Digite o número do teste (ex: 010): ")
        print(f"\n{Colors.CYAN}🚀 Executando teste {numero}...{Colors.ENDC}\n")
        subprocess.run(["pytest", "tests/test_interface_completo.py", "-v", "-k", f"test_{numero}"])
    elif option == "9":
        print(f"\n{Colors.CYAN}🚀 Gerando relatório HTML...{Colors.ENDC}\n")
        subprocess.run(["pytest", "tests/test_interface_completo.py", "-v", 
                       "--html=report.html", "--self-contained-html"])
        print(f"\n{Colors.GREEN}✅ Relatório gerado: report.html{Colors.ENDC}")
        print(f"{Colors.YELLOW}   Abra o arquivo no navegador para visualizar{Colors.ENDC}")
    elif option == "0":
        print(f"\n{Colors.CYAN}👋 Até logo!{Colors.ENDC}\n")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}❌ Opção inválida{Colors.ENDC}\n")
        sys.exit(1)

def main():
    """Função principal"""
    print_header()
    check_python()
    check_dependencies()
    check_docker()
    check_frontend()
    check_backend()
    
    show_menu()
    option = input("Digite a opção: ")
    run_tests(option)
    
    print()
    print(f"{Colors.CYAN}========================================={Colors.ENDC}")
    print(f"{Colors.GREEN}✅ Execução concluída!{Colors.ENDC}")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Execução interrompida pelo usuário{Colors.ENDC}\n")
        sys.exit(0)
