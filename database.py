
import sqlite3
from datetime import datetime, timedelta


NOME_BANCO = "hotelflow.db"


def conectar():
    """Abre uma conexão com o banco de dados."""

    conexao = sqlite3.connect(NOME_BANCO)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")

    return conexao


def obter_data_atual():
    """Retorna a data e o horário atuais."""

    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")



def registrar_historico(
    cursor,
    id_ocorrencia,
    acao,
    campo="",
    valor_anterior="",
    valor_novo="",
    usuario="Usuário Demonstração"
):
    """Registra uma ação no histórico de ocorrências."""

    cursor.execute("""
        INSERT INTO historico_ocorrencias (
            id_ocorrencia,
            acao,
            campo,
            valor_anterior,
            valor_novo,
            data_hora,
            usuario
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        id_ocorrencia,
        acao,
        campo,
        str(valor_anterior) if valor_anterior is not None else "",
        str(valor_novo) if valor_novo is not None else "",
        obter_data_atual(),
        usuario
    ))



def criar_banco():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS setores (
            id_setor INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            descricao TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quartos (
            id_quarto INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT NOT NULL UNIQUE,
            tipo TEXT NOT NULL,
            situacao TEXT NOT NULL DEFAULT 'Disponível'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cargo TEXT NOT NULL,
            id_setor INTEGER,
            FOREIGN KEY (id_setor)
                REFERENCES setores(id_setor)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ocorrencias (
            id_ocorrencia INTEGER PRIMARY KEY AUTOINCREMENT,
            id_quarto INTEGER,
            id_usuario INTEGER,
            id_setor INTEGER NOT NULL,
            hospede TEXT,
            categoria TEXT NOT NULL,
            descricao TEXT NOT NULL,
            prioridade TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Aberta',
            data_abertura TEXT NOT NULL,
            data_conclusao TEXT,

            FOREIGN KEY (id_quarto)
                REFERENCES quartos(id_quarto),

            FOREIGN KEY (id_usuario)
                REFERENCES usuarios(id_usuario),

            FOREIGN KEY (id_setor)
                REFERENCES setores(id_setor)
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_ocorrencias (
            id_historico INTEGER PRIMARY KEY AUTOINCREMENT,
            id_ocorrencia INTEGER NOT NULL,
            acao TEXT NOT NULL,
            campo TEXT,
            valor_anterior TEXT,
            valor_novo TEXT,
            data_hora TEXT NOT NULL,
            usuario TEXT
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_historico_ocorrencia
        ON historico_ocorrencias (id_ocorrencia)
    """)

    conexao.commit()

    inserir_dados_iniciais(conexao)

    conexao.close()



def inserir_dados_iniciais(conexao):

    cursor = conexao.cursor()

    setores = [
        ("Recepção", "Atendimento e suporte aos hóspedes"),
        ("Governança", "Limpeza e organização dos quartos"),
        ("Manutenção", "Manutenção preventiva e corretiva"),
        ("Alimentos e Bebidas", "Serviços de alimentação"),
        ("Gerência", "Gestão administrativa do hotel")
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO setores (nome, descricao)
        VALUES (?, ?)
    """, setores)

    quartos = [
        ("101", "Standard", "Ocupado"),
        ("102", "Standard", "Disponível"),
        ("103", "Standard", "Ocupado"),
        ("201", "Luxo", "Ocupado"),
        ("202", "Luxo", "Disponível"),
        ("203", "Luxo", "Ocupado"),
        ("301", "Suíte", "Disponível"),
        ("302", "Suíte", "Ocupado")
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO quartos (numero, tipo, situacao)
        VALUES (?, ?, ?)
    """, quartos)

    cursor.execute("""
        SELECT id_setor FROM setores
        WHERE nome = 'Recepção'
    """)

    setor_recepcao = cursor.fetchone()["id_setor"]

    cursor.execute("""
        SELECT COUNT(*) AS total FROM usuarios
    """)

    if cursor.fetchone()["total"] == 0:

        cursor.execute("""
            INSERT INTO usuarios (nome, cargo, id_setor)
            VALUES (?, ?, ?)
        """, (
            "Usuário Demonstração",
            "Recepcionista",
            setor_recepcao
        ))

    conexao.commit()



def cadastrar_ocorrencia(
    id_quarto,
    hospede,
    categoria,
    descricao,
    id_setor,
    prioridade
):

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT id_usuario, nome
            FROM usuarios
            LIMIT 1
        """)

        usuario = cursor.fetchone()

        if usuario is None:
            raise ValueError("Nenhum usuário cadastrado.")

        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")

        cursor.execute("""
            INSERT INTO ocorrencias (
                id_quarto,
                id_usuario,
                id_setor,
                hospede,
                categoria,
                descricao,
                prioridade,
                status,
                data_abertura
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_quarto,
            usuario["id_usuario"],
            id_setor,
            hospede,
            categoria,
            descricao,
            prioridade,
            "Aberta",
            data_atual
        ))

        id_novo = cursor.lastrowid

        registrar_historico(
            cursor,
            id_novo,
            "Ocorrência criada",
            campo="Cadastro",
            valor_anterior="",
            valor_novo="Ocorrência cadastrada",
            usuario=usuario["nome"]
        )

        conexao.commit()

        return id_novo

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def listar_ocorrencias(filtro=""):

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        sql = """
            SELECT
                o.id_ocorrencia,
                o.id_quarto,
                o.id_setor,
                q.numero AS quarto,
                o.hospede,
                o.categoria,
                o.descricao,
                s.nome AS setor,
                o.prioridade,
                o.status,
                o.data_abertura,
                o.data_conclusao

            FROM ocorrencias o

            LEFT JOIN quartos q
                ON o.id_quarto = q.id_quarto

            INNER JOIN setores s
                ON o.id_setor = s.id_setor
        """

        parametros = ()

        if filtro:
            sql += """
                WHERE
                    CAST(o.id_ocorrencia AS TEXT) LIKE ?
                    OR COALESCE(q.numero, '') LIKE ?
                    OR COALESCE(o.hospede, '') LIKE ?
                    OR o.categoria LIKE ?
                    OR o.descricao LIKE ?
                    OR s.nome LIKE ?
                    OR o.status LIKE ?
            """

            termo = f"%{filtro}%"
            parametros = (termo,) * 7

        sql += " ORDER BY o.id_ocorrencia DESC"

        cursor.execute(sql, parametros)

        return cursor.fetchall()

    finally:
        conexao.close()



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

    conexao = conectar()

    try:
        cursor = conexao.cursor()


        cursor.execute("""
            SELECT *
            FROM ocorrencias
            WHERE id_ocorrencia = ?
        """, (id_ocorrencia,))

        anterior = cursor.fetchone()

        if anterior is None:
            return False

        cursor.execute("""
            SELECT id_usuario, nome
            FROM usuarios
            LIMIT 1
        """)

        usuario = cursor.fetchone()

        nome_usuario = (
            usuario["nome"]
            if usuario else "Usuário Demonstração"
        )


        def nome_quarto(identificador):
            if identificador is None:
                return "Sem quarto associado"

            cursor.execute("""
                SELECT numero FROM quartos
                WHERE id_quarto = ?
            """, (identificador,))

            resultado = cursor.fetchone()

            return resultado["numero"] if resultado else str(identificador)

        def nome_setor(identificador):
            cursor.execute("""
                SELECT nome FROM setores
                WHERE id_setor = ?
            """, (identificador,))

            resultado = cursor.fetchone()

            return resultado["nome"] if resultado else str(identificador)


        if status == "Concluída":
            if anterior["status"] == "Concluída":
                data_conclusao = anterior["data_conclusao"]
            else:
                data_conclusao = datetime.now().strftime("%d/%m/%Y %H:%M")
        else:
            data_conclusao = None

        cursor.execute("""
            UPDATE ocorrencias

            SET
                id_quarto = ?,
                hospede = ?,
                categoria = ?,
                descricao = ?,
                id_setor = ?,
                prioridade = ?,
                status = ?,
                data_conclusao = ?

            WHERE id_ocorrencia = ?
        """, (
            id_quarto,
            hospede,
            categoria,
            descricao,
            id_setor,
            prioridade,
            status,
            data_conclusao,
            id_ocorrencia
        ))


        alteracoes = [
            ("Quarto", nome_quarto(anterior["id_quarto"]), nome_quarto(id_quarto)),
            ("Hóspede", anterior["hospede"], hospede),
            ("Categoria", anterior["categoria"], categoria),
            ("Descrição", anterior["descricao"], descricao),
            ("Setor responsável", nome_setor(anterior["id_setor"]), nome_setor(id_setor)),
            ("Prioridade", anterior["prioridade"], prioridade),
            ("Status", anterior["status"], status)
        ]

        for campo, valor_anterior, valor_novo in alteracoes:

            valor_anterior = (
                "" if valor_anterior is None else str(valor_anterior)
            )

            valor_novo = (
                "" if valor_novo is None else str(valor_novo)
            )

            if valor_anterior != valor_novo:

                registrar_historico(
                    cursor,
                    id_ocorrencia,
                    "Alteração realizada",
                    campo,
                    valor_anterior,
                    valor_novo,
                    nome_usuario
                )

        conexao.commit()

        return cursor.rowcount >= 0

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()



def listar_historico(id_ocorrencia):

    conexao = conectar()

    try:
        resultados = conexao.execute("""
            SELECT
                id_historico,
                id_ocorrencia,
                acao,
                campo,
                valor_anterior,
                valor_novo,
                data_hora,
                usuario

            FROM historico_ocorrencias

            WHERE id_ocorrencia = ?

            ORDER BY id_historico DESC
        """, (id_ocorrencia,)).fetchall()

        return resultados

    finally:
        conexao.close()



def excluir_ocorrencia(id_ocorrencia):

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT id_ocorrencia
            FROM ocorrencias
            WHERE id_ocorrencia = ?
        """, (id_ocorrencia,))

        registro = cursor.fetchone()

        if registro is None:
            return False

        cursor.execute("""
            SELECT nome
            FROM usuarios
            LIMIT 1
        """)

        usuario = cursor.fetchone()

        nome_usuario = (
            usuario["nome"]
            if usuario else "Usuário Demonstração"
        )

        registrar_historico(
            cursor,
            id_ocorrencia,
            "Ocorrência excluída",
            campo="Exclusão",
            valor_anterior="Ocorrência cadastrada",
            valor_novo="Ocorrência excluída",
            usuario=nome_usuario
        )

        cursor.execute("""
            DELETE FROM ocorrencias
            WHERE id_ocorrencia = ?
        """, (id_ocorrencia,))

        excluidos = cursor.rowcount

        conexao.commit()

        return excluidos > 0

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()



def listar_setores():

    conexao = conectar()

    try:
        resultados = conexao.execute("""
            SELECT id_setor, nome
            FROM setores
            ORDER BY nome
        """).fetchall()

        return resultados

    finally:
        conexao.close()


def listar_quartos():

    conexao = conectar()

    try:
        resultados = conexao.execute("""
            SELECT id_quarto, numero, tipo, situacao
            FROM quartos
            ORDER BY numero
        """).fetchall()

        return resultados

    finally:
        conexao.close()



def obter_indicadores():

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) AS total,

                SUM(CASE
                    WHEN status = 'Aberta' THEN 1
                    ELSE 0
                END) AS abertas,

                SUM(CASE
                    WHEN status = 'Em andamento' THEN 1
                    ELSE 0
                END) AS andamento,

                SUM(CASE
                    WHEN status = 'Concluída' THEN 1
                    ELSE 0
                END) AS concluidas

            FROM ocorrencias
        """)

        resultado = cursor.fetchone()

        return {
            "total": resultado["total"] or 0,
            "abertas": resultado["abertas"] or 0,
            "andamento": resultado["andamento"] or 0,
            "concluidas": resultado["concluidas"] or 0
        }

    finally:
        conexao.close()



def relatorio_por_setor():

    conexao = conectar()

    try:
        resultados = conexao.execute("""
            SELECT
                s.nome AS setor,
                COUNT(o.id_ocorrencia) AS total

            FROM setores s

            LEFT JOIN ocorrencias o
                ON s.id_setor = o.id_setor

            GROUP BY s.id_setor, s.nome
            ORDER BY total DESC
        """).fetchall()

        return resultados

    finally:
        conexao.close()



def converter_data_desempenho(valor):
    """
    Converte as datas armazenadas no banco
    para objetos datetime.
    """

    if not valor:
        return None

    formatos = [
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M"
    ]

    for formato in formatos:
        try:
            return datetime.strptime(valor, formato)
        except (ValueError, TypeError):
            continue

    return None


def obter_periodo_desempenho(periodo="todo"):
    """
    Retorna a data inicial do período selecionado.
    """

    agora = datetime.now()

    if periodo == "hoje":
        return agora.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

    elif periodo == "7dias":
        return agora - timedelta(days=7)

    elif periodo == "mes":
        return agora.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

    return None


def obter_dados_desempenho(periodo="todo"):
    """
    Calcula indicadores gerais e desempenho por setor.

    Períodos disponíveis:
    - hoje
    - 7dias
    - mes
    - todo
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT
                o.id_ocorrencia,
                o.categoria,
                o.descricao,
                o.prioridade,
                o.status,
                o.data_abertura,
                o.data_conclusao,
                s.nome AS setor

            FROM ocorrencias o

            INNER JOIN setores s
                ON o.id_setor = s.id_setor

            ORDER BY o.id_ocorrencia DESC
        """)

        registros = cursor.fetchall()

        data_inicial = obter_periodo_desempenho(periodo)
        agora = datetime.now()

        ocorrencias_periodo = []

        for registro in registros:

            data_abertura = converter_data_desempenho(
                registro["data_abertura"]
            )

            if data_abertura is None:
                continue


            if data_inicial and data_abertura < data_inicial:
                continue

            if data_abertura > agora:
                continue

            ocorrencias_periodo.append({
                "id": registro["id_ocorrencia"],
                "categoria": registro["categoria"],
                "descricao": registro["descricao"],
                "prioridade": registro["prioridade"],
                "status": registro["status"],
                "setor": registro["setor"],
                "data_abertura": registro["data_abertura"],
                "data_conclusao": registro["data_conclusao"]
            })

        total = len(ocorrencias_periodo)

        concluidas = [
            ocorrencia
            for ocorrencia in ocorrencias_periodo
            if ocorrencia["status"] == "Concluída"
        ]

        total_concluidas = len(concluidas)

        taxa_conclusao = (
            (total_concluidas / total) * 100
            if total > 0 else 0
        )


        tempos_resolucao = []

        for ocorrencia in concluidas:

            abertura = converter_data_desempenho(
                ocorrencia["data_abertura"]
            )

            conclusao = converter_data_desempenho(
                ocorrencia["data_conclusao"]
            )

            if abertura and conclusao:

                diferenca = (
                    conclusao - abertura
                ).total_seconds() / 60

                if diferenca >= 0:
                    tempos_resolucao.append(diferenca)

        tempo_medio = (
            sum(tempos_resolucao) / len(tempos_resolucao)
            if tempos_resolucao else 0
        )


        setores = {}

        for ocorrencia in ocorrencias_periodo:

            nome_setor = ocorrencia["setor"]

            if nome_setor not in setores:
                setores[nome_setor] = {
                    "setor": nome_setor,
                    "total": 0,
                    "concluidas": 0,
                    "tempos": []
                }

            setores[nome_setor]["total"] += 1

            if ocorrencia["status"] == "Concluída":

                setores[nome_setor]["concluidas"] += 1

                abertura = converter_data_desempenho(
                    ocorrencia["data_abertura"]
                )

                conclusao = converter_data_desempenho(
                    ocorrencia["data_conclusao"]
                )

                if abertura and conclusao:

                    diferenca = (
                        conclusao - abertura
                    ).total_seconds() / 60

                    if diferenca >= 0:
                        setores[nome_setor]["tempos"].append(
                            diferenca
                        )

        resultado_setores = []

        for dados in setores.values():

            tempos = dados["tempos"]

            media_setor = (
                sum(tempos) / len(tempos)
                if tempos else 0
            )

            resultado_setores.append({
                "setor": dados["setor"],
                "total": dados["total"],
                "concluidas": dados["concluidas"],
                "media_minutos": round(media_setor, 2)
            })

        resultado_setores.sort(
            key=lambda item: item["total"],
            reverse=True
        )

        return {
            "total": total,
            "concluidas": total_concluidas,
            "pendentes": total - total_concluidas,
            "taxa_conclusao": round(taxa_conclusao, 2),
            "tempo_medio_minutos": round(tempo_medio, 2),
            "setor_destaque": (
                resultado_setores[0]["setor"]
                if resultado_setores else "Nenhum"
            ),
            "setores": resultado_setores,
            "ocorrencias": ocorrencias_periodo
        }

    finally:
        conexao.close()


def converter_data_desempenho(valor):
    """
    Converte as datas armazenadas no banco
    para objetos datetime.
    """

    if not valor:
        return None

    formatos = [
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M"
    ]

    for formato in formatos:
        try:
            return datetime.strptime(valor, formato)
        except (ValueError, TypeError):
            continue

    return None


def obter_periodo_desempenho(periodo="todo"):
    """
    Retorna a data inicial do período selecionado.
    """

    agora = datetime.now()

    if periodo == "hoje":
        return agora.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

    elif periodo == "7dias":
        return agora - timedelta(days=7)

    elif periodo == "mes":
        return agora.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

    return None


def obter_dados_desempenho(periodo="todo"):
    """
    Calcula indicadores gerais e desempenho por setor.

    Períodos disponíveis:
    - hoje
    - 7dias
    - mes
    - todo
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT
                o.id_ocorrencia,
                o.categoria,
                o.descricao,
                o.prioridade,
                o.status,
                o.data_abertura,
                o.data_conclusao,
                s.nome AS setor

            FROM ocorrencias o

            INNER JOIN setores s
                ON o.id_setor = s.id_setor

            ORDER BY o.id_ocorrencia DESC
        """)

        registros = cursor.fetchall()

        data_inicial = obter_periodo_desempenho(periodo)
        agora = datetime.now()

        ocorrencias_periodo = []

        for registro in registros:

            data_abertura = converter_data_desempenho(
                registro["data_abertura"]
            )

            if data_abertura is None:
                continue


            if data_inicial and data_abertura < data_inicial:
                continue

            if data_abertura > agora:
                continue

            ocorrencias_periodo.append({
                "id": registro["id_ocorrencia"],
                "categoria": registro["categoria"],
                "descricao": registro["descricao"],
                "prioridade": registro["prioridade"],
                "status": registro["status"],
                "setor": registro["setor"],
                "data_abertura": registro["data_abertura"],
                "data_conclusao": registro["data_conclusao"]
            })

        total = len(ocorrencias_periodo)

        concluidas = [
            ocorrencia
            for ocorrencia in ocorrencias_periodo
            if ocorrencia["status"] == "Concluída"
        ]

        total_concluidas = len(concluidas)

        taxa_conclusao = (
            (total_concluidas / total) * 100
            if total > 0 else 0
        )


        tempos_resolucao = []

        for ocorrencia in concluidas:

            abertura = converter_data_desempenho(
                ocorrencia["data_abertura"]
            )

            conclusao = converter_data_desempenho(
                ocorrencia["data_conclusao"]
            )

            if abertura and conclusao:

                diferenca = (
                    conclusao - abertura
                ).total_seconds() / 60

                if diferenca >= 0:
                    tempos_resolucao.append(diferenca)

        tempo_medio = (
            sum(tempos_resolucao) / len(tempos_resolucao)
            if tempos_resolucao else 0
        )


        setores = {}

        for ocorrencia in ocorrencias_periodo:

            nome_setor = ocorrencia["setor"]

            if nome_setor not in setores:
                setores[nome_setor] = {
                    "setor": nome_setor,
                    "total": 0,
                    "concluidas": 0,
                    "tempos": []
                }

            setores[nome_setor]["total"] += 1

            if ocorrencia["status"] == "Concluída":

                setores[nome_setor]["concluidas"] += 1

                abertura = converter_data_desempenho(
                    ocorrencia["data_abertura"]
                )

                conclusao = converter_data_desempenho(
                    ocorrencia["data_conclusao"]
                )

                if abertura and conclusao:

                    diferenca = (
                        conclusao - abertura
                    ).total_seconds() / 60

                    if diferenca >= 0:
                        setores[nome_setor]["tempos"].append(
                            diferenca
                        )

        resultado_setores = []

        for dados in setores.values():

            tempos = dados["tempos"]

            media_setor = (
                sum(tempos) / len(tempos)
                if tempos else 0
            )

            resultado_setores.append({
                "setor": dados["setor"],
                "total": dados["total"],
                "concluidas": dados["concluidas"],
                "media_minutos": round(media_setor, 2)
            })

        resultado_setores.sort(
            key=lambda item: item["total"],
            reverse=True
        )

        return {
            "total": total,
            "concluidas": total_concluidas,
            "pendentes": total - total_concluidas,
            "taxa_conclusao": round(taxa_conclusao, 2),
            "tempo_medio_minutos": round(tempo_medio, 2),
            "setor_destaque": (
                resultado_setores[0]["setor"]
                if resultado_setores else "Nenhum"
            ),
            "setores": resultado_setores,
            "ocorrencias": ocorrencias_periodo
        }

    finally:
        conexao.close()


if __name__ == "__main__":

    criar_banco()

    print("===================================")
    print(" HOTELFLOW - BANCO DE DADOS")
    print("===================================")
    print("Banco de dados criado com sucesso!")
    print("Tabelas e dados iniciais preparados.")
    print("Nova tabela: historico_ocorrencias")
    print("===================================")
