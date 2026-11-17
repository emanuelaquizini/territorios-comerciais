"""Ponto de entrada usado pelo PyInstaller para gerar o executável."""

import sys

from contatos_territorio.cli import main

if __name__ == "__main__":
    sys.exit(main())
