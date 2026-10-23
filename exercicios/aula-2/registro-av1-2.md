# Registro individual — AV1.2

**Limite: uma página, incluindo evidências essenciais.** Estudante: Almir de Lima Felix dos Santos — Data: 23/10/2026
Origem: `caso/miniloja/calculo.py` fictício; modalidade: **execução própria** (com registro comparativo também das respostas simuladas `b2-rodada1-sem-escopo.md` e `b2-rodada2-com-escopo.md`).

**Golden master:** 140 entradas (produto cartesiano: 5 carrinhos × 7 estados de cupom [`None`, `PROMO10`, `VIP15`, `FRETEGRATIS`, `NATAL` com flag `0` e `1`, `CUPOM_X`] × 4 UFs [`PE`, `SP`, `RJ`, `BA`]); gerado sobre o `calculo.py` original antes de qualquer refatoração (commit `6826854` em `caso/testes_existentes/test_calculo.py`); comparação exata por `self.assertEqual(obtidos, esperados[c_id])` e `self.assertIsInstance(val, float)`, sem tolerância. Resultado antes da mudança e após a Rodada 2: `Ran 27 tests in 0.005s — OK`.

| Medida | Rodada 1 (sem escopo) | Rodada 2 (com escopo) |
| --- | --- | --- |
| Linhas adicionadas/removidas | `+39 / −65` em execução própria (simulada: `+412 / −187`) | `+35 / −15` em execução própria (simulada: `+58 / −41`) |
| Arquivos alterados (e quais estavam fora do esperado) | 2 arquivos: `calculo.py` e `descontos.py` fora do esperado (simulada: 9 arquivos, incluindo `utils.py`, `pedidos.py`, `handlers.py` e `test_calculo.py`) | 1 arquivo: apenas `caso/miniloja/calculo.py` (0 fora do esperado) |
| Mudou comportamento? (golden master) | **Sim, quebrou** (`FAILED (failures=2)`: `limite_200` `223.55` → `210.0`, `vazio` `13.54` → `13.55` e `C2` `223.12` → `223.13`) | **Não** (`Ran 27 tests in 0.005s — OK`, 140/140 cenários idênticos) |
| Tempo de revisão | ~12 min (inspeção de múltiplos arquivos, diagnóstico de quebras no Golden Master e `git checkout --` para descartar tudo) | ~3 min (diff localizado em 1 arquivo, 4 funções privadas extraídas na ordem de R1.6 e Golden Master verde de primeira) |
| Idas e vindas | 2 (1ª versão quebrou o Golden Master por corrigir `>= 200` e `Decimal`; descartada integralmente) | 1 (plano revisado antes de executar; código aprovado de primeira) |

**Escopo da rodada 2:**
- **objetivo:** extrair as etapas de `calcular_total` em `_calcular_subtotal`, `_aplicar_desconto`, `_calcular_frete` e `_aplicar_taxa`, na ordem de R1.6, preservando 100% do comportamento atual;
- **pode tocar:** apenas `caso/miniloja/calculo.py` (após gravar o Golden Master em `caso/testes_existentes/test_calculo.py`);
- **não pode tocar:** assinatura `calcular_total(itens, cupom=None, uf="PE")`, tipo de retorno `float`, `descontos.py`, `pedidos.py`, `handlers.py`, `caso/regras.md` e `testes/`;
- **invariantes:** 140 cenários do Golden Master com igualdade exata (`assertEqual` + `float`), 26 testes existentes verdes, 11 verificações mantendo `8 ok / 3 FAIL`, e preservação dos literais exigidos por `testes/mutacao_manual.py`;
- **pronto quando:** `python -B testes/test_miniloja.py --codigo caso --existentes` passar (`27/27 OK`) e o diff contiver apenas a extração estrutural em `calculo.py`;
- **pare e pergunte se:** encontrar divergência entre o código atual e o contrato `caso/regras.md` (deve apenas reportar, sem corrigir) ou se uma simplificação estrutural remover literais buscados pela ferramenta de mutação.

**Plano do agente: o que eu cortei ou corrigi antes de executar:**
1. **Cortei** a correção de `total > 200` para `>= 200` (R1.3) e a troca de `round(float)` por `Decimal` com `ROUND_HALF_UP` (R1.5), bem como o acoplamento com `descontos.py`: como provado na Rodada 1, essas mudanças alteram o comportamento observável e quebram o Golden Master.
2. **Corrigi** a proposta de substituir as cadeias `if/elif` por `FRETE_POR_UF.get()`/`TAXA_POR_UF.get()` e de remover `desconto_aplicado`: mantive as estruturas literais dentro das funções privadas para não quebrar os `assert velho in original` de `testes/mutacao_manual.py`.

**Algo que parecia bug e eu apenas reportei:**
1. **R1.3 (fronteira do frete grátis):** `calculo.py` usa `if total > 200:` em vez de `>= 200`, cobrando frete quando o subtotal com desconto é exatamente R$ 200,00 (em PE retorna `223.55` em vez de `210.0`).
2. **R1.5 (arredondamento meio para cima):** `calculo.py` usa `round(total, 2)` em `float` binário (arredondamento par/bancário), fazendo com que 2 itens de R$ 1,00 em PE retornem `15.64` em vez de `15.65` e carrinho vazio em PE retorne `13.54` em vez de `13.55`. Ambos foram apenas reportados na docstring/ADR e mantidos intactos na refatoração.

**`AGENTS.md` mínimo (6 linhas, gravado na raiz):**
```markdown
# Regras para Agentes — MiniLoja
- Verificações do contrato: `python -B testes/test_miniloja.py --codigo caso`
- Suíte existente e Golden Master: `python -B testes/test_miniloja.py --codigo caso --existentes`
- Mutação: `$env:MINILOJA_TEST_CMD="python -B testes/test_miniloja.py --existentes --codigo caso -x"; python -B testes/mutacao_manual.py`
- Limites invioláveis: nunca editar `testes/` nem `caso/regras.md`; em refatoração estrutural, se achar bug frente ao contrato, reporte sem corrigir.
- Convenção não óbvia: `testes/mutacao_manual.py` aplica `str.replace(velho, novo, 1)` sobre literais em `caso/miniloja/` (ex.: `"frete = 12.9"`, `"total > 200"`, `"desconto_aplicado = True"`); nunca repita esses literais em docstrings/comentários nem troque esses blocos por `.get()` sem autorização.
```

**Trecho essencial de evidência:**
- Rodada 1 (sem escopo): `python -B testes/test_miniloja.py --codigo caso --existentes` → `FAIL: test_cenarios_gravados ({'limite_200': 210.0, 'vazio': 13.55} != {'limite_200': 223.55, 'vazio': 13.54})` e `FAIL: test_golden_master_produto_cartesiano (First differing element 8: 223.13 != 223.12 — Divergência no carrinho C2) — FAILED (failures=2)`.
- Rodada 2 (com escopo, commit `9501a17` / `77b30e3`): `git diff --stat 6826854..9501a17` → `caso/miniloja/calculo.py | 50 (+35/-15)` e `python -B testes/test_miniloja.py --codigo caso --existentes` → `Ran 27 tests in 0.005s — OK`.

**Limite e condição para rever o escopo:** O Golden Master garante equivalência comportamental sobre as 140 combinações testadas, mas **congela também os defeitos atuais** (como os desvios de R1.3 em `total == 200` e de R1.5 em `float`/`round`) e não valida entradas fora do domínio (preços/quantidades negativos ou tipos inválidos). Eu ampliaria o escopo (permitindo alterar comportamento e atualizar os valores esperados do Golden Master de forma controlada) somente em uma tarefa funcional dedicada à correção dos bugs de R1.3 e R1.5, em commit separado da refatoração estrutural; e reduziria o escopo a uma única função auxiliar por commit se o módulo tivesse acoplamento externo sem cobertura de caracterização.

**Procedência/IA:** Ferramentas e modelos visíveis: Antigravity / Gemini 4 Argon e Claude Code / Claude Opus 5.5; tarefa delegada e contexto: geração da matriz de 140 cenários do Golden Master em `test_calculo.py`, execução da Rodada 1 sem escopo (descartada após falha no Golden Master) e da Rodada 2 com escopo revisado em `calculo.py`, além de contraste com as respostas simuladas (`b2-rodada1-sem-escopo.md` e `b2-rodada2-com-escopo.md`); trecho aproveitado: `test_golden_master_produto_cartesiano`, funções privadas `_calcular_subtotal`, `_aplicar_desconto`, `_calcular_frete` e `_aplicar_taxa` em `calculo.py` e arquivo `AGENTS.md`; minha verificação/intervenção: definição prévia dos 6 campos do escopo, corte das correções funcionais (`>= 200` e `Decimal`) e da troca por `.get()` no plano da Rodada 2, e execução da suíte de verificação e Golden Master. O raciocínio e a decisão registrados são meus.

**Revisão:** [x] golden master; [x] duas rodadas com números; [x] seis campos; [x] AGENTS.md; [x] até uma página.
