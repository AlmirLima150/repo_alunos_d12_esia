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

    def test_liberar_restaura_saldo_e_remove_reserva(self):
        # R2.2: desfazer reserva restaura o saldo e limpa o registro em reservas
        e = Estoque({"BOLA-01": 10})
        e.reservar("BOLA-01", 4, "p1")
        self.assertEqual(e.saldo("BOLA-01"), 6)
        e.liberar("BOLA-01", 4, "p1")
        self.assertEqual(e.saldo("BOLA-01"), 10)
        self.assertNotIn(("p1", "BOLA-01"), e.reservas)

    def test_reservar_mesmo_sku_acumula_e_liberar_parcial_preserva_anterior(self):
        # Evita sobrescrita quando o mesmo (pedido_id, sku) é reservado mais de uma vez
        e = Estoque({"BOLA-01": 10})
        e.reservar("BOLA-01", 2, "tmp-1")
        e.reservar("BOLA-01", 3, "tmp-1")
        self.assertEqual(e.saldo("BOLA-01"), 5)
        self.assertEqual(e.reservas[("tmp-1", "BOLA-01")], 5)
        e.liberar("BOLA-01", 3, "tmp-1")
        self.assertEqual(e.saldo("BOLA-01"), 8)
        self.assertEqual(e.reservas[("tmp-1", "BOLA-01")], 2)
