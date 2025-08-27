# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import random
from datetime import datetime
from db import get_db_connection, init_db

# Inicializa o banco de dados ao iniciar a aplicação.
init_db()

app = Flask(__name__)

# Rota principal para exibir a página e os dados.
@app.route('/')
def index():
    conn = get_db_connection()
    
    # Busca todos os dados para exibição inicial
    turmas = conn.execute('SELECT * FROM turmas').fetchall()
    tarefas = conn.execute('SELECT * FROM tarefas').fetchall()
    alunos = conn.execute('SELECT * FROM alunos').fetchall()
    
    # Busca os sorteios realizados com os nomes correspondentes.
    sorteios = conn.execute('''
        SELECT
            sorteios.data_sorteio,
            turmas.nome AS turma_nome,
            alunos.nome AS aluno_nome,
            tarefas.nome AS tarefa_nome
        FROM sorteios
        JOIN turmas ON sorteios.turma_id = turmas.id
        JOIN alunos ON sorteios.aluno_id = alunos.id
        JOIN tarefas ON sorteios.tarefa_id = tarefas.id
        ORDER BY sorteios.data_sorteio DESC
        LIMIT 10
    ''').fetchall()
    
    conn.close()
    
    # Renderiza a página principal, passando todos os dados.
    return render_template('index.html', turmas=turmas, tarefas=tarefas, alunos=alunos, sorteios=sorteios)

# Rota para adicionar uma nova turma.
@app.route('/adicionar_turma', methods=['POST'])
def adicionar_turma():
    if request.method == 'POST':
        turma_nome = request.form['nome_turma']
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO turmas (nome) VALUES (?)', (turma_nome,))
            conn.commit()
        except sqlite3.IntegrityError:
            # Caso o nome da turma já exista, ignora o erro.
            pass
        finally:
            conn.close()
    return redirect(url_for('index'))

# Rota para adicionar um novo aluno.
@app.route('/adicionar_aluno', methods=['POST'])
def adicionar_aluno():
    if request.method == 'POST':
        aluno_nome = request.form['nome_aluno']
        turma_id = request.form['turma_id']
        conn = get_db_connection()
        conn.execute('INSERT INTO alunos (nome, turma_id) VALUES (?, ?)', (aluno_nome, turma_id))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

# Rota para adicionar uma nova tarefa.
@app.route('/adicionar_tarefa', methods=['POST'])
def adicionar_tarefa():
    if request.method == 'POST':
        tarefa_nome = request.form['nome_tarefa']
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO tarefas (nome) VALUES (?)', (tarefa_nome,))
            conn.commit()
        except sqlite3.IntegrityError:
            # Caso o nome da tarefa já exista, ignora o erro.
            pass
        finally:
            conn.close()
    return redirect(url_for('index'))

# Rota para deletar uma turma
@app.route('/deletar_turma/<int:turma_id>', methods=['POST'])
def deletar_turma(turma_id):
    conn = get_db_connection()
    conn.execute('PRAGMA foreign_keys = ON') # Ativa as chaves estrangeiras
    conn.execute('DELETE FROM turmas WHERE id = ?', (turma_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Rota para deletar um aluno
@app.route('/deletar_aluno/<int:aluno_id>', methods=['POST'])
def deletar_aluno(aluno_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM alunos WHERE id = ?', (aluno_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))
    
# Rota para deletar uma tarefa
@app.route('/deletar_tarefa/<int:tarefa_id>', methods=['POST'])
def deletar_tarefa(tarefa_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tarefas WHERE id = ?', (tarefa_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Rota da API para realizar o sorteio (retorna JSON)
@app.route('/api/sortear', methods=['POST'])
def sortear_api():
    data = request.get_json()
    turma_id = data.get('turma_id')
    tarefa_id = data.get('tarefa_id')

    if not turma_id or not tarefa_id:
        return jsonify({'error': 'Turma e Tarefa são obrigatórios.'}), 400

    conn = get_db_connection()
    
    alunos_turma = conn.execute('SELECT * FROM alunos WHERE turma_id = ?', (turma_id,)).fetchall()
    
    if not alunos_turma:
        conn.close()
        return jsonify({'error': 'Nenhum aluno encontrado nesta turma.'}), 404

    # Sorteia um aluno aleatoriamente
    aluno_sorteado = random.choice(alunos_turma)
    
    # Salva o resultado do sorteio
    data_sorteio = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn.execute('INSERT INTO sorteios (tarefa_id, aluno_id, turma_id, data_sorteio) VALUES (?, ?, ?, ?)',
                 (tarefa_id, aluno_sorteado['id'], turma_id, data_sorteio))
    conn.commit()
    
    # Busca os nomes para o retorno
    aluno_nome = conn.execute('SELECT nome FROM alunos WHERE id = ?', (aluno_sorteado['id'],)).fetchone()['nome']
    turma_nome = conn.execute('SELECT nome FROM turmas WHERE id = ?', (turma_id,)).fetchone()['nome']
    tarefa_nome = conn.execute('SELECT nome FROM tarefas WHERE id = ?', (tarefa_id,)).fetchone()['nome']

    conn.close()
    
    # Retorna o resultado em formato JSON
    return jsonify({
        'sucesso': True,
        'aluno_sorteado': aluno_nome,
        'turma': turma_nome,
        'tarefa': tarefa_nome,
        'data': data_sorteio
    })

if __name__ == '__main__':
    app.run(debug=True)
