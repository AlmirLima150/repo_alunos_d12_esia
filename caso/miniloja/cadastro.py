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


def email_valido(email):
    """R3.3: formato texto@texto.texto."""
    if not isinstance(email, str) or "@" not in email:
        return False
    local, sep, dominio = email.partition("@")
    if not local or not sep or "@" in dominio or "." not in dominio:
        return False
    partes = dominio.split(".")
    return all(bool(p) for p in partes)


def cadastrar_cliente(payload):
    """Cadastra um cliente segundo R3 (422 com todos os erros ou 201 com id)."""
    erros = []
    if not payload.get("nome"):
        erros.append({"campo": "nome", "erro": "nome obrigatório"})
    email = payload.get("email")
    if not email or not email_valido(email):
        erros.append({"campo": "email", "erro": "email inválido"})
    cpf = payload.get("cpf")
    if not cpf or not cpf_valido(cpf):
        erros.append({"campo": "cpf", "erro": "cpf inválido"})
    if erros:
        return 422, {"erros": erros}
    cliente = dict(payload, id=len(_CLIENTES) + 1)
    _CLIENTES.append(cliente)
    return 201, cliente


def limpar():
    _CLIENTES.clear()
