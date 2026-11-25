import tkinter as tk
import sqlite3
import csv
from datetime import datetime
from tkinter import ttk, messagebox, filedialog

import database
import chamados


COR_FUNDO = "#F3F5F9"
COR_MENU = "#172B4D"
COR_MENU_ATIVO = "#29466F"
COR_TEXTO = "#25344A"
COR_AZUL = "#356AC3"
COR_VERDE = "#24865B"
COR_VERMELHO = "#C84B4B"
COR_BRANCO = "#FFFFFF"


def obter_valor(registro, *nomes, padrao=""):
    """Obtém um valor de uma linha do banco."""

    try:
        chaves = registro.keys()

        for nome in nomes:
            if nome in chaves:
                valor = registro[nome]
                return padrao if valor is None else valor

    except (AttributeError, TypeError):
        pass

    return padrao


def converter_data(data):
    """Converte uma data para datetime."""

    if not data:
        return None

    formatos = [
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M"
    ]

    for formato in formatos:
        try:
            return datetime.strptime(str(data), formato)
        except ValueError:
            continue

    return None


class HotelFlow:

    def __init__(self, janela):

        self.janela = janela
        self.janela.title("HotelFlow - Gestão de Ocorrências")
        self.janela.geometry("1180x720")
        self.janela.minsize(950, 600)
        self.janela.configure(bg=COR_FUNDO)

        self.area_conteudo = None
        self.tela_atual = None
        self.periodo_desempenho = "todo"

        self.configurar_estilos()
        self.criar_menu()
        self.mostrar_dashboard()


    def configurar_estilos(self):

        estilo = ttk.Style()
        estilo.theme_use("clam")

        estilo.configure(
            "Treeview",
            background=COR_BRANCO,
            foreground=COR_TEXTO,
            rowheight=32,
            fieldbackground=COR_BRANCO,
            font=("Arial", 9)
        )

        estilo.configure(
            "Treeview.Heading",
            background="#E7ECF3",
            foreground=COR_TEXTO,
            font=("Arial", 9, "bold"),
            padding=8
        )

        estilo.map(
            "Treeview",
            background=[("selected", "#D8E6FA")],
            foreground=[("selected", COR_TEXTO)]
        )

        estilo.configure("TCombobox", padding=6)


    def criar_menu(self):

        self.menu = tk.Frame(
            self.janela,
            bg=COR_MENU,
            width=230
        )

        self.menu.pack(side="left", fill="y")
        self.menu.pack_propagate(False)

        tk.Label(
            self.menu,
            text="HotelFlow",
            bg=COR_MENU,
            fg=COR_BRANCO,
            font=("Arial", 22, "bold")
        ).pack(pady=(35, 5))

        tk.Label(
            self.menu,
            text="GESTÃO HOTELEIRA",
            bg=COR_MENU,
            fg="#B9C9DF",
            font=("Arial", 8, "bold")
        ).pack(pady=(0, 35))

        self.botao_menu("Dashboard", self.mostrar_dashboard)
        self.botao_menu("Ocorrências", self.mostrar_ocorrencias)
        self.botao_menu("Nova ocorrência", self.nova_ocorrencia)
        self.botao_menu("Relatórios", self.mostrar_relatorios)
        self.botao_menu("Desempenho", self.mostrar_desempenho)
        self.botao_menu("Sobre o sistema", self.mostrar_sobre)

        tk.Label(
            self.menu,
            text="HotelFlow\nSistema demonstrativo",
            bg=COR_MENU,
            fg="#B9C9DF",
            font=("Arial", 8),
            justify="center"
        ).pack(side="bottom", pady=25)

    def botao_menu(self, texto, comando):

        botao = tk.Button(
            self.menu,
            text=texto,
            command=comando,
            bg=COR_MENU,
            fg=COR_BRANCO,
            activebackground=COR_MENU_ATIVO,
            activeforeground=COR_BRANCO,
            relief="flat",
            anchor="w",
            padx=25,
            pady=14,
            font=("Arial", 10),
            cursor="hand2"
        )

        botao.pack(fill="x", padx=8, pady=2)


    def limpar_conteudo(self):

        if self.area_conteudo is not None:
            self.area_conteudo.destroy()

        self.area_conteudo = tk.Frame(
            self.janela,
            bg=COR_FUNDO
        )

        self.area_conteudo.pack(
            side="right",
            fill="both",
            expand=True
        )

    def criar_titulo(self, titulo, descricao=""):

        cabecalho = tk.Frame(
            self.area_conteudo,
            bg=COR_FUNDO
        )

        cabecalho.pack(
            fill="x",
            padx=30,
            pady=(28, 20)
        )

        tk.Label(
            cabecalho,
            text=titulo,
            bg=COR_FUNDO,
            fg=COR_TEXTO,
            font=("Arial", 22, "bold")
        ).pack(anchor="w")

        if descricao:

            tk.Label(
                cabecalho,
                text=descricao,
                bg=COR_FUNDO,
                fg="#718096",
                font=("Arial", 10)
            ).pack(anchor="w", pady=(5, 0))


    def mostrar_dashboard(self):

        self.limpar_conteudo()
        self.tela_atual = "dashboard"

        self.criar_titulo(
            "Dashboard",
            "Visão geral das ocorrências, pendências e solicitações do hotel."
        )

        try:
            indicadores = database.obter_indicadores()
            ocorrencias = database.listar_ocorrencias()

        except sqlite3.Error as erro:

            messagebox.showerror(
                "Erro no banco de dados",
                f"Não foi possível carregar o dashboard.\n\n{erro}"
            )
            return

        agora = datetime.now()

        pendencias = []
        alertas = []

        for registro in ocorrencias:

            status = str(
                obter_valor(registro, "status")
            ).strip()

            prioridade = str(
                obter_valor(registro, "prioridade")
            ).strip()

            id_ocorrencia = obter_valor(
                registro,
                "id_ocorrencia"
            )

            if status.lower() == "concluída":
                continue

            pendencias.append(registro)

            motivos = []

            if prioridade.lower() == "urgente":
                motivos.append("Prioridade urgente")

            if status.lower() == "aberta":

                data_abertura = obter_valor(
                    registro,
                    "data_abertura"
                )

                data_convertida = converter_data(data_abertura)

                if data_convertida is not None:

                    tempo_aberto = agora - data_convertida

                    if tempo_aberto.total_seconds() >= 86400:
                        motivos.append("Aberta há mais de 24 horas")

            if status.lower() == "em andamento":
                motivos.append("Atendimento em andamento")

            if motivos:

                alertas.append({
                    "id": id_ocorrencia,
                    "categoria": obter_valor(registro, "categoria"),
                    "setor": obter_valor(
                        registro,
                        "nome_setor",
                        "setor",
                        padrao="Não informado"
                    ),
                    "prioridade": prioridade,
                    "status": status,
                    "motivo": " | ".join(motivos)
                })

        total_pendencias = len(pendencias)


        area_cartoes = tk.Frame(
            self.area_conteudo,
            bg=COR_FUNDO
        )

        area_cartoes.pack(fill="x", padx=25)

        cartoes = [
            ("Total de ocorrências", indicadores.get("total", 0), COR_AZUL),
            ("Abertas", indicadores.get("abertas", 0), "#D58A24"),
            ("Em andamento", indicadores.get("andamento", 0), "#7657B8"),
            ("Concluídas", indicadores.get("concluidas", 0), COR_VERDE),
            ("Pendências", total_pendencias, COR_VERMELHO)
        ]

        for titulo, valor, cor in cartoes:

            cartao = tk.Frame(
                area_cartoes,
                bg=COR_BRANCO,
                padx=12,
                pady=13,
                highlightbackground="#E1E6ED",
                highlightthickness=1
            )

            cartao.pack(
                side="left",
                fill="both",
                expand=True,
                padx=4
            )

            tk.Label(
                cartao,
                text=titulo,
                bg=COR_BRANCO,
                fg="#718096",
                font=("Arial", 8)
            ).pack(anchor="w")

            tk.Label(
                cartao,
                text=str(valor),
                bg=COR_BRANCO,
                fg=cor,
                font=("Arial", 23, "bold")
            ).pack(anchor="w", pady=(6, 0))


        area_alertas = tk.Frame(
            self.area_conteudo,
            bg=COR_BRANCO,
            padx=15,
            pady=12,
            highlightbackground="#E1E6ED",
            highlightthickness=1
        )

        area_alertas.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(15, 10)
        )

        cabecalho_alertas = tk.Frame(
            area_alertas,
            bg=COR_BRANCO
        )

        cabecalho_alertas.pack(fill="x", pady=(0, 8))

        tk.Label(
            cabecalho_alertas,
            text="Painel de pendências e alertas",
            bg=COR_BRANCO,
            fg=COR_TEXTO,
            font=("Arial", 12, "bold")
        ).pack(side="left")

        tk.Label(
            cabecalho_alertas,
            text=f"{len(alertas)} alerta(s) identificado(s)",
            bg=COR_BRANCO,
            fg="#718096",
            font=("Arial", 9)
        ).pack(side="right")

        colunas_alertas = (
            "id", "categoria", "setor",
            "prioridade", "status", "motivo"
        )

        tabela_alertas = ttk.Treeview(
            area_alertas,
            columns=colunas_alertas,
            show="headings",
            height=4
        )

        configuracoes_alertas = {
            "id": ("ID", 45),
            "categoria": ("Categoria", 115),
            "setor": ("Setor responsável", 130),
            "prioridade": ("Prioridade", 85),
            "status": ("Status", 95),
            "motivo": ("Motivo do alerta", 250)
        }

        for coluna, (titulo, largura) in configuracoes_alertas.items():

            tabela_alertas.heading(coluna, text=titulo)

            tabela_alertas.column(
                coluna,
                width=largura,
                minwidth=45,
                anchor="center"
            )

        tabela_alertas.tag_configure(
            "urgente",
            background="#FCE8E8",
            foreground="#A52A2A"
        )

        tabela_alertas.tag_configure(
            "antigo",
            background="#FFF1D6",
            foreground="#95620D"
        )

        tabela_alertas.tag_configure(
            "andamento",
            background="#EEE9FA",
            foreground="#62439A"
        )

        tabela_alertas.tag_configure(
            "normal",
            background=COR_BRANCO,
            foreground=COR_TEXTO
        )

        barra_alertas = ttk.Scrollbar(
            area_alertas,
            orient="vertical",
            command=tabela_alertas.yview
        )

        tabela_alertas.configure(
            yscrollcommand=barra_alertas.set
        )

        tabela_alertas.pack(
            side="left",
            fill="both",
            expand=True
        )

        barra_alertas.pack(side="right", fill="y")

        if alertas:

            for alerta in alertas:

                motivo = alerta["motivo"]

                if "Prioridade urgente" in motivo:
                    tag = "urgente"

                elif "mais de 24 horas" in motivo:
                    tag = "antigo"

                elif "Atendimento em andamento" in motivo:
                    tag = "andamento"

                else:
                    tag = "normal"

                tabela_alertas.insert(
                    "",
                    "end",
                    iid=str(alerta["id"]),
                    values=(
                        alerta["id"],
                        alerta["categoria"],
                        alerta["setor"],
                        alerta["prioridade"],
                        alerta["status"],
                        alerta["motivo"]
                    ),
                    tags=(tag,)
                )

        else:

            tabela_alertas.insert(
                "",
                "end",
                values=(
                    "-",
                    "Nenhum alerta",
                    "-",
                    "-",
                    "-",
                    "Não existem pendências que exijam atenção."
                )
            )

        tabela_alertas.bind(
            "<Double-1>",
            lambda evento: self.abrir_alerta_selecionado(
                tabela_alertas
            )
        )

        tk.Label(
            area_alertas,
            text="Dica: dê dois cliques em um alerta para abrir a ocorrência.",
            bg=COR_BRANCO,
            fg="#718096",
            font=("Arial", 8)
        ).pack(anchor="w", pady=(7, 0))


        area_recentes = tk.Frame(
            self.area_conteudo,
            bg=COR_BRANCO,
            padx=15,
            pady=12,
            highlightbackground="#E1E6ED",
            highlightthickness=1
        )

        area_recentes.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 15)
        )

        tk.Label(
            area_recentes,
            text="Ocorrências recentes",
            bg=COR_BRANCO,
            fg=COR_TEXTO,
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 8))

        colunas = (
            "id", "quarto", "categoria",
            "setor", "prioridade", "status"
        )

        tabela = ttk.Treeview(
            area_recentes,
            columns=colunas,
            show="headings",
            height=4
        )

        configuracoes = {
            "id": ("ID", 45),
            "quarto": ("Quarto", 65),
            "categoria": ("Categoria", 125),
            "setor": ("Setor responsável", 135),
            "prioridade": ("Prioridade", 90),
            "status": ("Status", 110)
        }

        for coluna, (titulo, largura) in configuracoes.items():

            tabela.heading(coluna, text=titulo)

            tabela.column(
                coluna,
                width=largura,
                anchor="center"
            )

        tabela.pack(fill="both", expand=True)

        for registro in ocorrencias[:10]:

            tabela.insert(
                "",
                "end",
                values=(
                    obter_valor(registro, "id_ocorrencia"),
                    obter_valor(
                        registro,
                        "numero_quarto",
                        "quarto",
                        "numero",
                        padrao="Não informado"
                    ),
                    obter_valor(registro, "categoria"),
                    obter_valor(
                        registro,
                        "nome_setor",
                        "setor",
                        padrao="Não informado"
                    ),
                    obter_valor(registro, "prioridade"),
                    obter_valor(registro, "status")
                )
            )


    def abrir_alerta_selecionado(self, tabela_alertas):

        selecionado = tabela_alertas.selection()

        if not selecionado:
            return

        id_ocorrencia = selecionado[0]

        try:

            registros = database.listar_ocorrencias()

            registro = next(
                (
                    item for item in registros
                    if str(obter_valor(item, "id_ocorrencia"))
                    == str(id_ocorrencia)
                ),
                None
            )

            if registro is None:

                messagebox.showwarning(
                    "Ocorrência não encontrada",
                    "Este registro não está mais disponível."
                )

                self.mostrar_dashboard()
                return

            self.abrir_formulario(registro)

        except sqlite3.Error as erro:

            messagebox.showerror(
                "Erro",
                f"Não foi possível abrir a ocorrência.\n\n{erro}"
            )


    def mostrar_ocorrencias(self):

        self.limpar_conteudo()
        self.tela_atual = "ocorrencias"

        self.criar_titulo(
            "Ocorrências",
            "Consulte, pesquise, edite e exclua registros."
        )

        area_busca = tk.Frame(
            self.area_conteudo,
            bg=COR_FUNDO
        )

        area_busca.pack(fill="x", padx=30, pady=(0, 15))

        self.campo_busca = tk.Entry(
            area_busca,
            font=("Arial", 10),
            width=35,
            relief="solid",
            bd=1
        )

        self.campo_busca.pack(side="left", ipady=7)
        self.campo_busca.insert(0, "Pesquisar ocorrência...")

        tk.Button(
            area_busca,
            text="Pesquisar",
            command=self.pesquisar_ocorrencias,
            bg=COR_AZUL,
            fg=COR_BRANCO,
            relief="flat",
            padx=18,
            pady=8,
            cursor="hand2"
        ).pack(side="left", padx=8)

        tk.Button(
            area_busca,
            text="Limpar busca",
            command=self.mostrar_ocorrencias,
            bg="#E2E8F0",
            fg=COR_TEXTO,
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2"
        ).pack(side="left")

        area_tabela = tk.Frame(
            self.area_conteudo,
            bg=COR_BRANCO
        )

        area_tabela.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 15)
        )

        colunas = (
            "id", "quarto", "hospede",
            "categoria", "descricao", "setor",
            "prioridade", "status", "abertura"
        )

        self.tabela = ttk.Treeview(
            area_tabela,
            columns=colunas,
            show="headings"
        )

        configuracoes = {
            "id": ("ID", 45),
            "quarto": ("Quarto", 65),
            "hospede": ("Hóspede", 110),
            "categoria": ("Categoria", 100),
            "descricao": ("Descrição", 180),
            "setor": ("Setor", 115),
            "prioridade": ("Prioridade", 85),
            "status": ("Status", 95),
            "abertura": ("Abertura", 110)
        }

        for coluna, (titulo, largura) in configuracoes.items():

            self.tabela.heading(coluna, text=titulo)

            self.tabela.column(
                coluna,
                width=largura,
                minwidth=45,
                anchor="center"
            )

        barra = ttk.Scrollbar(
            area_tabela,
            orient="vertical",
            command=self.tabela.yview
        )

        self.tabela.configure(yscrollcommand=barra.set)

        self.tabela.pack(
            side="left",
            fill="both",
            expand=True
        )

        barra.pack(side="right", fill="y")

        area_botoes = tk.Frame(
            self.area_conteudo,
            bg=COR_FUNDO
        )

        area_botoes.pack(
            fill="x",
            padx=30,
            pady=(0, 25)
        )

        botoes = [
            ("Nova ocorrência", self.nova_ocorrencia, COR_AZUL),
            ("Editar selecionada", self.editar_ocorrencia, COR_VERDE),
            ("Excluir selecionada", self.excluir_ocorrencia, COR_VERMELHO),
            ("Ver histórico", self.visualizar_historico, "#7657B8")
        ]

        for texto, comando, cor in botoes:

            tk.Button(
                area_botoes,
                text=texto,
                command=comando,
                bg=cor,
                fg=COR_BRANCO,
                relief="flat",
                padx=18,
                pady=10,
                cursor="hand2"
            ).pack(side="left", padx=5)

        self.carregar_tabela()

    def carregar_tabela(self, filtro=""):

        for item in self.tabela.get_children():
            self.tabela.delete(item)

        try:

            ocorrencias = database.listar_ocorrencias(filtro)

            for registro in ocorrencias:

                self.tabela.insert(
                    "",
                    "end",
                    values=(
                        obter_valor(registro, "id_ocorrencia"),
                        obter_valor(
                            registro,
                            "numero_quarto",
                            "quarto",
                            "numero",
                            padrao="Não informado"
                        ),
                        obter_valor(registro, "hospede"),
                        obter_valor(registro, "categoria"),
                        obter_valor(registro, "descricao"),
                        obter_valor(
                            registro,
                            "nome_setor",
                            "setor",
                            padrao="Não informado"
                        ),
                        obter_valor(registro, "prioridade"),
                        obter_valor(registro, "status"),
                        obter_valor(registro, "data_abertura")
                    )
                )

        except sqlite3.Error as erro:

            messagebox.showerror(
                "Erro ao carregar",
                f"Não foi possível carregar as ocorrências.\n\n{erro}"
            )

    def pesquisar_ocorrencias(self):

        termo = self.campo_busca.get().strip()

        if termo == "Pesquisar ocorrência...":
            termo = ""

        self.carregar_tabela(termo)


    def nova_ocorrencia(self):
        self.abrir_formulario()

    def editar_ocorrencia(self):

        selecionado = self.tabela.selection()

        if not selecionado:

            messagebox.showwarning(
                "Atenção",
                "Selecione uma ocorrência para editar."
            )
            return

        valores = self.tabela.item(
            selecionado[0],
            "values"
        )

        id_ocorrencia = valores[0]

        try:

            registros = database.listar_ocorrencias()

            registro = next(
                (
                    item for item in registros
                    if str(obter_valor(item, "id_ocorrencia"))
                    == str(id_ocorrencia)
                ),
                None
            )

            if registro is None:

                messagebox.showerror(
                    "Erro",
                    "Não foi possível localizar a ocorrência."
                )
                return

            self.abrir_formulario(registro)

        except sqlite3.Error as erro:

            messagebox.showerror(
                "Erro",
                f"Não foi possível abrir o registro.\n\n{erro}"
            )

    def abrir_formulario(self, registro=None):

        editando = registro is not None

        formulario = tk.Toplevel(self.janela)

        formulario.title(
            "Editar ocorrência" if editando else "Nova ocorrência"
        )

        formulario.geometry("570x680")
        formulario.resizable(False, False)
        formulario.configure(bg=COR_BRANCO)
        formulario.transient(self.janela)
        formulario.grab_set()

        tk.Label(
            formulario,
            text="Editar ocorrência" if editando else "Cadastrar ocorrência",
            bg=COR_BRANCO,
            fg=COR_TEXTO,
            font=("Arial", 17, "bold")
        ).pack(anchor="w", padx=30, pady=(25, 5))

        tk.Label(
            formulario,
            text="Preencha as informações da solicitação.",
            bg=COR_BRANCO,
            fg="#718096",
            font=("Arial", 9)
        ).pack(anchor="w", padx=30, pady=(0, 20))

        area = tk.Frame(
            formulario,
            bg=COR_BRANCO
        )

        area.pack(fill="both", expand=True, padx=30)

        try:

            quartos = database.listar_quartos()
            setores = database.listar_setores()

        except sqlite3.Error as erro:

            messagebox.showerror(
                "Erro no banco de dados",
                f"Não foi possível carregar quartos e setores.\n\n{erro}",
                parent=formulario
            )

            formulario.destroy()
            return

        quartos_opcoes = {
            "Sem quarto associado": None
        }

        for quarto in quartos:

            numero = obter_valor(quarto, "numero")
            id_quarto = obter_valor(quarto, "id_quarto")
            tipo = obter_valor(quarto, "tipo")

            texto = f"{numero} - {tipo}"
            quartos_opcoes[texto] = id_quarto

        setores_opcoes = {}

        for setor in setores:

            nome = obter_valor(setor, "nome")
            id_setor = obter_valor(setor, "id_setor")

            setores_opcoes[nome] = id_setor

        def criar_rotulo(texto):

            tk.Label(
                area,
                text=texto,
                bg=COR_BRANCO,
                fg=COR_TEXTO,
                font=("Arial", 9, "bold")
            ).pack(anchor="w", pady=(5, 4))

        def criar_campo(texto, valor=""):

            criar_rotulo(texto)

            campo = tk.Entry(
                area,
                font=("Arial", 10),
                relief="solid",
                bd=1
            )

            campo.pack(fill="x", ipady=6)
            campo.insert(0, valor)

            return campo

        def criar_combo(texto, opcoes, valor_inicial=""):

            criar_rotulo(texto)

            combo = ttk.Combobox(
                area,
                values=opcoes,
                state="readonly",
                font=("Arial", 10)
            )

            combo.pack(fill="x", ipady=4)

            if valor_inicial in opcoes:
                combo.set(valor_inicial)

            elif opcoes:
                combo.current(0)

            return combo

        hospede = criar_campo(
            "Nome do hóspede",
            obter_valor(registro, "hospede") if editando else ""
        )

        quarto_inicial = "Sem quarto associado"

        if editando:

            id_quarto_atual = obter_valor(
                registro,
                "id_quarto",
                padrao=None
            )

            for texto, identificador in quartos_opcoes.items():

                if str(identificador) == str(id_quarto_atual):
                    quarto_inicial = texto
                    break

        quarto = criar_combo(
            "Quarto",
            list(quartos_opcoes.keys()),
            quarto_inicial
        )

        categorias = [
            "Solicitação de hóspede",
            "Manutenção",
            "Limpeza",
            "Governança",
            "Alimentos e Bebidas",
            "Reclamação",
            "Outros"
        ]

        categoria_inicial = (
            obter_valor(registro, "categoria")
            if editando else categorias[0]
        )

        categoria = criar_combo(
            "Categoria",
            categorias,
            categoria_inicial
        )

        criar_rotulo("Descrição")

        descricao = tk.Text(
            area,
            height=4,
            font=("Arial", 10),
            relief="solid",
            bd=1,
            wrap="word"
        )

        descricao.pack(fill="x")

        if editando:

            descricao.insert(
                "1.0",
                obter_valor(registro, "descricao")
            )

        setor_inicial = ""

        if editando:

            nome_setor_atual = obter_valor(
                registro,
                "nome_setor",
                "setor"
            )

            if nome_setor_atual in setores_opcoes:
                setor_inicial = nome_setor_atual

        setor = criar_combo(
            "Setor responsável",
            list(setores_opcoes.keys()),
            setor_inicial
        )

        prioridades = [
            "Baixa",
            "Média",
            "Alta",
            "Urgente"
        ]

        prioridade = criar_combo(
            "Prioridade",
            prioridades,
            obter_valor(registro, "prioridade")
            if editando else "Média"
        )

        status = criar_combo(
            "Status",
            ["Aberta", "Em andamento", "Concluída"],
            obter_valor(registro, "status")
            if editando else "Aberta"
        )


        def salvar():

            nome_hospede = hospede.get().strip()
            categoria_valor = categoria.get().strip()
            descricao_valor = descricao.get("1.0", "end").strip()
            setor_valor = setor.get().strip()
            prioridade_valor = prioridade.get().strip()
            status_valor = status.get().strip()
            quarto_valor = quarto.get().strip()

            if not categoria_valor:

                messagebox.showwarning(
                    "Campo obrigatório",
                    "Selecione uma categoria.",
                    parent=formulario
                )

                categoria.focus_set()
                return

            if not descricao_valor:

                messagebox.showwarning(
                    "Campo obrigatório",
                    "Informe a descrição da ocorrência.",
                    parent=formulario
                )

                descricao.focus_set()
                return

            if not setor_valor:

                messagebox.showwarning(
                    "Campo obrigatório",
                    "Selecione o setor responsável.",
                    parent=formulario
                )

                setor.focus_set()
                return

            if not prioridade_valor:

                messagebox.showwarning(
                    "Campo obrigatório",
                    "Selecione a prioridade.",
                    parent=formulario
                )

                prioridade.focus_set()
                return

            if not status_valor:

                messagebox.showwarning(
                    "Campo obrigatório",
                    "Selecione o status.",
                    parent=formulario
                )

                status.focus_set()
                return

            id_quarto = quartos_opcoes.get(quarto_valor)
            id_setor = setores_opcoes.get(setor_valor)

            if id_setor is None:

                messagebox.showwarning(
                    "Campo obrigatório",
                    "Selecione um setor válido.",
                    parent=formulario
                )

                return

            try:

                if editando:

                    id_ocorrencia = obter_valor(
                        registro,
                        "id_ocorrencia"
                    )

                    database.atualizar_ocorrencia(
                        id_ocorrencia,
                        id_quarto,
                        nome_hospede,
                        categoria_valor,
                        descricao_valor,
                        id_setor,
                        prioridade_valor,
                        status_valor
                    )

                    mensagem = "Ocorrência atualizada com sucesso!"

                else:

                    database.cadastrar_ocorrencia(
                        id_quarto,
                        nome_hospede,
                        categoria_valor,
                        descricao_valor,
                        id_setor,
                        prioridade_valor
                    )

                    mensagem = "Ocorrência cadastrada com sucesso!"

                messagebox.showinfo(
                    "Sucesso",
                    mensagem,
                    parent=formulario
                )

                formulario.destroy()

                if self.tela_atual == "ocorrencias":
                    self.mostrar_ocorrencias()

                elif self.tela_atual == "relatorios":
                    self.mostrar_relatorios()

                elif self.tela_atual == "desempenho":
                    self.mostrar_desempenho()

                else:
                    self.mostrar_dashboard()

            except (sqlite3.Error, ValueError, TypeError) as erro:

                messagebox.showerror(
                    "Erro ao salvar",
                    f"Não foi possível salvar a ocorrência.\n\n{erro}",
                    parent=formulario
                )

        area_botoes = tk.Frame(
            formulario,
            bg=COR_BRANCO
        )

        area_botoes.pack(
            fill="x",
            padx=30,
            pady=20
        )

        tk.Button(
            area_botoes,
            text="Salvar ocorrência",
            command=salvar,
            bg=COR_AZUL,
            fg=COR_BRANCO,
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        ).pack(side="left")

        tk.Button(
            area_botoes,
            text="Cancelar",
            command=formulario.destroy,
            bg="#E2E8F0",
            fg=COR_TEXTO,
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2"
        ).pack(side="left", padx=10)


    def visualizar_historico(self):

        selecionado = self.tabela.selection()

        if not selecionado:

            messagebox.showwarning(
                "Atenção",
                "Selecione uma ocorrência para consultar seu histórico."
            )

            return

        valores = self.tabela.item(
            selecionado[0],
            "values"
        )

        id_ocorrencia = valores[0]

        try:
            historico = database.listar_historico(id_ocorrencia)

        except sqlite3.Error as erro:

            messagebox.showerror(
                "Erro",
                f"Não foi possível consultar o histórico.\n\n{erro}"
            )

            return

        janela_historico = tk.Toplevel(self.janela)

        janela_historico.title(
            f"Histórico da ocorrência #{id_ocorrencia}"
        )

        janela_historico.geometry("950x480")
        janela_historico.minsize(750, 350)
        janela_historico.configure(bg=COR_FUNDO)
        janela_historico.transient(self.janela)

        cabecalho = tk.Frame(
            janela_historico,
            bg=COR_FUNDO
        )

        cabecalho.pack(fill="x", padx=25, pady=20)

        tk.Label(
            cabecalho,
            text=f"Histórico da ocorrência #{id_ocorrencia}",
            bg=COR_FUNDO,
            fg=COR_TEXTO,
            font=("Arial", 18, "bold")
        ).pack(anchor="w")

        tk.Label(
            cabecalho,
            text="Consulte as alterações realizadas neste registro.",
            bg=COR_FUNDO,
            fg="#718096",
            font=("Arial", 10)
        ).pack(anchor="w", pady=(5, 0))

        painel = tk.Frame(
            janela_historico,
            bg=COR_BRANCO
        )

        painel.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 20)
        )

        colunas = (
            "data_hora",
            "acao",
            "campo",
            "valor_anterior",
            "valor_novo",
            "usuario"
        )

        tabela_historico = ttk.Treeview(
            painel,
            columns=colunas,
            show="headings"
        )

        configuracoes = {
            "data_hora": ("Data e hora", 135),
            "acao": ("Ação", 150),
            "campo": ("Campo alterado", 120),
            "valor_anterior": ("Valor anterior", 150),
            "valor_novo": ("Novo valor", 150),
            "usuario": ("Usuário", 120)
        }

        for coluna, (titulo, largura) in configuracoes.items():

            tabela_historico.heading(
                coluna,
                text=titulo
            )

            tabela_historico.column(
                coluna,
                width=largura,
                minwidth=80,
                anchor="center"
            )

        barra_vertical = ttk.Scrollbar(
            painel,
            orient="vertical",
            command=tabela_historico.yview
        )

        barra_horizontal = ttk.Scrollbar(
            painel,
            orient="horizontal",
            command=tabela_historico.xview
        )

        tabela_historico.configure(
            yscrollcommand=barra_vertical.set,
            xscrollcommand=barra_horizontal.set
        )

        tabela_historico.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        barra_vertical.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        barra_horizontal.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        painel.grid_rowconfigure(0, weight=1)
        painel.grid_columnconfigure(0, weight=1)

        if not historico:

            tabela_historico.insert(
                "",
                "end",
                values=(
                    "-",
                    "Nenhum histórico",
                    "-",
                    "-",
                    "Nenhuma alteração registrada",
                    "-"
                )
            )

        else:

            for registro in historico:

                tabela_historico.insert(
                    "",
                    "end",
                    values=(
                        obter_valor(registro, "data_hora", padrao="-"),
                        obter_valor(registro, "acao", padrao="-"),
                        obter_valor(registro, "campo", padrao="-"),
                        obter_valor(registro, "valor_anterior", padrao="-"),
                        obter_valor(registro, "valor_novo", padrao="-"),
                        obter_valor(registro, "usuario", padrao="-")
                    )
                )

        tk.Button(
            janela_historico,
            text="Fechar",
            command=janela_historico.destroy,
            bg=COR_AZUL,
            fg=COR_BRANCO,
            relief="flat",
            padx=25,
            pady=9,
            cursor="hand2"
        ).pack(pady=(0, 15))


    def excluir_ocorrencia(self):

        selecionado = self.tabela.selection()

        if not selecionado:

            messagebox.showwarning(
                "Atenção",
                "Selecione uma ocorrência para excluir."
            )

            return

        valores = self.tabela.item(
            selecionado[0],
            "values"
        )

        id_ocorrencia = valores[0]

        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            "Deseja realmente excluir esta ocorrência?"
        )

        if not confirmar:
            return

        try:

            database.excluir_ocorrencia(id_ocorrencia)

            messagebox.showinfo(
                "Sucesso",
                "Ocorrência excluída com sucesso!"
            )

            self.mostrar_ocorrencias()

        except sqlite3.Error as erro:

            messagebox.showerror(
                "Erro",
                f"Não foi possível excluir a ocorrência.\n\n{erro}"
            )


    def exportar_relatorio_csv(self):

        try:

            ocorrencias = database.listar_ocorrencias()

            if not ocorrencias:

                messagebox.showinfo(
                    "Exportação",
                    "Não existem ocorrências cadastradas para exportar."
                )

                return

            caminho = filedialog.asksaveasfilename(
                title="Salvar relatório de ocorrências",
                defaultextension=".csv",
                filetypes=[
                    ("Arquivo CSV", "*.csv"),
                    ("Todos os arquivos", "*.*")
                ],
                initialfile="relatorio_hotelflow.csv"
            )

            if not caminho:
                return

            colunas = [
                ("ID", "id_ocorrencia"),
                ("Quarto", "numero_quarto"),
                ("Hóspede", "hospede"),
                ("Categoria", "categoria"),
                ("Descrição", "descricao"),
                ("Setor responsável", "nome_setor"),
                ("Prioridade", "prioridade"),
                ("Status", "status"),
                ("Data de abertura", "data_abertura"),
                ("Data de conclusão", "data_conclusao")
            ]

            with open(
                caminho,
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as arquivo:

                escritor = csv.writer(
                    arquivo,
                    delimiter=";"
                )

                escritor.writerow([
                    titulo for titulo, campo in colunas
                ])

                for ocorrencia in ocorrencias:

                    valores = []

                    for titulo, campo in colunas:

                        valor = obter_valor(
                            ocorrencia,
                            campo,
                            padrao=""
                        )

                        valores.append(
                            "" if valor is None else str(valor)
                        )

                    escritor.writerow(valores)

            messagebox.showinfo(
                "Exportação concluída",
                f"Relatório exportado com sucesso!\n\n"
                f"Arquivo salvo em:\n{caminho}"
            )

        except (sqlite3.Error, OSError, csv.Error) as erro:

            messagebox.showerror(
                "Erro na exportação",
                f"Não foi possível exportar o relatório.\n\n{erro}"
            )


    def mostrar_relatorios(self):

        self.limpar_conteudo()
        self.tela_atual = "relatorios"

        self.criar_titulo(
            "Relatórios gerenciais",
            "Acompanhe a distribuição das ocorrências por status, prioridade e setor."
        )

        try:
            ocorrencias = database.listar_ocorrencias()

        except sqlite3.Error as erro:

            messagebox.showerror(
                "Erro no banco de dados",
                f"Não foi possível gerar os relatórios.\n\n{erro}"
            )

            return

        total = len(ocorrencias)

        contagem_status = {
            "Aberta": 0,
            "Em andamento": 0,
            "Concluída": 0
        }

        contagem_prioridade = {
            "Baixa": 0,
            "Média": 0,
            "Alta": 0,
            "Urgente": 0
        }

        contagem_setores = {}

        for registro in ocorrencias:

            status_registro = str(
                obter_valor(registro, "status", padrao="Não informado")
            )

            prioridade_registro = str(
                obter_valor(registro, "prioridade", padrao="Não informada")
            )

            setor_registro = str(
                obter_valor(
                    registro,
                    "nome_setor",
                    "setor",
                    padrao="Não informado"
                )
            )

            contagem_status[status_registro] = (
                contagem_status.get(status_registro, 0) + 1
            )

            contagem_prioridade[prioridade_registro] = (
                contagem_prioridade.get(prioridade_registro, 0) + 1
            )

            contagem_setores[setor_registro] = (
                contagem_setores.get(setor_registro, 0) + 1
            )

        # CARTÕES

        area_cartoes = tk.Frame(
            self.area_conteudo,
            bg=COR_FUNDO
        )

        area_cartoes.pack(
            fill="x",
            padx=25,
            pady=(0, 18)
        )

        concluidas = contagem_status.get("Concluída", 0)
        abertas = contagem_status.get("Aberta", 0)
        andamento = contagem_status.get("Em andamento", 0)

        cartoes = [
            ("Total registradas", total, COR_AZUL),
            ("Abertas", abertas, "#D58A24"),
            ("Em andamento", andamento, "#7657B8"),
            ("Concluídas", concluidas, COR_VERDE)
        ]

        for titulo, valor, cor in cartoes:

            cartao = tk.Frame(
                area_cartoes,
                bg=COR_BRANCO,
                padx=15,
                pady=14,
                highlightbackground="#E1E6ED",
                highlightthickness=1
            )

            cartao.pack(
                side="left",
                fill="both",
                expand=True,
                padx=5
            )

            tk.Label(
                cartao,
                text=titulo,
                bg=COR_BRANCO,
                fg="#718096",
                font=("Arial", 9)
            ).pack(anchor="w")

            tk.Label(
                cartao,
                text=str(valor),
                bg=COR_BRANCO,
                fg=cor,
                font=("Arial", 22, "bold")
            ).pack(anchor="w", pady=(5, 0))


        def criar_quadro_relatorio(parent, titulo, dados):

            quadro = tk.Frame(
                parent,
                bg=COR_BRANCO,
                padx=14,
                pady=12,
                highlightbackground="#E1E6ED",
                highlightthickness=1
            )

            tk.Label(
                quadro,
                text=titulo,
                bg=COR_BRANCO,
                fg=COR_TEXTO,
                font=("Arial", 11, "bold")
            ).pack(anchor="w", pady=(0, 9))

            tabela = ttk.Treeview(
                quadro,
                columns=("item", "quantidade", "percentual"),
                show="headings",
                height=min(max(len(dados), 3), 6)
            )

            tabela.heading("item", text="Classificação")
            tabela.heading("quantidade", text="Quantidade")
            tabela.heading("percentual", text="Participação")

            tabela.column("item", width=180, anchor="w")
            tabela.column("quantidade", width=95, anchor="center")
            tabela.column("percentual", width=105, anchor="center")

            for nome, quantidade in dados:

                percentual = (
                    quantidade / total * 100
                ) if total else 0

                tabela.insert(
                    "",
                    "end",
                    values=(
                        nome,
                        quantidade,
                        f"{percentual:.1f}%"
                    )
                )

            if not dados:

                tabela.insert(
                    "",
                    "end",
                    values=("Nenhum registro", 0, "0,0%")
                )

            tabela.pack(fill="both", expand=True)

            return quadro

        area_tabelas = tk.Frame(
            self.area_conteudo,
            bg=COR_FUNDO
        )

        area_tabelas.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 12)
        )

        area_tabelas.grid_columnconfigure(0, weight=1)
        area_tabelas.grid_columnconfigure(1, weight=1)

        dados_status = list(contagem_status.items())
        dados_prioridade = list(contagem_prioridade.items())

        dados_setores = sorted(
            contagem_setores.items(),
            key=lambda item: item[1],
            reverse=True
        )

        quadro_status = criar_quadro_relatorio(
            area_tabelas,
            "Ocorrências por status",
            dados_status
        )

        quadro_status.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 7),
            pady=(0, 12)
        )

        quadro_prioridade = criar_quadro_relatorio(
            area_tabelas,
            "Ocorrências por prioridade",
            dados_prioridade
        )

        quadro_prioridade.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(7, 0),
            pady=(0, 12)
        )

        quadro_setores = criar_quadro_relatorio(
            area_tabelas,
            "Ocorrências por setor responsável",
            dados_setores
        )

        quadro_setores.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="nsew"
        )

        area_botoes = tk.Frame(
            self.area_conteudo,
            bg=COR_FUNDO
        )

        area_botoes.pack(
            anchor="e",
            padx=30,
            pady=(0, 18)
        )

        tk.Button(
            area_botoes,
            text="Exportar CSV",
            command=self.exportar_relatorio_csv,
            bg=COR_VERDE,
            fg=COR_BRANCO,
            relief="flat",
            padx=18,
            pady=9,
            cursor="hand2"
        ).pack(side="left", padx=5)

        tk.Button(
            area_botoes,
            text="Atualizar relatórios",
            command=self.mostrar_relatorios,
            bg=COR_AZUL,
            fg=COR_BRANCO,
            relief="flat",
            padx=18,
            pady=9,
            cursor="hand2"
        ).pack(side="left", padx=5)


    def formatar_tempo(self, minutos):
        """Converte minutos em uma apresentação legível."""

        minutos = round(float(minutos or 0))

        if minutos < 60:
            return f"{minutos} min"

        horas = minutos // 60
        resto = minutos % 60

        if resto == 0:
            return f"{horas} h"

        return f"{horas} h {resto} min"

    def mostrar_desempenho(self):

        self.limpar_conteudo()
        self.tela_atual = "desempenho"

        self.criar_titulo(
            "Desempenho",
            "Acompanhe o tempo de atendimento e os resultados dos setores."
        )

        try:

            dados = database.obter_dados_desempenho(
                self.periodo_desempenho
            )

        except (sqlite3.Error, ValueError, TypeError) as erro:

            messagebox.showerror(
                "Erro ao carregar desempenho",
                f"Não foi possível consultar os indicadores.\n\n{erro}"
            )

            return


        area_filtro = tk.Frame(
            self.area_conteudo,
            bg=COR_FUNDO
        )

        area_filtro.pack(
            fill="x",
            padx=30,
            pady=(0, 15)
        )

        tk.Label(
            area_filtro,
            text="Período de análise:",
            bg=COR_FUNDO,
            fg=COR_TEXTO,
            font=("Arial", 10, "bold")
        ).pack(side="left", padx=(0, 10))

        periodos = {
            "Todo o período": "todo",
            "Hoje": "hoje",
            "Últimos 7 dias": "7dias",
            "Este mês": "mes"
        }

        periodo_atual = next(
            (
                nome for nome, valor in periodos.items()
                if valor == self.periodo_desempenho
            ),
            "Todo o período"
        )

        combo_periodo = ttk.Combobox(
            area_filtro,
            values=list(periodos.keys()),
            state="readonly",
            width=22,
            font=("Arial", 10)
        )

        combo_periodo.set(periodo_atual)
        combo_periodo.pack(side="left", ipady=4)

        combo_periodo.bind(
            "<<ComboboxSelected>>",
            lambda evento: self.alterar_periodo_desempenho(
                periodos[combo_periodo.get()]
            )
        )

        tk.Button(
            area_filtro,
            text="Atualizar",
            command=self.mostrar_desempenho,
            bg=COR_AZUL,
            fg=COR_BRANCO,
            relief="flat",
            padx=16,
            pady=7,
            cursor="hand2"
        ).pack(side="left", padx=10)


        area_cartoes = tk.Frame(
            self.area_conteudo,
            bg=COR_FUNDO
        )

        area_cartoes.pack(
            fill="x",
            padx=25,
            pady=(0, 15)
        )

        cartoes = [
            ("Ocorrências no período", dados["total"], COR_AZUL),
            ("Concluídas", dados["concluidas"], COR_VERDE),
            ("Pendentes", dados["pendentes"], COR_VERMELHO),
            (
                "Taxa de conclusão",
                f'{dados["taxa_conclusao"]:.1f}%'.replace(".", ","),
                "#7657B8"
            )
        ]

        for titulo, valor, cor in cartoes:

            cartao = tk.Frame(
                area_cartoes,
                bg=COR_BRANCO,
                padx=12,
                pady=12,
                highlightbackground="#E1E6ED",
                highlightthickness=1
            )

            cartao.pack(
                side="left",
                fill="both",
                expand=True,
                padx=4
            )

            tk.Label(
                cartao,
                text=titulo,
                bg=COR_BRANCO,
                fg="#718096",
                font=("Arial", 8)
            ).pack(anchor="w")

            tk.Label(
                cartao,
                text=str(valor),
                bg=COR_BRANCO,
                fg=cor,
                font=("Arial", 20, "bold")
            ).pack(anchor="w", pady=(6, 0))


        area_resumo = tk.Frame(
            self.area_conteudo,
            bg=COR_BRANCO,
            padx=18,
            pady=13,
            highlightbackground="#E1E6ED",
            highlightthickness=1
        )

        area_resumo.pack(
            fill="x",
            padx=30,
            pady=(0, 15)
        )

        tk.Label(
            area_resumo,
            text="Tempo médio de resolução",
            bg=COR_BRANCO,
            fg="#718096",
            font=("Arial", 9)
        ).pack(anchor="w")

        tk.Label(
            area_resumo,
            text=self.formatar_tempo(
                dados["tempo_medio_minutos"]
            ),
            bg=COR_BRANCO,
            fg=COR_AZUL,
            font=("Arial", 21, "bold")
        ).pack(anchor="w", pady=(3, 5))

        tk.Label(
            area_resumo,
            text=(
                "Setor com maior volume: "
                + dados["setor_destaque"]
            ),
            bg=COR_BRANCO,
            fg=COR_TEXTO,
            font=("Arial", 9)
        ).pack(anchor="w")


        quadro_setores = tk.Frame(
            self.area_conteudo,
            bg=COR_BRANCO,
            padx=15,
            pady=12,
            highlightbackground="#E1E6ED",
            highlightthickness=1
        )

        quadro_setores.pack(
            fill="x",
            padx=30,
            pady=(0, 15)
        )

        tk.Label(
            quadro_setores,
            text="Desempenho por setor",
            bg=COR_BRANCO,
            fg=COR_TEXTO,
            font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(0, 8))

        colunas_setores = (
            "setor",
            "total",
            "concluidas",
            "media"
        )

        tabela_setores = ttk.Treeview(
            quadro_setores,
            columns=colunas_setores,
            show="headings",
            height=4
        )

        configuracoes_setores = {
            "setor": ("Setor responsável", 230),
            "total": ("Ocorrências", 100),
            "concluidas": ("Concluídas", 100),
            "media": ("Tempo médio", 130)
        }

        for coluna, (titulo, largura) in configuracoes_setores.items():

            tabela_setores.heading(coluna, text=titulo)

            tabela_setores.column(
                coluna,
                width=largura,
                anchor="center"
            )

        tabela_setores.pack(fill="x")

        if dados["setores"]:

            for setor in dados["setores"]:

                media = (
                    self.formatar_tempo(setor["media_minutos"])
                    if setor["concluidas"] > 0
                    else "Sem conclusão"
                )

                tabela_setores.insert(
                    "",
                    "end",
                    values=(
                        setor["setor"],
                        setor["total"],
                        setor["concluidas"],
                        media
                    )
                )

        else:

            tabela_setores.insert(
                "",
                "end",
                values=(
                    "Nenhuma ocorrência no período",
                    0,
                    0,
                    "-"
                )
            )


        quadro_ocorrencias = tk.Frame(
            self.area_conteudo,
            bg=COR_BRANCO,
            padx=15,
            pady=12,
            highlightbackground="#E1E6ED",
            highlightthickness=1
        )

        quadro_ocorrencias.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 12)
        )

        tk.Label(
            quadro_ocorrencias,
            text="Detalhamento das ocorrências",
            bg=COR_BRANCO,
            fg=COR_TEXTO,
            font=("Arial", 11, "bold")
        ).pack(anchor="w", pady=(0, 8))

        colunas_ocorrencias = (
            "id",
            "categoria",
            "setor",
            "prioridade",
            "status",
            "abertura",
            "conclusao"
        )

        tabela_ocorrencias = ttk.Treeview(
            quadro_ocorrencias,
            columns=colunas_ocorrencias,
            show="headings",
            height=5
        )

        configuracoes_ocorrencias = {
            "id": ("ID", 45),
            "categoria": ("Categoria", 120),
            "setor": ("Setor", 125),
            "prioridade": ("Prioridade", 85),
            "status": ("Status", 100),
            "abertura": ("Abertura", 125),
            "conclusao": ("Conclusão", 125)
        }

        for coluna, (titulo, largura) in configuracoes_ocorrencias.items():

            tabela_ocorrencias.heading(coluna, text=titulo)

            tabela_ocorrencias.column(
                coluna,
                width=largura,
                minwidth=45,
                anchor="center"
            )

        barra = ttk.Scrollbar(
            quadro_ocorrencias,
            orient="vertical",
            command=tabela_ocorrencias.yview
        )

        tabela_ocorrencias.configure(
            yscrollcommand=barra.set
        )

        tabela_ocorrencias.pack(
            side="left",
            fill="both",
            expand=True
        )

        barra.pack(side="right", fill="y")

        for ocorrencia in dados["ocorrencias"]:

            tabela_ocorrencias.insert(
                "",
                "end",
                values=(
                    ocorrencia["id"],
                    ocorrencia["categoria"],
                    ocorrencia["setor"],
                    ocorrencia["prioridade"],
                    ocorrencia["status"],
                    ocorrencia["data_abertura"],
                    ocorrencia["data_conclusao"] or "Não concluída"
                )
            )


        area_botoes = tk.Frame(
            self.area_conteudo,
            bg=COR_FUNDO
        )

        area_botoes.pack(
            anchor="e",
            padx=30,
            pady=(0, 15)
        )

        tk.Button(
            area_botoes,
            text="Exportar desempenho CSV",
            command=self.exportar_desempenho_csv,
            bg=COR_VERDE,
            fg=COR_BRANCO,
            relief="flat",
            padx=18,
            pady=9,
            cursor="hand2"
        ).pack(side="left")

    def alterar_periodo_desempenho(self, periodo):

        self.periodo_desempenho = periodo
        self.mostrar_desempenho()

    def exportar_desempenho_csv(self):

        try:

            dados = database.obter_dados_desempenho(
                self.periodo_desempenho
            )

            caminho = filedialog.asksaveasfilename(
                title="Exportar relatório de desempenho",
                defaultextension=".csv",
                filetypes=[
                    ("Arquivo CSV", "*.csv"),
                    ("Todos os arquivos", "*.*")
                ],
                initialfile="desempenho_hotelflow.csv"
            )

            if not caminho:
                return

            with open(
                caminho,
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as arquivo:

                escritor = csv.writer(
                    arquivo,
                    delimiter=";"
                )

                escritor.writerow([
                    "RELATÓRIO DE DESEMPENHO - HOTELFLOW"
                ])

                escritor.writerow([
                    "Período",
                    self.periodo_desempenho
                ])

                escritor.writerow([])

                escritor.writerow([
                    "Indicador",
                    "Resultado"
                ])

                escritor.writerow([
                    "Total de ocorrências",
                    dados["total"]
                ])

                escritor.writerow([
                    "Concluídas",
                    dados["concluidas"]
                ])

                escritor.writerow([
                    "Pendentes",
                    dados["pendentes"]
                ])

                escritor.writerow([
                    "Taxa de conclusão",
                    f'{dados["taxa_conclusao"]:.2f}%'
                ])

                escritor.writerow([
                    "Tempo médio de resolução (minutos)",
                    dados["tempo_medio_minutos"]
                ])

                escritor.writerow([
                    "Setor com maior volume",
                    dados["setor_destaque"]
                ])

                escritor.writerow([])

                escritor.writerow([
                    "DESEMPENHO POR SETOR"
                ])

                escritor.writerow([
                    "Setor",
                    "Total de ocorrências",
                    "Concluídas",
                    "Tempo médio em minutos"
                ])

                for setor in dados["setores"]:

                    escritor.writerow([
                        setor["setor"],
                        setor["total"],
                        setor["concluidas"],
                        setor["media_minutos"]
                    ])

                escritor.writerow([])

                escritor.writerow([
                    "DETALHAMENTO DAS OCORRÊNCIAS"
                ])

                escritor.writerow([
                    "ID",
                    "Categoria",
                    "Setor",
                    "Prioridade",
                    "Status",
                    "Data de abertura",
                    "Data de conclusão"
                ])

                for ocorrencia in dados["ocorrencias"]:

                    escritor.writerow([
                        ocorrencia["id"],
                        ocorrencia["categoria"],
                        ocorrencia["setor"],
                        ocorrencia["prioridade"],
                        ocorrencia["status"],
                        ocorrencia["data_abertura"],
                        ocorrencia["data_conclusao"] or ""
                    ])

            messagebox.showinfo(
                "Exportação concluída",
                f"Relatório de desempenho exportado com sucesso!\n\n"
                f"Arquivo salvo em:\n{caminho}"
            )

        except (sqlite3.Error, OSError, csv.Error, ValueError) as erro:

            messagebox.showerror(
                "Erro na exportação",
                f"Não foi possível exportar o desempenho.\n\n{erro}"
            )



    def mostrar_sobre(self):

        self.limpar_conteudo()

        self.criar_titulo(
            "Sobre o HotelFlow",
            "Conheça a finalidade e os objetivos do sistema."
        )

        painel = tk.Frame(
            self.area_conteudo,
            bg=COR_BRANCO,
            padx=30,
            pady=30
        )

        painel.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )

        tk.Label(
            painel,
            text="HotelFlow",
            bg=COR_BRANCO,
            fg=COR_AZUL,
            font=("Arial", 24, "bold")
        ).pack(anchor="w", pady=(0, 15))

        texto = (
            "O HotelFlow é um sistema desktop desenvolvido para "
            "auxiliar no gerenciamento de ocorrências e solicitações "
            "em estabelecimentos hoteleiros.\n\n"
            "A aplicação permite registrar solicitações, associar "
            "ocorrências a quartos e hóspedes, definir setores "
            "responsáveis, estabelecer prioridades e acompanhar "
            "o andamento dos atendimentos.\n\n"
            "O sistema também oferece recursos de relatórios "
            "gerenciais e análise de desempenho, permitindo "
            "acompanhar os resultados dos setores e os tempos "
            "de resolução das ocorrências.\n\n"
            "O sistema utiliza Python para a lógica da aplicação, "
            "Tkinter para a interface gráfica e SQLite para o "
            "armazenamento dos dados.\n\n"
        )

        tk.Label(
            painel,
            text=texto,
            bg=COR_BRANCO,
            fg=COR_TEXTO,
            font=("Arial", 11),
            justify="left",
            wraplength=750
        ).pack(anchor="w")



if __name__ == "__main__":

    try:

        database.criar_banco()

        janela = tk.Tk()
        aplicativo = HotelFlow(janela)

        janela.mainloop()

    except sqlite3.Error as erro:

        messagebox.showerror(
            "Erro ao iniciar",
            f"Não foi possível iniciar o banco de dados.\n\n{erro}"
        )

