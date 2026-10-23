# Registro individual — AV1.1

**Limite: uma página, incluindo evidências essenciais.** Estudante: Almir de Lima Felix dos Santos — Data: 23/10/2026 (feito depois da aula do B1)
Origem: tarefas T1–T3 fictícias do enunciado; modalidade: **execução própria**.

**Critério de aceite (escrito antes):** T1 = v08 e v09 passam (CPF com DV errado ou dígitos iguais → `422` com `cpf` em `erros`), sem quebrar v07 e v11. T2 = v10 passa (`422` com todos os erros: `nome`, `email`, `cpf`).

| Tarefa | Modo | Tempo até 1ª versão | Tempo até pronto e verificado | Idas e vindas | % corrigido à mão | O que a IA errou | Como verifiquei |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T1 | A: agente (Claude Code, edita e roda testes) | 2 min | 5 min | 1 | 0% | Não tornou o CPF obrigatório (R3.1); avisou que isso quebraria `test_cadastro_valido` e parou, como o pedido mandava | Rodei as verificações: 10 ok, 1 FAIL (v10, que é a T2) |
| T1 | B: chat (Claude responde, eu colo e rodo) | 1 min | 6 min (os 4 min iniciais não valiam: rodei o teste sem o arquivo salvo) | 2 (colagem falhou; pedi ao Claude para aplicar) | 0% | No chat não avisou que o CPF ficou opcional (o agente avisou); o erro de verdade foi meu: o "10 ok" veio sem o código salvo, e o Claude detectou conferindo o arquivo (3 FAIL) | Teste rodado com o código aplicado: 10 ok, 1 FAIL (v10) |
| T2 | Agente (Antigravity / Gemini 4 Argon, edita e roda testes) | 1 min | 3 min | 1 | 0% | Nenhum erro funcional; por tornar `cpf` obrigatório (R3.1) e mudar retorno de `400` para `422` (R3.4), atualizou `test_cadastro.py` (que esperava `400` e omitia `cpf` em `test_cadastro_valido`) | Rodei verificações (`11/11 ok`) e suíte existente (`26/26 ok`), conferindo o diff |

**Justificativa dos modos em T1 e T2:** T1 e T2 têm baixo raio de impacto (isoladas em `cadastro.py` e `test_cadastro.py`), alta reversibilidade via Git e oráculo determinístico (`v07`–`v11`), tornando o modo Agente mais produtivo por eliminar o atrito manual de copiar/salvar código no modo Chat.

**Trecho essencial de evidência (comando e saída que sustentam "verificado"):**
- `python -B testes/test_miniloja.py --codigo caso` → `test_v07 ... ok`, `test_v08 ... ok`, `test_v09 ... ok`, `test_v10_payload_invalido_lista_todos_os_erros ... ok`, `test_v11 ... ok` (`Ran 11 tests in 0.012s — OK`).
- `python -B testes/test_miniloja.py --codigo caso --existentes` → `Ran 26 tests in 0.003s — OK` (`test_cadastro.py` atualizado para o contrato R3: `422` e `cpf` obrigatório).

**T3 (hipotética): raio de impacto** alto (ambiente de produção às 02h, risco de agravar indisponibilidade ou corromper dados); **oráculo disponível** parcial/indireto (métricas de latência/erro e logs, sem teste automatizado que garanta ausência de efeitos colaterais antes da ação); **permissões que concederia** somente leitura em logs, métricas, traces e estado dos serviços (`SELECT`/queries de diagnóstico, sem escrita, restart, deploy ou `shell` destrutivo); **modo e por quê** Chat consultivo ou Agente restrito a leitura (coleta e correlação de hipóteses), mantendo qualquer comando de mitigação ou mudança em produção sob aprovação e execução humana.

**Alternativa para T3:** Agente autônomo com permissão de execução irrestrita em produção (restarts, alteração de configuração/escala). **Comparação com minha escolha (restrição e consequência):** restringir o agente à leitura aumenta o tempo até a mitigação (exige intervenção humana a cada ação), mas evita que uma alucinação ou diagnóstico precipitado apague evidências do incidente ou cause queda total às 02h. **Limite da comparação e condição para rever a escolha:** em T1/T2, uma única execução por modo não prova superioridade estatística da ferramenta (apenas evidenciou o risco operacional de colagem/salvamento no Chat). Em T3, eu reveria a restrição para permitir ações automatizadas se houvesse runbooks pré-homologados, feature flags/rollback instantâneo em ambiente canário e guardrails estritos de escopo (allowlist de comandos idempotentes).

**Procedência/IA:** Ferramentas e modelos visíveis: Claude Code (T1 modo A e B) e Antigravity / Gemini 4 Argon (T2 modo Agente e consolidação do registro); tarefa delegada e contexto: implementação de `cpf_valido`, `email_valido` e acúmulo de erros `422` em `caso/miniloja/cadastro.py` conforme R3 (`caso/regras.md`) e ajuste de contrato em `caso/testes_existentes/test_cadastro.py`; trecho aproveitado: funções `cpf_valido`, `email_valido`, `cadastrar_cliente` e testes em `test_cadastro.py`; minha verificação/intervenção: conferência de `git diff` e execução das 11 verificações do caso e 26 testes existentes. O raciocínio e a decisão registrados são meus.

**Revisão:** [x] dois modos em T1; [x] evidência localizada; [x] T3 decidida; [x] alternativa e limite; [x] até uma página.
