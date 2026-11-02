import unittest

from miniloja.estoque import Estoque, EstoqueInsuficiente


class TestEstoque(unittest.TestCase):
    def test_reservar_decrementa_saldo(self):
        e = Estoque({"BOLA-01": 10})
        e.reservar("BOLA-01", 3, "p1")
        self.assertEqual(e.saldo("BOLA-01"), 7)

    def test_reservar_alem_do_saldo_levanta(self):
        e = Estoque({"BOLA-01": 2})
        with self.assertRaises(EstoqueInsuficiente):
            e.reservar("BOLA-01", 3, "p1")

    def test_reservar_exatamente_todo_o_saldo_disponivel(self):
        # Fronteira R2.2: reservar qtd == disponivel deve ser permitido e zerar o saldo
        e = Estoque({"BOLA-01": 10})
        self.assertTrue(e.reservar("BOLA-01", 10, "p1"))
        self.assertEqual(e.saldo("BOLA-01"), 0)
