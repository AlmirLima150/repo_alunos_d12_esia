"""Cadastro de clientes."""

_CLIENTES = []


def cpf_valido(cpf):
    """R3.2: dígitos verificadores válidos e não todos iguais; aceita com ou sem pontuação."""
    digitos = [int(c) for c in str(cpf) if c.isdigit()]
    if len(digitos) != 11 or len(set(digitos)) == 1:
        return False
    for n in (9, 10):
        soma = sum(d * peso for d, peso in zip(digitos[:n], range(n + 1, 1, -1)))
        dv = soma * 10 % 11 % 10
        if digitos[n] != dv:
            return False
    return True


def cadastrar_cliente(payload):
    """Cadastra um cliente."""
    if not payload.get("nome"):
        return 400, {"erro": "payload inválido"}
    if not payload.get("email"):
        return 400, {"erro": "payload inválido"}
    if "cpf" in payload and not cpf_valido(payload["cpf"]):
        return 422, {"erros": [{"campo": "cpf", "erro": "cpf inválido"}]}
    cliente = dict(payload, id=len(_CLIENTES) + 1)
    _CLIENTES.append(cliente)
    return 201, cliente


def limpar():
    _CLIENTES.clear()
