import unittest

from miniloja import cadastro


class TestCadastro(unittest.TestCase):
    def test_cadastro_sem_nome_e_rejeitado(self):
        cadastro.limpar()
        status, _ = cadastro.cadastrar_cliente({"email": "a@b.com"})
        self.assertEqual(status, 400)

    def test_cadastro_sem_email_e_rejeitado(self):
        # R3.1: campo email é obrigatório. Só exige a rejeição: o status certo é 422 (R3.4),
        # e o código atual responde 400; fixar o 400 congelaria a divergência.
        cadastro.limpar()
        status, _ = cadastro.cadastrar_cliente({"nome": "Ana"})
        self.assertNotEqual(status, 201)

    def test_cadastro_valido(self):
        cadastro.limpar()
        status, corpo = cadastro.cadastrar_cliente({"nome": "Ana", "email": "ana@exemplo.com"})
        self.assertEqual(status, 201)
        self.assertEqual(corpo["id"], 1)
