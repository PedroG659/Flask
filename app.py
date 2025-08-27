from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import random
from datetime import datetime
from db import get_db_connection, init_db

init_db()

app = Flask(__name__)

@app.route('/')
def index():
    conn = get_db_connection()
    
    turmas = conn.execute('SELECT * FROM turmas').fetchall()
    
    tarefas = conn.execute('SELECT * FROM tarefas').fetchall()
    
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
    ''').fetchall()
    
    conn.close()
    
    return render_template('index.html', turmas=turmas, tarefas=tarefas, sorteios=sorteios)

@app.route('/adicionar_turma', methods=['POST'])
def adicionar_turma():
    if request.method == 'POST':
        turma_nome = request.form['nome_turma']
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO turmas (nome) VALUES (?)', (turma_nome,))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        finally:
            conn.close()
    return redirect(url_for('index'))

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

@app.route('/adicionar_tarefa', methods=['POST'])
def adicionar_tarefa():
    if request.method == 'POST':
        tarefa_nome = request.form['nome_tarefa']
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO tarefas (nome) VALUES (?)', (tarefa_nome,))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        finally:
            conn.close()
    return redirect(url_for('index'))

@app.route('/sortear', methods=['POST'])
def sortear():
    if request.method == 'POST':
        turma_id = request.form['turma_sorteio_id']
        tarefa_id = request.form['tarefa_sorteio_id']
        
        conn = get_db_connection()
        
        alunos = conn.execute('SELECT * FROM alunos WHERE turma_id = ?', (turma_id,)).fetchall()
        
        if alunos:
            aluno_sorteado = random.choice(alunos)
            
            data_sorteio = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            conn.execute('INSERT INTO sorteios (tarefa_id, aluno_id, turma_id, data_sorteio) VALUES (?, ?, ?, ?)',
                         (tarefa_id, aluno_sorteado['id'], turma_id, data_sorteio))
            conn.commit()
            
        conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)