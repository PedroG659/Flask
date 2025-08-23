# db.py
import sqlite3

# Função para conectar ao banco de dados.
# Se o arquivo do banco de dados não existir, ele será criado.
def get_db_connection():
    conn = sqlite3.connect('sorteio.db')
    conn.row_factory = sqlite3.Row  # Isso permite acessar colunas por nome
    return conn

# Função para inicializar o banco de dados e criar as tabelas necessárias.
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS turmas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            turma_id INTEGER NOT NULL,
            FOREIGN KEY (turma_id) REFERENCES turmas(id)
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sorteios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarefa_id INTEGER NOT NULL,
            aluno_id INTEGER NOT NULL,
            turma_id INTEGER NOT NULL,
            data_sorteio TEXT NOT NULL,
            FOREIGN KEY (tarefa_id) REFERENCES tarefas(id),
            FOREIGN KEY (aluno_id) REFERENCES alunos(id),
            FOREIGN KEY (turma_id) REFERENCES turmas(id)
        );
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Banco de dados 'sorteio.db' inicializado com sucesso.")
