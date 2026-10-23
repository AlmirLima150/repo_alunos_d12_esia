# Regras para Agentes — MiniLoja
- Verificações do contrato: `python -B testes/test_miniloja.py --codigo caso`
- Suíte existente e Golden Master: `python -B testes/test_miniloja.py --codigo caso --existentes`
- Mutação: `$env:MINILOJA_TEST_CMD="python -B testes/test_miniloja.py --existentes --codigo caso -x"; python -B testes/mutacao_manual.py`
- Limites invioláveis: nunca editar `testes/` nem `caso/regras.md`; em refatoração estrutural, se achar bug frente ao contrato, reporte sem corrigir.
- Convenção não óbvia: `testes/mutacao_manual.py` aplica `str.replace(velho, novo, 1)` sobre literais em `caso/miniloja/` (ex.: `"frete = 12.9"`, `"total > 200"`, `"desconto_aplicado = True"`); nunca repita esses literais em docstrings/comentários nem troque esses blocos por `.get()` sem autorização.
