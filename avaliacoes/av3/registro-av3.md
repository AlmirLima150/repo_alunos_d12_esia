# Registro individual — AV3

**Limite: três páginas + até duas de evidências.** Estudante: Almir de Lima Felix dos Santos — Data: 25/10/2026 — Caminho: B (MiniLoja: **B3** — corrigir a reserva de estoque que não é desfeita quando um item falha, R2.2, com teste de regressão)

---

## 1. Modo de interação e justificativa

- **Modo de interação usado e por quê (raio de impacto, oráculo, familiaridade):** **Modo Agente supervisionado por escopo e revisão de plano** (Antigravity / Gemini 4 Argon com execução local em branch isolada `av3-b3`).
  - **Raio de impacto:** baixo e reversível, restrito a dois módulos em memória (`caso/miniloja/estoque.py` e `caso/miniloja/pedidos.py`) e três arquivos de teste (`test_estoque.py`, `test_pedidos.py` e `test_handlers.py`), versionados no Git sem efeitos externos.
  - **Oráculo:** forte, rápido e determinístico (`< 0,01s`), composto pelos novos testes de regressão derivados de `R2.2` (`caso/regras.md:21`), pela suíte existente com Golden Master de 140 cenários (`--existentes`, 37 testes) e pela ferramenta de mutação (`testes/mutacao_manual.py`, 31 mutantes).
  - **Familiaridade:** alta, pois a arquitetura de `miniloja`, as convenções de `AGENTS.md` e as restrições de literais de `mutacao_manual.py` já foram mapeadas nos blocos B1–B5 e na AV2.
- **Alternativa comparada:** **Modo Chat (copiar/colar trechos manualmente)** e **Modo Agente autônomo sem escopo prévio**.
  - Em comparação ao **Modo Chat** (experimentado na AV1.1 T1-B, onde levou `6 min` e `2` idas e vindas por rodar a suíte com o arquivo ainda não salvo no disco), o Agente supervisionado elimina o erro operacional de colagem/salvamento e executa imediatamente o ciclo *Red → Green → Mutação*.
  - Em comparação ao **Agente sem escopo prévio** (experimentado na AV1.2 Rodada 1, que tocou arquivos fora do alvo e quebrou invariantes), exigir os 6 campos de escopo e revisar o plano antes da edição conteve o diff de produção em apenas `+22 / −3` linhas.

---

## 2. Escopo declarado antes, plano revisado e PR revisável

**Escopo declarado antes (seis campos):**
- **Objetivo:** Corrigir `PedidoService.criar` (`caso/miniloja/pedidos.py`) e `Estoque` (`caso/miniloja/estoque.py`) para cumprir `R2.2` (`caso/regras.md:21`: *"Todos os itens precisam ter estoque. Se algum não tiver, o pedido é recusado (`409`) e nenhuma reserva pode permanecer"*), desfazendo todas as reservas já realizadas no pedido caso um item subsequente lance `EstoqueInsuficiente`, acompanhado de testes de regressão.
- **Pode tocar:** `caso/miniloja/estoque.py`, `caso/miniloja/pedidos.py`, `caso/testes_existentes/test_estoque.py`, `caso/testes_existentes/test_pedidos.py`, `caso/testes_existentes/test_handlers.py` e `avaliacoes/av3/registro-av3.md`.
- **Não pode tocar:** `testes/` (`test_miniloja.py`, `mutacao_manual.py`), `caso/regras.md`, `caso/requirements.txt`, `calculo.py`, `cadastro.py`, `descontos.py`, `formatacao.py`, `relatorios.py`, `handlers.py` e as assinaturas públicas existentes (`Estoque.reservar`, `Estoque.saldo`, `PedidoService.criar`).
- **Invariantes:**
  1. Os literais exatos exigidos por `testes/mutacao_manual.py:40-47` em `estoque.py` (`"if disponivel < qtd:"`, `"disponivel - qtd"`) e em `pedidos.py` (`'if cobranca["status"] != "aprovado":'`, `'"total_fmt": moeda(total)'`, `"if not itens:"`) devem permanecer intactos e sem duplicação em docstrings/comentários;
  2. Os testes legados com `MagicMock` em `test_pedidos.py` (`test_criar_pedido` e `test_fluxo_chama_colaboradores`, que verifica `estoque.reservar.called`) devem continuar passando;
  3. O Golden Master de 140 cenários e o escore de mutação de `97%` (`30/31` mortos, `1` equivalente) devem ser preservados; zero dependências novas.
- **Pronto quando:** (1) os testes de regressão de `R2.2` falharem antes da correção (commit atômico *Red*) e passarem após a correção (commit atômico *Green*); (2) `--existentes` passar com `37/37 OK`; (3) `mutacao_manual.py` mantiver `30/31` mortos (`97%`); e (4) a barreira `git diff --name-only` confirmar que nenhum arquivo fora da lista permitida foi alterado.
- **Pare e pergunte se:** a correção exigir alterar `handlers.py`, quebrar mocks existentes em `test_pedidos.py` ou colidir com os casadores textuais de `mutacao_manual.py`.

**Plano revisado e sequência de commits atômicos (mudança revisável):**
1. **Commit 1 (`23d84fb` — *Red*):** Adiciona 5 testes de regressão em `test_estoque.py`, `test_pedidos.py` e `test_handlers.py` cobrindo: liberação unitária de reserva, acúmulo de reservas repetidas do mesmo `(pedido_id, sku)` com liberação parcial, rollback completo quando o 3º item falha em `PedidoService.criar`, isolamento de reservas de pedidos anteriores já pagos do mesmo `usuario_id` (`"tmp-1"`), e retorno HTTP `409` em `post_pedidos` sem vazar reserva do 1º item.
2. **Commit 2 (`2ec06d3` — *Green*):** Em `Estoque.reservar` (`estoque.py:19-20`), acumula `self.reservas[chave] = self.reservas.get(chave, 0) + qtd` e adiciona `Estoque.liberar(sku, qtd, pedido_id)` (`estoque.py:23-31`) restaurando `self.saldos[sku]` e abatendo/removendo `self.reservas[(pedido_id, sku)]`. Em `PedidoService.criar` (`pedidos.py:22-31`), empilha cada `(sku, qtd)` efetivamente reservado em `reservados` dentro de `try/except EstoqueInsuficiente:` e, ao falhar, desfaz em ordem reversa (`reversed(reservados)`) via `self.estoque.liberar(...)` antes de relançar a exceção.
3. **Commit 3 (este arquivo):** Documenta o PR, as evidências de verificação, os erros da IA e o desenho de medição e automação.

**Cumprido? Como verifiquei (comando e barreira de escopo):**
- **Sim.** Barreira executada: `git diff --numstat main..2ec06d3` (código + testes):
  - `caso/miniloja/estoque.py`: `+12 / −1`
  - `caso/miniloja/pedidos.py`: `+10 / −2`
  - `caso/testes_existentes/test_estoque.py`: `+20 / −0`
  - `caso/testes_existentes/test_handlers.py`: `+16 / −0`
  - `caso/testes_existentes/test_pedidos.py`: `+37 / −1`
  - **Total:** 5 arquivos (100% dentro de "Pode tocar"), `+22 / −3` linhas de produção e `+73 / −1` linhas de teste.

---

## 3. Verificação efetiva (teste que falharia sem a mudança)

- **Testes principais que falhariam sem a mudança:**
  - `test_falha_em_item_subsequente_desfaz_reservas_anteriores_r2_2` (`test_pedidos.py:49-65`): estoque inicial `{"BOLA-01": 10, "CAMISA-M": 5, "CHUTEIRA-42": 1}`; pedido solicita 3 `BOLA-01`, 2 `CAMISA-M` e 5 `CHUTEIRA-42`. O 3º item lança `EstoqueInsuficiente("CHUTEIRA-42")`; o teste exige `saldo("BOLA-01") == 10`, `saldo("CAMISA-M") == 5`, `saldo("CHUTEIRA-42") == 1` e `estoque.reservas == {}`.
  - `test_rollback_nao_desfaz_reserva_de_pedido_anterior_do_mesmo_usuario` (`test_pedidos.py:67-83`): `usuario_id=1` conclui um 1º pedido reservando 2 `BOLA-01` (`saldo == 8`, `reservas[("tmp-1", "BOLA-01")] == 2`); em seguida, tenta um 2º pedido com 3 `BOLA-01` e 5 `CHUTEIRA-42` (que falha). O teste exige que o rollback devolva apenas as 3 unidades da tentativa falha, mantendo `saldo("BOLA-01") == 8` e `reservas[("tmp-1", "BOLA-01")] == 2`.
  - `test_post_pedidos_409_desfaz_reserva_dos_itens_anteriores` (`test_handlers.py:28-42`): via handler HTTP `post_pedidos`, exige status `409` e saldo de `BOLA-01` inalterado (`48 == 48`).
- **Prova 1 — Execução ANTES da mudança (commit `23d84fb` sobre o código original):**
  - Comando: `python -B testes/test_miniloja.py --codigo caso --existentes`
  - Saída observada: `Ran 37 tests in 0.007s — FAILED (failures=4, errors=1)`:
    - `FAIL: test_falha_em_item_subsequente_desfaz_reservas_anteriores_r2_2` → `AssertionError: 7 != 10` (3 unidades de `BOLA-01` ficaram presas na reserva órfã).
    - `FAIL: test_post_pedidos_409_desfaz_reserva_dos_itens_anteriores` → `AssertionError: 44 != 48` (4 unidades de `BOLA-01` vazaram após o `409`).
    - `FAIL: test_rollback_nao_desfaz_reserva_de_pedido_anterior_do_mesmo_usuario` → `AssertionError: 5 != 8`.
    - `FAIL: test_reservar_mesmo_sku_acumula_e_liberar_parcial_preserva_anterior` → `AssertionError: 3 != 5` (`reservar` sobrescrevia `self.reservas[(pedido_id, sku)] = qtd` em vez de acumular).
    - `ERROR: test_liberar_restaura_saldo_e_remove_reserva` → `AttributeError: 'Estoque' object has no attribute 'liberar'`.
- **Prova 2 — Execução DEPOIS da mudança (commit `2ec06d3`):**
  - `python -B testes/test_miniloja.py --codigo caso --existentes` → `Ran 37 tests in 0.004s — OK`.
  - `$env:MINILOJA_TEST_CMD="python -B testes/test_miniloja.py --existentes --codigo caso -x"; python -B testes/mutacao_manual.py` → `Mutantes: 31 | mortos: 30 | sobreviventes: 1 | escore: 97%` (`SOBREVIVEU calculo.py: variável sem efeito (mutante equivalente)`).
- **Prova 3 — Sabotagem manual do rollback:** comentando `self.estoque.liberar(sku, qtd, pedido_id=pedido_id)` em `pedidos.py:30`, a suíte falha imediatamente em `test_falha_em_item_subsequente_desfaz_reservas_anteriores_r2_2` (`AssertionError: 7 != 10`), `test_rollback_nao_desfaz_reserva_de_pedido_anterior_do_mesmo_usuario` (`5 != 8`) e `test_post_pedidos_409_desfaz_reserva_dos_itens_anteriores` (`44 != 48`).

---

## 4. Honestidade sobre os erros da IA e justificativa técnica das correções

| O que a IA errou (o quê, onde) | Como detectei | O que corrigi e por quê (causa e impacto) |
| --- | --- | --- |
| **1. Pré-validação com `self.estoque.saldo(sku) < qtd` em `PedidoService.criar` (`caso/miniloja/pedidos.py:22`) antes de reservar:** a primeira abordagem sugerida para evitar reservas parciais foi checar `if self.estoque.saldo(i["sku"]) < i["qtd"]: raise EstoqueInsuficiente(i["sku"])` num primeiro laço antes de chamar `self.estoque.reservar`. | Na revisão do plano cruzada com `caso/testes_existentes/test_pedidos.py:14,21` (`test_criar_pedido` e `test_fluxo_chama_colaboradores`) e confirmação em execução: em Python 3, quando `self.estoque` é um `MagicMock()` sem `return_value` numérico configurado para `saldo()`, a comparação `MagicMock() < 1` lança `TypeError: '<' not supported between instances of 'MagicMock' and 'int'`, quebrando os dois testes existentes. Além disso, falharia se o mesmo SKU aparecesse duas vezes no pedido somando mais que o saldo (`[qtd=6, qtd=6]` para `saldo=10`). | **Correção:** descartar a pré-validação por `saldo()` em `pedidos.py` e adotar **rollback compensatório** (`try/except EstoqueInsuficiente:` chamando `self.estoque.liberar` sobre a lista `reservados`). **Causa e impacto:** `test_pedidos.py` injeta `MagicMock()` como dublê de `Estoque` e verifica `estoque.reservar.called`; delegar a verificação de saldo exclusivamente a `reservar()` e compensar via `liberar()` apenas quando `EstoqueInsuficiente` ocorre preserva 100% de compatibilidade com os mocks e trata corretamente múltiplos itens do mesmo SKU no pedido. |
| **2. Estorno ingênuo por `pedido_id=f"tmp-{usuario_id}"` varrendo `self.reservas` (`caso/miniloja/estoque.py:19` e `pedidos.py:23`):** a proposta de criar `Estoque.cancelar_reservas(pedido_id)` removendo todas as chaves `(p_id, sku)` de `self.reservas` onde `p_id == f"tmp-{usuario_id}"` e devolvendo `qtd` ao saldo. | Ao inspecionar `pedidos.py:23-36` e o teste `test_rollback_nao_desfaz_reserva_de_pedido_anterior_do_mesmo_usuario`: `PedidoService.criar` usa o identificador fixo `pedido_id=f"tmp-{usuario_id}"` para todas as compras do mesmo usuário e nunca remove `("tmp-1", sku)` após um pedido pago. | **Correção:** em `pedidos.py:23-31`, rastrear na variável local `reservados = []` exatamente os pares `(sku, qtd)` reservados naquela chamada de `criar()`, e em `estoque.py:19-31` acumular `self.reservas[chave] = self.reservas.get(chave, 0) + qtd` em `reservar` e subtrair apenas `qtd` em `liberar(sku, qtd, pedido_id)`. **Causa e impacto:** se `liberar` varresse `self.reservas` por `"tmp-1"`, um 2º pedido com falha do usuário `1` estornaria as unidades já compradas e pagas no 1º pedido dele, inflando indevidamente o estoque disponível; além disso, a atribuição simples `self.reservas[chave] = qtd` (`estoque.py:19`) sobrescrevia a quantidade anterior, perdendo o rastro de múltiplas reservas do mesmo SKU. |
| **3. Comportamento de `git checkout` entre branches com arquivos não rastreados (durante a preparação do repositório para a AV3):** ao alternar de `bloco5_pr` para `bloco4_legado` para commitar a AV1.4 após commitar a AV1.5, o agente deixou a árvore de trabalho posicionada em `bloco4_legado`, fazendo com que `exercicios/aula-5/registro-av1-5.md` e `apoio/pr-bloco5/` deixassem de aparecer no diretório local. | O estudante notou imediatamente a ausência dos arquivos da Aula 5 no workspace e pediu para salvá-los na árvore principal. | **Correção:** voltar para a branch `main`, consolidar os arquivos de `av1-4`, `av1-5`, `av1-6` e `av2-refatoracao` na `main` (commits `fae64b2`, `e2fc04a` e `0abc7f2`) antes de criar a branch `av3-b3`. **Causa e impacto:** como `bloco4_legado` e `bloco5_pr` divergiram de `upstream/main`, manter o checkout em uma branch lateral ocultava as demais entregas no workspace local; consolidar na `main` garantiu que a branch `av3-b3` partisse de uma base unificada onde `git diff main..av3-b3` exibe exclusivamente as mudanças da AV3. |

**Dependências novas (se houver) e checagem:** **Nenhuma.** `caso/requirements.txt` permanece intacto (`# Sem dependências externas. A MiniLoja usa apenas a biblioteca padrão do Python.`); verificado via `git diff main..av3-b3 -- caso/requirements.txt` (vazio).

---

## 5. Medição do time e tarefa candidata a automação

| Medição do meu time | Meu desenho |
| --- | --- |
| **Pergunta e decisão** | **Pergunta:** O uso de agentes de codificação guiados por escopo prévio (6 campos + `AGENTS.md`) reduz o tempo até "pronto e verificado" em tarefas de manutenção sem reduzir o escore de mutação nem aumentar o retrabalho de revisão? **Decisão:** Padronizar e renovar o uso do agente para tarefas P/M no time backend (5 pessoas, sprints quinzenais) exigindo contrato de escopo e verificação no PR, ou restringir a IA ao modo Chat consultivo. |
| **Métrica primária e guardrail** | **Primária:** Mediana do *lead time até "pronto e verificado"* por tarefa concluída (da abertura ao PR aprovado com suíte verde) + *tempo de revisão humana* do diff. **Guardrails:** (1) Escore de mutação nos módulos tocados `>= 95%` dos mutantes não-equivalentes; (2) Violação de escopo `= 0` arquivos fora da lista "pode tocar" e `0` dependências não autorizadas; (3) Taxa de reversão/defeito pós-merge não superior ao baseline. |
| **Baseline, período e método** | **Baseline em miniatura do curso:** em **AV1.1**, Agente levou `3–5 min` (`1` ida e volta) vs. Chat `6 min` (`2` idas e vindas por arquivo não salvo); em **AV1.2**, sem escopo (Rodada 1) gerou `+39/−65` em 2 arquivos (simulada: `+412/−187` em 9 arquivos), quebrou o Golden Master e gastou `~12 min` de revisão para descarte total (`2` idas e vindas), enquanto com escopo de 6 campos (Rodada 2) gerou `+35/−15` em 1 arquivo (`0` fora do escopo) e levou `~3 min` de revisão (`1` ida e volta); em **AV1.3/AV2**, o escore de mutação subiu de `74%` (`23/31`) para `97%` (`30/31`, `1` equivalente); nesta **AV3 (B3)**, com escopo e plano revisados antes, o diff de produção ficou em `+22/−3` linhas (2 arquivos) com `37/37` testes verdes e `97%` na mutação. **No time:** histórico das últimas 8 semanas (4 sprints, ~40 PRs) comparado a 6 semanas (3 sprints, ~30 tarefas P/M) por mediana e P75 estratificados por tipo (bugfix, refatoração, testes). |
| **Risco de manipulação e contramedida** | **Risco (Lei de Goodhart):** (a) Fatiar uma tarefa em micro-PRs artificiais para baixar a mediana por PR; (b) aprovar PR de agente no escuro ("LGTM" rápido sem rodar testes nem auditar o diff, deixando passar quebras de contrato como R4, `except: pass` ou pacotes alucinados vistos na AV1.5); (c) inflar cobertura com testes tautológicos (`assertIsNotNone`, mocks que testam o mock ou snapshots do bug vistos na AV1.3). **Contramedida:** medir o ciclo pela **tarefa completa de negócio** (não por PR fatiado), travar o CI no escore de mutação e na barreira `git diff --name-only`, exigir na descrição do PR a saída do **teste que falharia sem a mudança** e auditar quinzenalmente uma amostra de PRs em revisão cruzada. |
| **Tarefa recorrente a automatizar e verificação exigida** | **Tarefa:** Caça a mutantes sobreviventes nos módulos alterados a cada PR interno (~8–10 PRs/semana; custo manual atual de ~25–35 min/PR), gerando **apenas uma proposta de patch** com testes derivados do contrato (ou classificação de mutante equivalente). **Verificação determinística antes de exibir a proposta:** (1) o teste proposto passa no código atual (`exit code 0`); (2) o teste proposto **falha** quando o mutante sobrevivente é injetado (provando que mata o mutante); (3) barreira `git diff --name-only` restrita a `test_*.py` (proibido tocar produção, `regras.md`, `requirements.txt` ou `testes/`); (4) se falhar no código atual, apenas reportar divergência código × contrato sem alterar o valor esperado. **Permissões e orçamento:** `read-only` no código, comentário apenas em PR de branch interna (**nunca** em PR de fork externo nem com segredos de deploy), container sem rede (`--network=none`), timeout de `5 min`, máximo de `2` tentativas e teto de `US$ 0,40` por PR. **Responsável:** autor do PR + revisor humano. |

---

## 6. Limites, condição para rever e procedência

- **Limites e condição para rever:**
  1. **No código (B3):** `PedidoService.criar` desfaz integralmente as reservas quando ocorre `EstoqueInsuficiente` (`R2.2`), mas quando o **pagamento é recusado** (`cobranca["status"] != "aprovado"`, `R2.3`, linhas 33–34 de `pedidos.py`), o código original apenas não salva o pedido no repositório sem liberar as reservas já feitas (pois `R2.3` exige apenas *"Pagamento recusado não salva o pedido (`402`)"* e não fazia parte do escopo B3). Além disso, os desvios de `R1.3` (`total > 200`), `R1.5` (`float`/`round`) e `R4` (`get_pedido` sem checar `usuario_id`) permanecem fora do escopo desta tarefa para não misturar mudanças independentes no mesmo PR.
  2. **Na medição:** uma janela de 6 semanas em time de 5 pessoas tem amostra pequena e confundidores (curva de aprendizado com escopo de 6 campos e variação de dificuldade das tarefas).
  3. **Condição para rever:** no código, abrir PRs dedicados para `R4` (B1), `R1.3/R1.5` (B2) e definir com o dono do contrato se `R2.3` (pagamento recusado) também deve liberar o estoque reservado; na medição/automação, interromper imediatamente o agente se a taxa de reversão pós-merge subir, se o escore de mutação cair abaixo de `95%` ou se mais de `30%` das propostas de teste do agente forem descartadas como snapshots de bug.

- **Procedência/IA:** ferramenta e modelo visíveis: Antigravity (Gemini 4 Argon), execução local em Python 3.11.9 (Windows, branch `av3-b3`); tarefa delegada e contexto: análise de `estoque.py` e `pedidos.py` frente a `R2.2`, escrita dos 5 testes de regressão (commit `23d84fb`), implementação de `Estoque.liberar` e do bloco `try/except EstoqueInsuficiente` em `PedidoService.criar` (commit `2ec06d3`), execução da suíte e de `testes/mutacao_manual.py`, e estruturação deste registro; trecho aproveitado: métodos `Estoque.reservar`/`Estoque.liberar`, rollback em `PedidoService.criar` e testes em `test_estoque.py`, `test_pedidos.py` e `test_handlers.py`; minha verificação/intervenção: definição e aprovação prévia do escopo de 6 campos e do plano, rejeição da pré-validação por `estoque.saldo()` (que quebraria os `MagicMock` de `test_pedidos.py`) e do estorno ingênuo por `"tmp-{usuario_id}"` (que estornaria pedidos anteriores já pagos do mesmo usuário), conferência da falha dos 5 testes antes da correção (`23d84fb`) e da passagem dos 37 testes + `97%` de mutação (`30/31`) após a correção (`2ec06d3`). O raciocínio e a decisão registrados são meus.

**Revisão:** [x] modo; [x] escopo; [x] verificação; [x] erros da IA; [x] medição e automação; [x] procedência.

---

## Anexo de Evidências (Descrição do PR, Diff e Saídas de Verificação)

### A.1. Commits atômicos do PR (`git log --oneline main..av3-b3`)
- `23d84fb` — `Adiciona testes de regressão para rollback de reserva de estoque (R2.2)` *(Red: 4 FAIL, 1 ERROR)*
- `2ec06d3` — `Desfaz reservas anteriores quando item falha por falta de estoque (R2.2)` *(Green: 37 OK, mutação 97%)*

### A.2. Diff de produção (`git diff main..2ec06d3 -- caso/miniloja/`)
```diff
diff --git a/caso/miniloja/estoque.py b/caso/miniloja/estoque.py
--- a/caso/miniloja/estoque.py
+++ b/caso/miniloja/estoque.py
@@ -16,5 +16,16 @@ class Estoque:
         if disponivel < qtd:
             raise EstoqueInsuficiente(sku)
         self.saldos[sku] = disponivel - qtd
-        self.reservas[(pedido_id, sku)] = qtd
+        chave = (pedido_id, sku)
+        self.reservas[chave] = self.reservas.get(chave, 0) + qtd
         return True
+
+    def liberar(self, sku, qtd, pedido_id):
+        """Desfaz a reserva da quantidade do SKU no estoque."""
+        self.saldos[sku] = self.saldos.get(sku, 0) + qtd
+        chave = (pedido_id, sku)
+        restante = self.reservas.get(chave, 0) - qtd
+        if restante > 0:
+            self.reservas[chave] = restante
+        else:
+            self.reservas.pop(chave, None)

diff --git a/caso/miniloja/pedidos.py b/caso/miniloja/pedidos.py
--- a/caso/miniloja/pedidos.py
+++ b/caso/miniloja/pedidos.py
@@ -21,4 +21,12 @@ class PedidoService:
         total = calcular_total(itens, cupom, uf)
-        for i in itens:
-            self.estoque.reservar(i["sku"], i["qtd"], pedido_id=f"tmp-{usuario_id}")
+        pedido_id = f"tmp-{usuario_id}"
+        reservados = []
+        try:
+            for i in itens:
+                self.estoque.reservar(i["sku"], i["qtd"], pedido_id=pedido_id)
+                reservados.append((i["sku"], i["qtd"]))
+        except EstoqueInsuficiente:
+            for sku, qtd in reversed(reservados):
+                self.estoque.liberar(sku, qtd, pedido_id=pedido_id)
+            raise
         cobranca = self.gateway.cobrar(total, token)
```

### A.3. Saída dos testes ANTES (`23d84fb`) vs. DEPOIS (`2ec06d3`) e Mutação
```text
# ANTES (commit 23d84fb — apenas os novos testes sobre o código original):
$ python -B testes/test_miniloja.py --codigo caso --existentes
ERROR: test_liberar_restaura_saldo_e_remove_reserva -> AttributeError: 'Estoque' object has no attribute 'liberar'
FAIL: test_reservar_mesmo_sku_acumula_e_liberar_parcial_preserva_anterior -> AssertionError: 3 != 5
FAIL: test_post_pedidos_409_desfaz_reserva_dos_itens_anteriores -> AssertionError: 44 != 48
FAIL: test_falha_em_item_subsequente_desfaz_reservas_anteriores_r2_2 -> AssertionError: 7 != 10
FAIL: test_rollback_nao_desfaz_reserva_de_pedido_anterior_do_mesmo_usuario -> AssertionError: 5 != 8
Ran 37 tests in 0.007s — FAILED (failures=4, errors=1)

# DEPOIS (commit 2ec06d3 — com a correção em estoque.py e pedidos.py):
$ python -B testes/test_miniloja.py --codigo caso --existentes
Ran 37 tests in 0.004s — OK

$ $env:MINILOJA_TEST_CMD="python -B testes/test_miniloja.py --existentes --codigo caso -x"; python -B testes/mutacao_manual.py
Mutantes: 31 | mortos: 30 | sobreviventes: 1 | escore: 97%
  SOBREVIVEU  calculo.py: variável sem efeito (mutante equivalente)
```
