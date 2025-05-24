import sqlite3
import json
import hashlib

def criar_tabela():
    conexao = sqlite3.connect("cadastro.db")
    cursor = conexao.cursor()

    # Tabela de usuários
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        senha TEXT NOT NULL)''')

    # Tabela de cursos e usuários
    cursor.execute('''CREATE TABLE IF NOT EXISTS cursos_usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario_id INTEGER NOT NULL,
                        curso_id INTEGER NOT NULL,
                        FOREIGN KEY (usuario_id) REFERENCES usuarios(id))''')

    # Tabela de módulos dos cursos
    cursor.execute('''CREATE TABLE IF NOT EXISTS modulos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        curso_id INTEGER NOT NULL,
                        nome TEXT NOT NULL,
                        descricao TEXT,
                        FOREIGN KEY (curso_id) REFERENCES cursos_usuarios(curso_id))''')

    conexao.commit()
    conexao.close()

def gerar_relatorio_estatistico():
    conexao = sqlite3.connect("cadastro.db")
    cursor = conexao.cursor()

    cursor.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT curso_id) FROM cursos_usuarios")
    total_cursos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM cursos_usuarios")
    total_inscricoes = cursor.fetchone()[0]

    print("\n=== Relatório Estatístico ===")
    print(f"Total de usuários cadastrados: {total_usuarios}")
    print(f"Total de cursos cadastrados: {total_cursos}")
    print(f"Total de inscrições de usuários em cursos: {total_inscricoes}")

    conexao.close()

def salvar_em_json():
    conexao = sqlite3.connect("cadastro.db")
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()

    cursor.execute("SELECT * FROM cursos_usuarios")
    cursos_usuarios = cursor.fetchall()

    cursor.execute("SELECT * FROM modulos")
    modulos = cursor.fetchall()

    data = {
        "usuarios": usuarios,
        "cursos_usuarios": cursos_usuarios,
        "modulos": modulos
    }

    with open("dados.json", "w") as arquivo_json:
        json.dump(data, arquivo_json, indent=4)

    conexao.close()
    print("Dados salvos em dados.json")

def cadastrar_usuario():
    nome = input("Nome: ")
    email = input("Email: ")
    senha = input("Senha: ")

    senha_hash = hashlib.sha256(senha.encode()).hexdigest()

    conexao = sqlite3.connect("cadastro.db")
    cursor = conexao.cursor()

    try:
        cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)", (nome, email, senha_hash))
        conexao.commit()
        print("Usuário cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        print("Erro: Email já cadastrado!")
    finally:
        conexao.close()

def listar_usuarios():
    conexao = sqlite3.connect("cadastro.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome, email FROM usuarios")
    usuarios = cursor.fetchall()
    conexao.close()

    if not usuarios:
        print("Nenhum usuário cadastrado ainda.")
    else:
        for usuario in usuarios:
            print(f"ID: {usuario[0]}, Nome: {usuario[1]}, Email: {usuario[2]}")

def atualizar_dados(id_usuario):
    print("\n=== Atualizar Dados ===")
    print("1. Atualizar Nome")
    print("2. Atualizar Email")
    print("3. Atualizar Senha")
    print("4. Voltar")

    escolha = input("O que você deseja atualizar? ")
    conexao = sqlite3.connect("cadastro.db")
    cursor = conexao.cursor()
    if escolha == "1":
        novo_nome = input("Digite seu novo nome: ")
        cursor.execute("UPDATE usuarios SET nome = ? WHERE id = ?", (novo_nome, id_usuario))
        print("Nome atualizado com sucesso!")
    elif escolha == "2":
        novo_email = input("Digite seu novo email: ")
        
        cursor.execute("SELECT id FROM usuarios WHERE email = ? AND id != ?", (novo_email, id_usuario))
        if cursor.fetchone():
            print("Erro: Este email já está sendo usado por outro usuário!")
        else:
            cursor.execute("UPDATE usuarios SET email = ? WHERE id = ?", (novo_email, id_usuario))
            print("Email atualizado com sucesso!")
    elif escolha == "3":
        senha_atual = input("Digite sua senha atual: ")
        senha_atual_hash = hashlib.sha256(senha_atual.encode()).hexdigest()
        cursor.execute("SELECT id FROM usuarios WHERE id = ? AND senha = ?", (id_usuario, senha_atual_hash))
        if cursor.fetchone():
            nova_senha = input("Digite sua nova senha: ")
            confirmacao = input("Confirme sua nova senha: ")
            
            if nova_senha == confirmacao:
                nova_senha_hash = hashlib.sha256(nova_senha.encode()).hexdigest()
                cursor.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (nova_senha_hash, id_usuario))
                print("Senha atualizada com sucesso!")
            else:
                print("Erro: As senhas não coincidem!")
        else:
            print("Erro: Senha atual incorreta!")   
    elif escolha == "4":
        print("Voltando ao menu do usuário...")
    else:
        print("Opção inválida!")
    conexao.commit()
    conexao.close()
    return escolha == "1"

def menu_usuario_logado(id_usuario, nome_usuario):
    while True:
        print(f"\n=== Menu do Usuário: {nome_usuario} ===")
        print("1. Ver meus cursos")
        print("2. Atualizar meus dados")
        print("3. Voltar ao menu principal")
        escolha = input("Digite sua escolha: ")

        if escolha == "1":
            cursos = {
                1: "Introdução à Informática",
                2: "Noções de Programação em Python",
                3: "Segurança de Dados e LGPD"
            }

            conexao = sqlite3.connect("cadastro.db")
            cursor = conexao.cursor()
            cursor.execute("SELECT curso_id FROM cursos_usuarios WHERE usuario_id = ?", (id_usuario,))
            cursos_usuario = cursor.fetchall()
            conexao.close()

            if not cursos_usuario:
                print("Você ainda não está inscrito em nenhum curso.")
            else:
                print("\n=== Seus Cursos ===")
                for curso in cursos_usuario:
                    id_curso = curso[0]
                    print(f"- {cursos.get(id_curso, 'Curso desconhecido')}")
        elif escolha == "2":
            nome_alterado = atualizar_dados(id_usuario)
            
            if nome_alterado:
                conexao = sqlite3.connect("cadastro.db")
                cursor = conexao.cursor()
                cursor.execute("SELECT nome FROM usuarios WHERE id = ?", (id_usuario,))
                nome_usuario = cursor.fetchone()[0]
                conexao.close()
        elif escolha == "3":
            print("Voltando ao menu principal...")
            break
        else:
            print("Opção inválida. Tente novamente.")

def fazer_login():
    email = input("Email: ")
    senha = input("Senha: ")
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()

    conexao = sqlite3.connect("cadastro.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome FROM usuarios WHERE email = ? AND senha = ?", (email, senha_hash))
    usuario = cursor.fetchone()
    conexao.close()

    if usuario:
        print(f"Login realizado com sucesso! Bem-vindo(a), {usuario[1]}!")
        return True, usuario[0], usuario[1]
    else:
        print("Erro: Email ou senha incorretos!")
        return False, None, None

def cadastrar_curso(id_usuario):
    cursos = {
        1: {"nome": "Introdução à Informática", "descrição": "Aprenda o básico sobre computadores, software e internet."},
        2: {"nome": "Noções de Programação em Python", "descrição": "Introdução à programação usando a linguagem Python."},
        3: {"nome": "Segurança de Dados e LGPD", "descrição": "Entenda como proteger dados e cumprir a Lei Geral de Proteção de Dados (LGPD)." }
    }

    for id_curso, curso in cursos.items():
        print(f"{id_curso}. {curso['nome']}")

    escolha = input("\nDigite o número do curso que deseja se inscrever: ")

    if escolha.isdigit():
        escolha = int(escolha)
        if escolha in cursos:
            conexao = sqlite3.connect("cadastro.db")
            cursor = conexao.cursor()

            cursor.execute("SELECT * FROM cursos_usuarios WHERE usuario_id = ? AND curso_id = ?", (id_usuario, escolha))
            if cursor.fetchone():
                print("Você já está inscrito neste curso.")
            else:
                cursor.execute("INSERT INTO cursos_usuarios (usuario_id, curso_id) VALUES (?, ?)", (id_usuario, escolha))
                conexao.commit()
                print(f"Inscrição no curso '{cursos[escolha]['nome']}' realizada com sucesso!")

            conexao.close()
        else:
            print("Opção inválida.")
    else:
        print("Entrada inválida.")

def cadastrar_modulo():
    print("=== Cadastrar Módulo do Curso ===")
    logado, id_usuario, nome_usuario = fazer_login()

    if not logado:
        return

    cursos = {
        1: "Introdução à Informática",
        2: "Noções de Programação em Python",
        3: "Segurança de Dados e LGPD"
    }

    for id_curso, nome_curso in cursos.items():
        print(f"{id_curso}. {nome_curso}")

    escolha_curso = input("\nDigite o número do curso para cadastrar o módulo: ")

    if escolha_curso.isdigit():
        escolha_curso = int(escolha_curso)
        if escolha_curso in cursos:
            nome_modulo = input("Digite o nome do módulo: ")
            descricao_modulo = input("Digite a descrição do módulo (opcional): ")

            conexao = sqlite3.connect("cadastro.db")
            cursor = conexao.cursor()

            cursor.execute("INSERT INTO modulos (curso_id, nome, descricao) VALUES (?, ?, ?)",
                           (escolha_curso, nome_modulo, descricao_modulo))
            conexao.commit()
            conexao.close()

            print(f"Módulo '{nome_modulo}' cadastrado com sucesso no curso '{cursos[escolha_curso]}'.")
        else:
            print("Curso inválido.")
    else:
        print("Entrada inválida.")

def menu():
    print("\n=== Menu de Opções ===")
    print("1. Fazer Cadastro")
    print("2. Fazer Login")
    print("3. Cadastrar Curso")
    print("4. Cadastrar módulos dos Cursos")
    print("5. Relatório Estatístico")
    print("6. Salvar em JSON")
    print("7. Sair")
    return input("Digite sua escolha: ")

def opcao_1():
    cadastrar_usuario()

def opcao_2():
    print("=== Login ===")
    logado, id_usuario, nome_usuario = fazer_login()

    if logado:
        print(f"Você está logado como {nome_usuario} (ID: {id_usuario})")
        menu_usuario_logado(id_usuario, nome_usuario)

def opcao_3():
    print("=== Cadastrar Curso ===")
    logado, id_usuario, nome_usuario = fazer_login()
    if logado:
        cadastrar_curso(id_usuario)

def opcao_4():
    cadastrar_modulo()

def opcao_5():
    gerar_relatorio_estatistico()

def opcao_6():
    salvar_em_json()

def main():
    criar_tabela()

    while True:
        escolha = menu()
        if escolha == "1":
            opcao_1()
        elif escolha == "2":
            opcao_2()
        elif escolha == "3":
            opcao_3()
        elif escolha == "4":
            opcao_4()
        elif escolha == "5":
            opcao_5()
        elif escolha == "6":
            opcao_6()
        elif escolha == "7":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()