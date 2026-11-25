
"""
HOTELFLOW
Módulo de lógica de negócio.

Responsável por validar os dados das ocorrências
e encaminhar as operações para o banco de dados.
"""

import database



CATEGORIAS_VALIDAS = [
    "Solicitação de hóspede",
    "Manutenção",
    "Limpeza",
    "Governança",
    "Alimentos e Bebidas",
    "Reclamação",
    "Outros"
]

PRIORIDADES_VALIDAS = [
    "Baixa",
    "Média",
    "Alta",
    "Urgente"
]

STATUS_VALIDOS = [
    "Aberta",
    "Em andamento",
    "Concluída"
]



def validar_ocorrencia(
    categoria,
    descricao,
    id_setor,
    prioridade
):
    """
    Valida os campos obrigatórios de uma ocorrência.
    """

    if not isinstance(categoria, str) or not categoria.strip():
        raise ValueError(
            "Informe a categoria da ocorrência."
        )

    if not isinstance(descricao, str) or not descricao.strip():
        raise ValueError(
            "Informe a descrição da ocorrência."
        )

    if len(descricao.strip()) < 5:
        raise ValueError(
            "A descrição deve possuir pelo menos 5 caracteres."
        )

    if id_setor is None:
        raise ValueError(
            "Selecione um setor responsável."
        )

    if categoria.strip() not in CATEGORIAS_VALIDAS:
        raise ValueError(
            "A categoria selecionada é inválida."
        )

    if prioridade not in PRIORIDADES_VALIDAS:
        raise ValueError(
            "A prioridade selecionada é inválida."
        )



def cadastrar_ocorrencia(
    id_quarto,
    hospede,
    categoria,
    descricao,
    id_setor,
    prioridade
):
    """
    Valida e cadastra uma nova ocorrência.
    """

    validar_ocorrencia(
        categoria,
        descricao,
        id_setor,
        prioridade
    )

    if hospede is not None:
        hospede = hospede.strip()

    categoria = categoria.strip()
    descricao = descricao.strip()

    resultado = database.cadastrar_ocorrencia(
        id_quarto,
        hospede,
        categoria,
        descricao,
        id_setor,
        prioridade
    )

    return resultado


def atualizar_ocorrencia(
    id_ocorrencia,
    id_quarto,
    hospede,
    categoria,
    descricao,
    id_setor,
    prioridade,
    status
):
    """
    Valida e atualiza uma ocorrência existente.
    """

    if id_ocorrencia is None:
        raise ValueError(
            "Identificador da ocorrência inválido."
        )

    validar_ocorrencia(
        categoria,
        descricao,
        id_setor,
        prioridade
    )

    if status not in STATUS_VALIDOS:
        raise ValueError(
            "O status selecionado é inválido."
        )

    if hospede is not None:
        hospede = hospede.strip()

    resultado = database.atualizar_ocorrencia(
        id_ocorrencia,
        id_quarto,
        hospede,
        categoria.strip(),
        descricao.strip(),
        id_setor,
        prioridade,
        status
    )

    return resultado



def excluir_ocorrencia(id_ocorrencia):
    """
    Valida o identificador e exclui a ocorrência.
    """

    if id_ocorrencia is None:
        raise ValueError(
            "Identificador da ocorrência inválido."
        )

    resultado = database.excluir_ocorrencia(
        id_ocorrencia
    )

    return resultado



def listar_ocorrencias(filtro=""):
    """
    Consulta as ocorrências cadastradas.
    """

    if filtro is None:
        filtro = ""

    return database.listar_ocorrencias(filtro)



def obter_indicadores():
    """
    Retorna os indicadores utilizados no dashboard.
    """

    return database.obter_indicadores()



def listar_setores():
    """
    Retorna os setores cadastrados no sistema.
    """

    return database.listar_setores()



def listar_quartos():
    """
    Retorna os quartos cadastrados no sistema.
    """

    return database.listar_quartos()
