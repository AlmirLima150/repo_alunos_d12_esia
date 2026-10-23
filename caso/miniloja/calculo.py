"""Cálculo de totais de pedido.

Contrato de referência: regra R1 em `caso/regras.md`.
Ordem obrigatória (R1.6): subtotal -> desconto -> frete -> taxa -> arredondamento.
Nota de caracterização (refatoração): preserva o comportamento observável atual,
incluindo a condição estrita acima de R$ 200,00 para isenção de frete (divergente de R1.3)
e o round() nativo sobre float (divergente de R1.5 meio para cima: 2 itens de R$ 1,00
em PE resultam em 15.64, e não 15.65, pela representação binária de 15,645).
"""
from miniloja import flags

# Ainda não usados: as cadeias if/elif de frete e taxa ficam literais porque são o alvo
# textual de testes/mutacao_manual.py, que não pode ser alterado neste pacote.
FRETE_POR_UF = {"PE": 12.9, "SP": 19.9, "RJ": 21.5}
TAXA_POR_UF = {"PE": 0.05, "SP": 0.07, "RJ": 0.06}


def _calcular_subtotal(itens):
    """Soma o produto do preço unitário pela quantidade de cada item (R1.1)."""
    total = 0
    for i in itens:
        preco = i["preco"]
        qtd = i["qtd"]
        total = total + preco * qtd
    return total


def _aplicar_desconto(total, cupom):
    """Aplica o desconto percentual do cupom sobre o subtotal (R1.2)."""
    desconto_aplicado = False
    if cupom is not None:
        if cupom == "PROMO10":
            total = total * 0.9
            desconto_aplicado = True
        elif cupom == "VIP15":
            total = total * 0.85
            desconto_aplicado = True
        elif cupom == "FRETEGRATIS":
            desconto_aplicado = False
        elif cupom == "NATAL":
            if flags.promo_natal_ativa():
                total = total * 0.8
                desconto_aplicado = True
            else:
                desconto_aplicado = False
        else:
            desconto_aplicado = False
    # Sem efeito no retorno; mantido como alvo do mutante equivalente de testes/mutacao_manual.py.
    if desconto_aplicado:
        pass
    return total


def _calcular_frete(total, cupom, uf):
    """Calcula o frete conforme cupom, faixa de valor pós-desconto e UF (R1.3)."""
    frete = 0
    if cupom == "FRETEGRATIS":
        frete = 0
    else:
        if total > 200:
            frete = 0
        else:
            if uf == "PE":
                frete = 12.9
            elif uf == "SP":
                frete = 19.9
            elif uf == "RJ":
                frete = 21.5
            else:
                frete = 29.9
    return frete


def _aplicar_taxa(total, uf):
    """Aplica a taxa de serviço por UF sobre (subtotal com desconto + frete) (R1.4)."""
    if uf == "PE":
        taxa = 0.05
    elif uf == "SP":
        taxa = 0.07
    elif uf == "RJ":
        taxa = 0.06
    else:
        taxa = 0.08
    imposto = total * taxa
    return total + imposto


def calcular_total(itens, cupom=None, uf="PE"):
    """Calcula o total do pedido aplicando desconto, frete e taxa de serviço (R1)."""
    total = _calcular_subtotal(itens)
    total = _aplicar_desconto(total, cupom)
    total = total + _calcular_frete(total, cupom, uf)
    total = _aplicar_taxa(total, uf)
    return round(total, 2)
