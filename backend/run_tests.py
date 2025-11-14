"""
Script otimizado para executar testes com performance máxima
Uso: python run_tests.py [opções]

Opções:
  --fast     : Executa apenas testes rápidos (unit + integration)
  --full     : Executa todos os testes incluindo performance
  --parallel : Ativa paralelização (requer pytest-xdist)
  --coverage : Gera relatório de cobertura (requer pytest-cov)
  --verbose  : Modo verbose detalhado
"""
import sys
import subprocess
import time
from pathlib import Path


def main():
    args = sys.argv[1:]
    
    # Comando base
    cmd = ["pytest", "tests/", "-v", "--tb=short", "--color=yes"]
    
    # Parse argumentos
    if "--fast" in args:
        cmd.extend(["-m", "not performance", "--maxfail=3"])
        print("🚀 Modo RÁPIDO: Executando testes unitários e de integração")
    
    elif "--full" in args:
        print("🔬 Modo COMPLETO: Executando TODOS os testes")
    
    if "--parallel" in args:
        try:
            import xdist
            cmd.extend(["-n", "auto"])
            print("⚡ Paralelização ATIVADA (pytest-xdist)")
        except ImportError:
            print("⚠️  pytest-xdist não instalado. Execute: pip install pytest-xdist")
    
    if "--coverage" in args:
        try:
            import pytest_cov
            cmd.extend(["--cov=app", "--cov-report=term", "--cov-report=html"])
            print("📊 Cobertura de código ATIVADA")
        except ImportError:
            print("⚠️  pytest-cov não instalado. Execute: pip install pytest-cov")
    
    if "--verbose" in args:
        cmd.extend(["-vv", "--durations=20"])
        print("📝 Modo VERBOSE ativado")
    
    # Adicionar contadores
    cmd.extend(["--durations=10"])
    
    print("=" * 70)
    print("🧪 INICIANDO TESTES AUTOMATIZADOS")
    print("=" * 70)
    print(f"Comando: {' '.join(cmd)}")
    print()
    
    # Executar testes
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        exit_code = result.returncode
    except KeyboardInterrupt:
        print("\n❌ Testes interrompidos pelo usuário")
        return 1
    
    elapsed_time = time.time() - start_time
    
    # Resumo
    print()
    print("=" * 70)
    print(f"⏱️  Tempo total: {elapsed_time:.2f}s")
    
    if exit_code == 0:
        print("✅ TODOS OS TESTES PASSARAM!")
    else:
        print(f"❌ FALHAS DETECTADAS (código {exit_code})")
    
    print("=" * 70)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
