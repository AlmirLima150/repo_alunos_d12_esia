import unittest
from unittest.mock import MagicMock

from miniloja.estoque import Estoque, EstoqueInsuficiente
from miniloja.pagamentos import GatewayFake
from miniloja.pedidos import PedidoService
from miniloja.repositorio import RepositorioPedidos


class TestPedidos(unittest.TestCase):
    def test_criar_pedido(self):
        repo = MagicMock()
        repo.salvar.return_value = {"id": 1}
        svc = PedidoService(repo, MagicMock(), MagicMock())
        svc.gateway.cobrar.return_value = {"status": "aprovado", "id": "x"}
        r = svc.criar(1, [{"sku": "BOLA-01", "preco": 10.0, "qtd": 1}])
        self.assertTrue(repo.salvar.called)
        self.assertEqual(r, {"id": 1})

    def test_fluxo_chama_colaboradores(self):
        estoque, gateway, repo = MagicMock(), MagicMock(), MagicMock()
        gateway.cobrar.return_value = {"status": "aprovado", "id": "x"}
        repo.salvar.return_value = {"id": 7}
        PedidoService(repo, estoque, gateway).criar(2, [{"sku": "CAMISA-M", "preco": 50.0, "qtd": 2}])
        self.assertTrue(estoque.reservar.called)
        self.assertTrue(gateway.cobrar.called)
        self.assertTrue(repo.salvar.called)

    def test_pedido_sem_itens_e_rejeitado(self):
        svc = PedidoService(RepositorioPedidos(), Estoque(), GatewayFake())
        with self.assertRaises(ValueError):
            svc.criar(1, [])

    def test_pagamento_recusado_nao_salva_pedido(self):
        repo = RepositorioPedidos()
        svc = PedidoService(repo, Estoque({"BOLA-01": 5}), GatewayFake())
        r = svc.criar(1, [{"sku": "BOLA-01", "preco": 10.0, "qtd": 1}], token="recusado")
        self.assertEqual(r["status"], "pagamento_recusado")
        self.assertEqual(repo.todos(), [])

    def test_criar_pedido_real_persiste_total_e_formatacao(self):
        # Verifica integração sem mocks tautológicos: total calculado (R1) e formatado
        repo = RepositorioPedidos()
        svc = PedidoService(repo, Estoque({"BOLA-01": 5}), GatewayFake())
        pedido = svc.criar(1, [{"sku": "BOLA-01", "preco": 50.0, "qtd": 2}], uf="PE")
        self.assertEqual(pedido["total"], 118.55)
        self.assertEqual(pedido["total_fmt"], "R$ 118,55")

    def test_falha_em_item_subsequente_desfaz_reservas_anteriores_r2_2(self):
        # R2.2: se algum item não tiver estoque, nenhuma reserva pode permanecer
        repo = RepositorioPedidos()
        estoque = Estoque({"BOLA-01": 10, "CAMISA-M": 5, "CHUTEIRA-42": 1})
        svc = PedidoService(repo, estoque, GatewayFake())
        itens = [
            {"sku": "BOLA-01", "preco": 50.0, "qtd": 3},
            {"sku": "CAMISA-M", "preco": 40.0, "qtd": 2},
            {"sku": "CHUTEIRA-42", "preco": 300.0, "qtd": 5},
        ]
        with self.assertRaises(EstoqueInsuficiente):
            svc.criar(1, itens)
        self.assertEqual(estoque.saldo("BOLA-01"), 10)
        self.assertEqual(estoque.saldo("CAMISA-M"), 5)
        self.assertEqual(estoque.saldo("CHUTEIRA-42"), 1)
        self.assertEqual(estoque.reservas, {})
        self.assertEqual(repo.todos(), [])

    def test_rollback_nao_desfaz_reserva_de_pedido_anterior_do_mesmo_usuario(self):
        # R2.2: falha em novo pedido de usuario_id=1 só desfaz reservas da tentativa atual
        repo = RepositorioPedidos()
        estoque = Estoque({"BOLA-01": 10, "CHUTEIRA-42": 1})
        svc = PedidoService(repo, estoque, GatewayFake())
        svc.criar(1, [{"sku": "BOLA-01", "preco": 50.0, "qtd": 2}])
        self.assertEqual(estoque.saldo("BOLA-01"), 8)
        with self.assertRaises(EstoqueInsuficiente):
            svc.criar(
                1,
                [
                    {"sku": "BOLA-01", "preco": 50.0, "qtd": 3},
                    {"sku": "CHUTEIRA-42", "preco": 300.0, "qtd": 5},
                ],
            )
        self.assertEqual(estoque.saldo("BOLA-01"), 8)
        self.assertEqual(estoque.reservas.get(("tmp-1", "BOLA-01")), 2)
