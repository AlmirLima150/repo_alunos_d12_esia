import os
import unittest

from miniloja.calculo import calcular_total


class TestCalculo(unittest.TestCase):
    def test_total_simples_pe(self):
        itens = [{"preco": 50.0, "qtd": 2}]
        self.assertEqual(calcular_total(itens, None, "PE"), 118.55)

    def test_cupom_promo10_sp(self):
        self.assertEqual(calcular_total([{"preco": 80.0, "qtd": 1}], "PROMO10", "SP"), 98.33)

    def test_frete_gratis_rj(self):
        self.assertEqual(calcular_total([{"preco": 40.0, "qtd": 1}], "FRETEGRATIS", "RJ"), 42.4)

    def test_pedido_acima_de_200_nao_paga_frete(self):
        self.assertEqual(calcular_total([{"preco": 250.0, "qtd": 1}], None, "PE"), 262.5)

    def test_uf_desconhecida_usa_frete_e_taxa_padrao(self):
        self.assertEqual(calcular_total([{"preco": 60.0, "qtd": 1}], None, "XX"), 97.09)

    def test_cupom_desconhecido_e_ignorado(self):
        itens = [{"preco": 30.0, "qtd": 1}]
        self.assertEqual(calcular_total(itens, "CUPOMFALSO", "PE"), calcular_total(itens, None, "PE"))

    def test_retorna_numero(self):
        resultado = calcular_total([{"preco": 10.0, "qtd": 1}], None, "PE")
        self.assertIsInstance(resultado, float)

    def test_cupom_natal_com_flag(self):
        os.environ["MINILOJA_PROMO_NATAL"] = "1"
        try:
            # R1.2 + R1.3 + R1.4: (100 * 0.80 + 21.50) * 1.06 = 101.50 * 1.06 = 107.59
            resultado = calcular_total([{"preco": 100.0, "qtd": 1}], "NATAL", "RJ")
            self.assertEqual(resultado, 107.59)
        finally:
            os.environ.pop("MINILOJA_PROMO_NATAL", None)

    def test_frete_rj_sem_cupom(self):
        # R1.3 + R1.4 em RJ: (100.0 + 21.50) * 1.06 = 128.79
        self.assertEqual(calcular_total([{"preco": 100.0, "qtd": 1}], None, "RJ"), 128.79)

    def test_cenarios_gravados(self):
        cenarios = {
            "simples": calcular_total([{"preco": 19.99, "qtd": 3}], None, "PE"),
            "vip": calcular_total([{"preco": 100.0, "qtd": 3}], "VIP15", "SP"),
            "limite_200": calcular_total([{"preco": 100.0, "qtd": 2}], None, "PE"),
            "vazio": calcular_total([], None, "PE"),
        }
        self.assertEqual(
            cenarios,
            {"simples": 76.51, "vip": 272.85, "limite_200": 223.55, "vazio": 13.54},
        )

    def test_golden_master_produto_cartesiano(self):
        """Golden Master: 5 carrinhos x 7 estados de cupom x 4 UFs = 140 cenários com igualdade exata."""
        carrinhos = {
            "C1": [{"sku": "CAMISA-M", "preco": 80.0, "qtd": 1}, {"sku": "BOLA-01", "preco": 50.0, "qtd": 1}],
            "C2": [{"sku": "CHUTEIRA-42", "preco": 250.0, "qtd": 1}],
            "C3": [{"sku": "BOLA-01", "preco": 19.99, "qtd": 3}],
            "C4": [{"sku": "ITEM-200", "preco": 100.0, "qtd": 2}],
            "C5": [],
        }
        cupons = [
            ("NONE", None, "0"),
            ("PROMO10", "PROMO10", "0"),
            ("VIP15", "VIP15", "0"),
            ("FRETEGRATIS", "FRETEGRATIS", "0"),
            ("NATAL_0", "NATAL", "0"),
            ("NATAL_1", "NATAL", "1"),
            ("INV", "CUPOM_X", "0"),
        ]
        ufs = ["PE", "SP", "RJ", "BA"]
        esperados = {
            "C1": [150.05, 160.39, 160.59, 172.69, 136.4, 146.48, 146.81, 158.65, 129.57, 139.53, 139.92, 151.63, 136.5, 139.1, 137.8, 140.4, 150.05, 160.39, 160.59, 172.69, 122.75, 132.57, 133.03, 144.61, 150.05, 160.39, 160.59, 172.69],
            "C2": [262.5, 267.5, 265.0, 270.0, 236.25, 240.75, 238.5, 243.0, 223.12, 227.38, 225.25, 229.5, 262.5, 267.5, 265.0, 270.0, 262.5, 267.5, 265.0, 270.0, 223.55, 235.29, 234.79, 248.29, 262.5, 267.5, 265.0, 270.0],
            "C3": [76.51, 85.46, 86.36, 97.06, 70.22, 79.04, 80.0, 90.58, 67.07, 75.84, 76.82, 87.34, 62.97, 64.17, 63.57, 64.77, 76.51, 85.46, 86.36, 97.06, 63.92, 72.63, 73.64, 84.11, 76.51, 85.46, 86.36, 97.06],
            "C4": [223.55, 235.29, 234.79, 248.29, 202.55, 213.89, 213.59, 226.69, 192.05, 203.19, 202.99, 215.89, 210.0, 214.0, 212.0, 216.0, 223.55, 235.29, 234.79, 248.29, 181.55, 192.49, 192.39, 205.09, 223.55, 235.29, 234.79, 248.29],
            "C5": [13.54, 21.29, 22.79, 32.29, 13.54, 21.29, 22.79, 32.29, 13.54, 21.29, 22.79, 32.29, 0.0, 0.0, 0.0, 0.0, 13.54, 21.29, 22.79, 32.29, 13.54, 21.29, 22.79, 32.29, 13.54, 21.29, 22.79, 32.29],
        }
        try:
            for c_id, itens in carrinhos.items():
                obtidos = []
                for _, cupom, flag in cupons:
                    os.environ["MINILOJA_PROMO_NATAL"] = flag
                    for uf in ufs:
                        val = calcular_total(itens, cupom, uf)
                        self.assertIsInstance(val, float)
                        obtidos.append(val)
                self.assertEqual(obtidos, esperados[c_id], f"Divergência no carrinho {c_id}")
        finally:
            os.environ.pop("MINILOJA_PROMO_NATAL", None)
