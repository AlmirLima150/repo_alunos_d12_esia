import unittest
from unittest.mock import MagicMock

from miniloja.estoque import Estoque
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
