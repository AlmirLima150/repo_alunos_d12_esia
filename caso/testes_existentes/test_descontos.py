import unittest

from miniloja.descontos import aplicar_desconto


class TestDescontos(unittest.TestCase):
    def test_sem_cupom_retorna_total(self):
        self.assertEqual(aplicar_desconto(200.0, None), 200.0)

    def test_aplicar_desconto(self):
        self.assertEqual(aplicar_desconto(200.0, "PROMO10"), 180.0)

    def test_aplicar_desconto_vip15(self):
        # R1.2: VIP15 aplica 15% sobre 200.0 -> 170.0
        self.assertEqual(aplicar_desconto(200.0, "VIP15"), 170.0)
