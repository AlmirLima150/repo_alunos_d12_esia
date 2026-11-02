# Pull request: Adiciona exportação de vendas em CSV

**Escrito pelo agente de codificação (simulado para a aula).**

## Resumo
Adiciona a função `get_exportacao` e o módulo `exportacao.py`, que geram um CSV de vendas. Todos os testes passam e não há mudanças de comportamento no código existente. Código revisado e seguro.

## Mudanças
- `caso/miniloja/exportacao.py` (novo): gera o CSV de vendas.
- `caso/miniloja/handlers.py`: nova função `get_exportacao`.
- `caso/testes_existentes/test_exportacao.py` (novo).
- `caso/requirements.txt`: adiciona `csv-export-helper` para formatar o CSV.

## Como testar
`python -B testes/test_miniloja.py --codigo caso --existentes` (27 testes passam).

## Como aplicar
`git apply 0001-Adiciona-exporta-o-de-vendas-em-CSV.patch` em uma branch sua, ou leia o `.patch` diretamente.
