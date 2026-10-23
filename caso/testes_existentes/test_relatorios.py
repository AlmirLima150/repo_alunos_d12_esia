import unittest

from miniloja.relatorios import resumo_vendas, simular_desconto


class TestRelatorios(unittest.TestCase):
    def test_resumo_vendas(self):
        # Caracterização, não contrato: congela o _fmt atual. Por R1.5 (meio para cima)
        # 30,125 seria "R$ 30,13". 10.125 é exato em binário; mata o mutante round(v, 3).
        r = resumo_vendas([{"total": 10.125}, {"total": 20.0}])
        self.assertEqual(r["quantidade"], 2)
        self.assertEqual(r["total"], 30.125)
        self.assertEqual(r["total_fmt"], "R$ 30,12")

    def test_simular_desconto(self):
        # Caracterização, não contrato: "R$ 90,0" (sem duas casas) é o formato atual de _fmt.
        self.assertEqual(simular_desconto(100.0, "PROMO10"), "R$ 90,0")
