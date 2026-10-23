# Registro individual — AV2

**Limite: duas páginas de análise + anexo técnico curto.** Estudante: Almir de Lima Felix dos Santos — Data: 22/10/2026 — Caminho: B (MiniLoja)

## 1. Escopo e plano

**Escopo (seis campos, escrito antes da mudança):**
- **Objetivo:** extrair as etapas de `calcular_total` (`caso/miniloja/calculo.py`) em `_calcular_subtotal`, `_aplicar_desconto`, `_calcular_frete` e `_aplicar_taxa`, na ordem de R1.6, sem mudar nenhuma saída.
- **Pode tocar:** `calculo.py` e testes em `caso/testes_existentes/`.
- **Não pode tocar:** assinatura `calcular_total(itens, cupom=None, uf="PE")`, demais módulos, tipo `float`, `caso/regras.md`, `testes/`.
- **Invariantes:** golden master de 140 cenários com igualdade exata e tipo `float`; os 26 testes originais verdes; as 11 verificações seguem 8 ok e 3 falhas; trechos literais que `testes/mutacao_manual.py` procura continuam presentes.
- **Pronto quando:** `--existentes` passa (32 testes), verificações inalteradas e mutação com só o mutante equivalente sobrevivendo.
- **Pare e pergunte se:** aparecer divergência com o contrato (reportar, não corrigir) ou uma mudança estrutural quebrar o casador textual da mutação.

**Plano do agente — o que cortei ou corrigi:**
1. **Cortei** a correção `> 200` → `>= 200` (R1.3) e a migração para `Decimal` (R1.5): mudariam comportamento (`223.55` → `210.00` no carrinho de R$ 200,00 em PE) e invalidariam o oráculo.
2. **Cortei** alterações em `pedidos.py`: a assinatura foi mantida, nenhum chamador precisa mudar.
3. **Corrigi** a troca de `if/elif` por `FRETE_POR_UF.get()` e a remoção de `desconto_aplicado`: `mutacao_manual.py` faz `assert velho in original` com trechos literais (`"frete = 12.9"`, `"desconto_aplicado = True"`) e não pode ser editado. As estruturas ficaram dentro das funções novas, com comentário explicando o motivo.

## 2. Comportamento preservado

- **Método:** golden master `test_golden_master_produto_cartesiano` (`test_calculo.py`), `assertEqual` exato e `assertIsInstance(float)`.
- **Entradas:** 140 cenários = 5 carrinhos (R$ 130; R$ 250; 3 × R$ 19,99; fronteira de 2 × R$ 100,00; vazio) × 7 estados de cupom (nenhum, PROMO10, VIP15, FRETEGRATIS, NATAL com flag 0 e 1, inválido) × 4 UFs (PE, SP, RJ, BA).
- **Prova de que o oráculo veio antes:** commit `6826854` contém só o golden master sobre o `calculo.py` original: `Ran 27 tests — OK`. A refatoração entra depois, em `77b30e3`, com o mesmo resultado.
- **Sensibilidade:** sabotei a ordem das operações (`total + imposto` → `total * (1 + taxa)`, matematicamente igual): `test_golden_master_produto_cartesiano` e `test_cenarios_gravados` falham. O golden master pega diferença de último dígito em `float`.
- **Comando e saída:** `python -B testes/test_miniloja.py --codigo caso --existentes` → `Ran 32 tests — OK`; `python -B testes/test_miniloja.py --codigo caso` → 8 ok, 3 falhas (v08, v09, v10, inalteradas).

## 3. Suíte com verificação real

| Teste (origem) | Prova de que falharia | Resultado |
| --- | --- | --- |
| `test_cupom_natal_com_flag` (R1.2–R1.4: (100 × 0,80 + 21,50) × 1,06 = **107,59**) | mutante NATAL 20% → 21% (antes só havia `assertIsNotNone`) | morto (106,53) |
| `test_frete_rj_sem_cupom` (R1.3–R1.4: (100 + 21,50) × 1,06 = **128,79**) | mutante frete RJ 21,5 → 22,5 | morto (129,85) |
| `test_aplicar_desconto` / `_vip15` (R1.2: 200 → **180,00** e **170,00**, valor fixo, não espelho) | mutante VIP15 15 → 5 | morto (190,00) |
| `test_reservar_exatamente_todo_o_saldo_disponivel` (R2.2: saldo 10, reserva 10 → saldo 0) | mutante `<` → `<=` | morto |
| `test_cadastro_sem_email_e_rejeitado` (R3.1: sem e-mail é rejeitado; exige só `status != 201`, porque R3.4 pede 422 e o código dá 400) | mutante `if False:` | morto (201) |
| `test_criar_pedido_real_persiste_total_e_formatacao` (R1 + R2, sem mock: 118,55 e `"R$ 118,55"`) | mutante `moeda(0)` | morto |
| `test_resumo_vendas` / `test_simular_desconto` — **caracterização, não contrato**: congelam o `_fmt` atual (`"R$ 30,12"`, `"R$ 90,0"`); por R1.5 seria `"R$ 30,13"` | mutante `round(v, 3)` | morto (`"R$ 30,125"`) |

**Mutação:** `$env:MINILOJA_TEST_CMD = "python -B testes/test_miniloja.py --existentes --codigo caso -x"; python -B testes/mutacao_manual.py` → antes `31 | mortos: 23 | sobreviventes: 8 | 74%`; depois `31 | mortos: 30 | sobreviventes: 1 | 97%`. **Sobrevivente equivalente:** `desconto_aplicado = True` → `False` não afeta o retorno (`if desconto_aplicado: pass`), logo nenhum teste de comportamento consegue matá-lo.

## 4. Documentação, ADR, erros da IA e limites

**ADR — divergências R1.3 e R1.5 mantidas na refatoração** (registrado também na docstring de `calculo.py`):
- **Contexto:** o código cobra frete em R$ 200,00 exatos (`> 200`, R1.3 pede `>=`) e usa `round()` sobre `float` (R1.5 pede meio para cima): 2 itens de R$ 1,00 em PE dão 15,64, não 15,65, porque 15,645 não tem representação exata em binário.
- **Decisão:** preservar ambos nesta refatoração e documentar; corrigir em mudança funcional própria (AV3 B2).
- **Consequências:** refatoração separada de mudança de comportamento; os dois desvios continuam ativos e congelados no golden master.
- **Alternativa:** corrigir no mesmo commit; rejeitada porque invalidaria o oráculo.

**O que a IA errou (o quê, onde, como detectei):**
1. **Antigravity — docstring absorveu a mutação** (`calculo.py`): escreveu os literais `total > 200` e `preco * qtd` na docstring; como `mutacao_manual.py:78` usa `replace(velho, novo, 1)`, o mutante alterava o comentário e "sobrevivia". Detectei por um sobrevivente inesperado; removi os literais.
2. **Antigravity — `float` no teste** (`test_relatorios.py`): propôs `10.124 + 20.0 == 30.124`, que falha (`30.124000000000002`). Troquei por `10.125`, exato em binário.
3. **Antigravity — rótulo de contrato falso** (`test_relatorios.py`): apresentou como derivados de R1.5 testes que afirmam o contrário de R1.5. Detectado na revisão cruzada; reclassificados como caracterização.
4. **Antigravity — teste congelava divergência** (`test_cadastro.py`): fixava `400`, contra R3.4 (422); quebraria ao corrigir o cadastro. Trocado por `assertNotEqual(status, 201)`; o mutante segue morto.
5. **Antigravity — números do anexo** errados (`calculo.py` +37/−21; real +35/−15).
6. **Claude Code — contestação errada na revisão:** contestou o 15,64 do ADR com conta própria (multiplicou por 1,05 em vez de somar `total * taxa`). Refutei executando o código: 15,64.

**Limite e condição para rever:** a suíte não cobre entradas fora do domínio (`preco` ou `qtd` negativos, tipos inválidos) nem a reserva não desfeita (R2.2) e o acesso (R4); o golden master preserva os desvios de R1.3 e R1.5 de propósito; a forma da refatoração ficou limitada pelos trechos literais da ferramenta de mutação (`FRETE_POR_UF`/`TAXA_POR_UF` seguem sem uso). Rever o ADR e atualizar o golden master de propósito quando for aberta a correção de R1.3/R1.5.

**Procedência/IA:** ferramentas e modelos: Antigravity com o modelo Argon 4 e Claude Code com Claude Opus 5.5 (revisão cruzada e correções); execução local, Python 3.11.9, Windows, branch `av2-refatoracao`. Tarefa delegada: extração das funções, matriz do golden master e testes para os mutantes; o Claude Code revisou cada afirmação executando, corrigiu os itens 3 e 4, comentou o código mantido por causa da mutação e organizou os commits. Trecho aproveitado: estrutura de `calculo.py` e testes. Minha verificação/intervenção: cortei do plano as mudanças funcionais (`>= 200` e `Decimal`); detectei a colisão da docstring com `replace(..., 1)` da mutação; ajustei a fronteira `qtd == saldo` em `test_estoque.py` e o `10.125` em `test_relatorios.py`; conferi as correções da revisão cruzada rodando as suítes e a mutação. O raciocínio e a decisão registrados são meus.

---

## Anexo técnico

**Commits (`git log --oneline main..av2-refatoracao`):** `6826854` golden master sobre o código original · `77b30e3` refatoração · `3771cce` testes novos.

**Diff (`git diff --numstat main`):** 7 arquivos, +114/−23 — `calculo.py` +35/−15; `test_calculo.py` +46/−2; `test_relatorios.py` +7/−3; `test_cadastro.py` +7; `test_pedidos.py` +8; `test_estoque.py` +6; `test_descontos.py` +5/−3.

**Trechos dos testes:**
```python
# test_calculo.py — R1.2 a R1.4
resultado = calcular_total([{"preco": 100.0, "qtd": 1}], "NATAL", "RJ")  # flag = "1"
self.assertEqual(resultado, 107.59)
self.assertEqual(calcular_total([{"preco": 100.0, "qtd": 1}], None, "RJ"), 128.79)

# test_cadastro.py — R3.1, sem congelar 400 x 422
status, _ = cadastro.cadastrar_cliente({"nome": "Ana"})
self.assertNotEqual(status, 201)

# test_estoque.py — fronteira qtd == saldo
self.assertTrue(e.reservar("BOLA-01", 10, "p1"))
self.assertEqual(e.saldo("BOLA-01"), 0)
```

**Revisão:** [x] escopo; [x] comportamento; [x] testes com prova; [x] documentação; [x] erros da IA; [x] limite.
