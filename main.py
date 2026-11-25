
"""
HOTELFLOW
Sistema de gerenciamento de ocorrências e solicitações hoteleiras.

Arquivo principal responsável pela inicialização do sistema.
"""
import tkinter as tk
import database
import interface


def iniciar_sistema():
    try:

        database.criar_banco()

        janela = tk.Tk()

        interface.HotelFlow(janela)

        janela.mainloop()

    except Exception as erro:
        print("Ocorreu um erro ao iniciar o HotelFlow:")
        print(erro)


if __name__ == "__main__":
    iniciar_sistema()
