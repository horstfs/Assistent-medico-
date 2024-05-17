# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, g, session, jsonify
import mysql.connector
from mysql.connector.errors import IntegrityError
import json
from functools import wraps  # Para criar decoradores
from datetime import date, datetime  # Para trabalhar com datas
from datetime import datetime, timedelta


# Configuração do banco de dados MySQL
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'sistemamedico'
}

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Necessário para usar flash messages


# Função para obter a conexão com o banco de dados
def get_db_connection():
    if 'db' not in g:
        g.db = mysql.connector.connect(**db_config)  # Conecta ao banco de dados
    return g.db

# Função para fechar a conexão com o banco de dados ao sair do contexto
@app.teardown_appcontext
def close_db_connection(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Rota para a página inicial
# Configurações do banco de dados
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = '0visit'

def inserir_visita(site, endereco_ip):
    try:
        # Conectar ao banco de dados
        conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
        cursor = conn.cursor()

        # Verificar se já existe uma visita registrada para este IP e site nas últimas 30 minutos
        query = "SELECT * FROM Visitas WHERE site = %s AND endereco_ip = %s AND data_hora >= %s"
        threshold_time = datetime.now() - timedelta(minutes=30)
        cursor.execute(query, (site, endereco_ip, threshold_time))
        result = cursor.fetchone()

        if not result:
            # Se não houver visita registrada nas últimas 30 minutos, inserir uma nova entrada
            query = "INSERT INTO Visitas (site, endereco_ip) VALUES (%s, %s)"
            cursor.execute(query, (site, endereco_ip))
            conn.commit()

        # Fechar a conexão com o banco de dados
        cursor.close()
        conn.close()
    except Exception as e:
        print("Erro ao inserir visita:", e)

@app.route('/')
def index():
    site = 'Medico'  # Substitua pelo nome do seu site
    endereco_ip = request.remote_addr
    inserir_visita(site, endereco_ip)
    return render_template('index.html')

# Rota para cadastrar um novo paciente
@app.route("/cadastrar_paciente", methods=["GET", "POST"])
def cadastrar_paciente():
    if request.method == "POST":
        # Coleta os dados do formulário
        nome = request.form.get("nome")
        cpf = request.form.get("cpf")
        tipo_sanguíneo = request.form.get("tipo_sanguíneo")
        data_nascimento = request.form.get("data_nascimento")
        endereco = request.form.get("endereco")
        telefone = request.form.get("telefone")
        email = request.form.get("email")

        # Insere o paciente no banco de dados
        db = get_db_connection()
        cursor = db.cursor()
        query = "INSERT INTO Pacientes (nome, cpf, tipo_sanguíneo, data_nascimento, endereco, telefone, email) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        
        try:
            cursor.execute(query, (nome, cpf, tipo_sanguíneo, data_nascimento, endereco, telefone, email))
            db.commit()
            flash("Paciente cadastrado com sucesso!")
        except IntegrityError:
            flash("CPF já cadastrado. Use outro CPF.")
        finally:
            cursor.close()
            db.close()

        return redirect(url_for("index"))

    return render_template("cadastrar_paciente.html")

# Rota para pesquisar pacientes por CPF
@app.route("/pesquisar_paciente", methods=["GET", "POST"])
def pesquisar_paciente():
    if request.method == "POST":
        cpf = request.form.get("cpf")

        # Busca o paciente pelo CPF
        db = get_db_connection()
        cursor = db.cursor()
        query = "SELECT id, nome FROM Pacientes WHERE cpf = %s"
        cursor.execute(query, (cpf,))
        paciente = cursor.fetchone()
        cursor.close()
        db.close()

        if paciente:
            return redirect(url_for("paciente", paciente_id=paciente[0]))
        else:
            flash("Paciente não encontrado.")
    
    return render_template("pesquisar_paciente.html")

# Exemplo de rota para detalhes do paciente
@app.route("/paciente/<int:paciente_id>")
def paciente(paciente_id):
    db = get_db_connection()
    cursor = db.cursor()
    query = "SELECT nome, cpf, tipo_sanguíneo, data_nascimento, endereco, telefone, email, id FROM Pacientes WHERE id = %s"  # Inclua todos os campos necessários
    cursor.execute(query, (paciente_id,))
    resultado = cursor.fetchone()  # Certifique-se de que este resultado contém todas as colunas necessárias
    cursor.close()
    db.close()

    if resultado:
        # Verifique se está tentando acessar um índice que não existe
        return render_template("paciente.html", paciente=resultado)  # Verifique se está acessando índices válidos
    else:
        flash("Paciente não encontrado.")
        return redirect(url_for("pesquisar_paciente"))


    
# Rota para inserir um hemograma para um paciente
@app.route("/paciente/<int:paciente_id>/cadastrar_hemograma", methods=["GET", "POST"])
def cadastrar_hemograma(paciente_id):
    if request.method == "POST":
        data = request.form.get("data")
        hemoglobina = request.form.get("hemoglobina")
        hematocrito = request.form.get("hematocrito")
        eritrócitos = request.form.get("eritrócitos")
        leucócitos = request.form.get("leucócitos")
        plaquetas = request.form.get("plaquetas")

        db = get_db_connection()
        cursor = db.cursor()
        query = "INSERT INTO Hemogramas (paciente_id, data, hemoglobina, hematocrito, eritrócitos, leucócitos, plaquetas) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (paciente_id, data, hemoglobina, hematocrito, eritrócitos, leucócitos, plaquetas))
        db.commit()
        cursor.close()
        db.close()

        flash("Hemograma inserido com sucesso!")
        return redirect(url_for("paciente", paciente_id=paciente_id))

    return render_template("cadastrar_hemograma.html", paciente_id=paciente_id)

# Rota para inserir um exame de urina para um paciente
@app.route("/paciente/<int:paciente_id>/cadastrar_exame_urina", methods=["GET", "POST"])
def cadastrar_exame_urina(paciente_id):
    if request.method == "POST":
        data = request.form.get("data")
        densidade = request.form.get("densidade")
        ph = request.form.get("ph")
        proteina = request.form.get("proteina")
        glicose = request.form.get("glicose")
        cetonas = request.form.get("cetonas")
        hemoglobina = request.form.get("hemoglobina")
        leucócitos = request.form.get("leucócitos")

        db = get_db_connection()
        cursor = db.cursor()
        query = "INSERT INTO Exames_Urina (paciente_id, data, densidade, ph, proteina, glicose, cetonas, hemoglobina, leucócitos) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (paciente_id, data, densidade, ph, proteina, glicose, cetonas, hemoglobina, leucócitos))
        db.commit()
        cursor.close()
        db.close()

        flash("Exame de urina inserido com sucesso!")
        return redirect(url_for("paciente", paciente_id=paciente_id))

    return render_template("cadastrar_exame_urina.html", paciente_id=paciente_id)

# Rota para inserir um histórico de peso para um paciente
@app.route("/paciente/<int:paciente_id>/cadastrar_historico_peso", methods=["GET", "POST"])
def cadastrar_historico_peso(paciente_id):
    if request.method == "POST":
        data = request.form.get("data")
        peso = request.form.get("peso")

        db = get_db_connection()
        cursor = db.cursor()
        query = "INSERT INTO Historico_Peso (paciente_id, data, peso) VALUES (%s, %s, %s)"
        cursor.execute(query, (paciente_id, data, peso))
        db.commit()
        cursor.close()
        db.close()

        flash("Peso inserido com sucesso!")
        return redirect(url_for("paciente", paciente_id=paciente_id))

    return render_template("cadastrar_historico_peso.html", paciente_id=paciente_id)





# Rota para comparar hemogramas
@app.route("/paciente/<int:paciente_id>/comparar_hemograma")
def comparar_hemograma(paciente_id):
    db = get_db_connection()
    cursor = db.cursor()

    # Obter informações do paciente
    paciente_query = "SELECT nome, cpf, tipo_sanguíneo FROM Pacientes WHERE id = %s"
    cursor.execute(paciente_query, (paciente_id,))
    paciente = cursor.fetchone()  # Obter informações do paciente
    
    if not paciente:
        flash("Paciente não encontrado.")
        return redirect(url_for("index"))

    # Obter dados de hemogramas
    hemograma_query = "SELECT data, hemoglobina, hematocrito, eritrócitos, leucócitos, plaquetas FROM Hemogramas WHERE paciente_id = %s ORDER BY data ASC"
    cursor.execute(hemograma_query, (paciente_id,))
    resultados = cursor.fetchall()
    cursor.close()
    db.close()

    # Converta as datas para strings antes de serializar em JSON
    datas = [d[0].isoformat() for d in resultados]  # Converte para formato "YYYY-MM-DD"
    hemoglobina = [d[1] for d in resultados]
    hematocrito = [d[2] for d in resultados]
    eritrócitos = [d[3] for d in resultados]
    leucócitos = [d[4] for d in resultados]
    plaquetas = [d[5] for d in resultados]

    return render_template("comparar_hemograma.html", paciente=paciente, datas=json.dumps(datas), hemoglobina=json.dumps(hemoglobina), hematocrito=json.dumps(hematocrito), eritrócitos=json.dumps(eritrócitos), leucócitos=json.dumps(leucócitos), plaquetas=json.dumps(plaquetas))
# Rota para comparar exames de urina


@app.route("/paciente/<int:paciente_id>/comparar_exame_urina")
def comparar_exame_urina(paciente_id):
    db = get_db_connection()
    cursor = db.cursor()

    # Obter informações do paciente
    paciente_query = "SELECT nome, cpf, tipo_sanguíneo FROM Pacientes WHERE id = %s"  # Confirme os nomes das colunas
    cursor.execute(paciente_query, (paciente_id,))
    paciente = cursor.fetchone() 
    
    if not paciente:
        flash("Paciente não encontrado.")
        return redirect(url_for("index"))

    # Obter dados dos exames de urina
    urina_query = "SELECT data, densidade, ph, proteina, glicose, cetonas, hemoglobina, leucócitos FROM Exames_Urina WHERE paciente_id = %s ORDER BY data ASC"
    cursor.execute(urina_query, (paciente_id,))
    resultados = cursor.fetchall()
    cursor.close()
    db.close()
    

    # Converta as datas para strings antes de serializar em JSON
    datas = [d[0].isoformat() for d in resultados]
    densidade = [d[1] for d in resultados]
    ph = [d[2] for d in resultados]
    proteina = [d[3] for d in resultados]
    glicose = [d[4] for d in resultados]
    cetonas = [d[5] for d in resultados]
    hemoglobina = [d[6] for d in resultados]
    leucócitos = [d[7] for d in resultados]

    return render_template("comparar_exame_urina.html", paciente=paciente, datas=json.dumps(datas), densidade=json.dumps(densidade), ph=json.dumps(ph), proteina=json.dumps(proteina), glicose=json.dumps(glicose), cetonas=json.dumps(cetonas), hemoglobina=json.dumps(hemoglobina), leucócitos=json.dumps(leucócitos))




@app.route("/paciente/<int:paciente_id>/comparar_historico_peso")
def comparar_historico_peso(paciente_id):
    db = get_db_connection()
    cursor = db.cursor()

    # Obter informações do paciente
    paciente_query = "SELECT nome, cpf, tipo_sanguíneo FROM Pacientes WHERE id = %s"  # Certifique-se de usar o nome correto das colunas
    cursor.execute(paciente_query, (paciente_id,))
    paciente = cursor.fetchone()  # Selecione corretamente as colunas disponíveis
    
    if not paciente:
        flash("Paciente não encontrado.")
        return redirect(url_for("index"))

    # Obter dados do histórico de peso
    peso_query = "SELECT data, peso FROM Historico_Peso WHERE paciente_id = %s ORDER BY data ASC"
    cursor.execute(peso_query, (paciente_id,))
    resultados = cursor.fetchall()  # Obter todos os registros do histórico de peso
    cursor.close()
    db.close()

    # Converta as datas para strings antes de serializar em JSON
    datas = [d[0].isoformat() for d in resultados]  # Converte para formato "YYYY-MM-DD"
    peso = [d[1] for d in resultados]

    return render_template("comparar_historico_peso.html", paciente=paciente, datas=json.dumps(datas), peso=json.dumps(peso))




@app.route("/paciente/<int:paciente_id>/grafico_dispersao")
def grafico_dispersao(paciente_id):
    db = get_db_connection()
    cursor = db.cursor()

    # Obter informações do paciente, incluindo a data de nascimento para calcular a idade
    paciente_query = "SELECT data_nascimento FROM Pacientes WHERE id = %s"  # Corrija para usar a coluna correta
    cursor.execute(paciente_query, (paciente_id,))
    data_nascimento = cursor.fetchone()  # Obter a data de nascimento

    if not data_nascimento:
        flash("Data de nascimento não encontrada.")
        return redirect(url_for("paciente", paciente_id=paciente_id))
    
    # Obter dados de histórico de peso para criar o gráfico de dispersão
    peso_query = "SELECT data, peso FROM Historico_Peso WHERE paciente_id = %s ORDER BY data ASC"
    cursor.execute(peso_query, (paciente_id,))
    resultados = cursor.fetchall()  # Obter os registros do histórico de peso
    cursor.close()
    db.close()

    # Calcular a idade a partir da data de nascimento e converter para formato serializável
    data_nascimento = data_nascimento[0]
    idades = [(date.today().year - data_nascimento.year) for d in resultados]
    pesos = [d[1] for d in resultados]

    scatter_data = [{"x": idades[i], "y": pesos[i]} for i in range(len(idades))]  # Criar dados para o gráfico de dispersão

    return render_template("grafico_dispersao.html", paciente_id=paciente_id, scatter_data=json.dumps(scatter_data))




@app.route("/paciente/<int:paciente_id>/grafico_radar")
def grafico_radar(paciente_id):
    db = get_db_connection()
    cursor = db.cursor()

    # Obter dados do hemograma para o gráfico de radar
    query = "SELECT hemoglobina, hematocrito, eritrócitos, leucócitos, plaquetas FROM Hemogramas WHERE paciente_id = %s ORDER BY data ASC"
    cursor.execute(query, (paciente_id,))
    resultados = cursor.fetchall()
    cursor.close()
    db.close()

    # Se não houver dados, informar o usuário
    if not resultados:
        flash("Nenhum dado de hemograma encontrado para o paciente.")
        return redirect(url_for("paciente", paciente_id=paciente_id))

    # Calcular a média dos valores para visualizar o perfil médico
    hemoglobina = sum([d[0] for d in resultados]) / len(resultados)
    hematocrito = sum([d[1] for d in resultados]) / len(resultados)
    eritrócitos = sum([d[2] for d in resultados]) / len(resultados)
    leucócitos = sum([d[3] for d in resultados]) / len(resultados)
    plaquetas = sum([d[4] for d in resultados]) / len(resultados)

    radar_data = [hemoglobina, hematocrito, eritrócitos, leucócitos, plaquetas]  # Dados para o gráfico de radar

    return render_template("grafico_radar.html", paciente=paciente_id, radar_data=json.dumps(radar_data))



@app.route("/paciente/<int:paciente_id>/grafico_boxplot")
def grafico_boxplot(paciente_id):
    db = get_db_connection()
    cursor = db.cursor()

    # Obter dados do hemograma para o boxplot
    query = "SELECT leucócitos FROM Hemogramas WHERE paciente_id = %s ORDER BY data ASC"
    cursor.execute(query, (paciente_id,))
    resultados = cursor.fetchall()  # Obter todos os registros para o paciente
    cursor.close()
    db.close()

    # Verificar se há dados suficientes para o gráfico
    if not resultados:
        flash("Nenhum dado disponível para o gráfico de boxplot.")
        return redirect(url_for("paciente", paciente_id=paciente_id))

    # Converta os resultados para um formato apropriado para o Chart.js
    boxplot_data = [{"y": d[0]} for d in resultados]

    return render_template("grafico_boxplot.html", paciente_id=paciente_id, boxplot_data=json.dumps(boxplot_data))






@app.route("/obter_colunas", methods=["GET"])
def obter_colunas():
    # Lista de tabelas de interesse
    tabelas = ["Pacientes", "Hemogramas", "Exames_Urina", "Historico_Peso"]
    colunas_por_tabela = {}

    db = get_db_connection()
    cursor = db.cursor()

    # Obter colunas de cada tabela
    for tabela in tabelas:
        query = f"SHOW COLUMNS FROM {tabela}"
        cursor.execute(query)
        colunas = [col[0] for col in cursor.fetchall()]
        colunas_por_tabela[tabela] = colunas

    cursor.close()
    db.close()

    return jsonify(colunas_por_tabela)


# Rota para página de comparação de variáveis
@app.route("/comparar_variaveis", methods=["GET", "POST"])
def comparar_variaveis():
    if request.method == "POST":
        variavel1 = request.form.get("variavel1")
        variavel2 = request.form.get("variavel2")

        db = get_db_connection()
        cursor = db.cursor()

        query = f"SELECT {variavel1}, {variavel2} FROM Pacientes"
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()
        db.close()

        data1 = [d[0] for d in resultados]
        data2 = [d[1] for d in resultados]

        return render_template("comparar_rresultado.html", data1=json.dumps(data1), data2=json.dumps(data2))

    return render_template("comparar_variaveis.html")


@app.route("/resultado_comparacao", methods=["POST"])
def resultado_comparacao():
    tabela1 = request.form.get("tabela1")
    coluna1 = request.form.get("coluna1")
    tabela2 = request.form.get("tabela2")
    coluna2 = request.form.get("coluna2")

    db = get_db_connection()
    cursor = db.cursor()

    # Obter os valores das colunas selecionadas para comparação
    query1 = f"SELECT {coluna1} FROM {tabela1}"
    cursor.execute(query1)
    valores1 = [d[0] for d in cursor.fetchall()]

    query2 = f"SELECT {coluna2} FROM {tabela2}"
    cursor.execute(query2)
    valores2 = [d[0] for d in cursor.fetchall()]

    cursor.close()
    db.close()

    # Tratar diferentes tipos de dados
    # Se coluna1 for data de nascimento, converta para idade
    if coluna1 == "data_nascimento":
        valores1 = [(datetime.today().year - v.year) if isinstance(v, (date, datetime)) else v for v in valores1]

    # Se coluna2 for data de nascimento, converta para idade
    if coluna2 == "data_nascimento":
        valores2 = [(datetime.today().year - v.year) if isinstance(v, (date, datetime)) else v for v in valores2]

    # Se o comprimento dos conjuntos de dados for diferente, avise o usuário
    if len(valores1) != len(valores2):
        flash("As colunas selecionadas têm tamanhos diferentes. Verifique se as seleções estão corretas.")
        return redirect(url_for("comparar_variaveis"))

    # Verifique se os valores são do tipo correto para comparação (por exemplo, números para gráficos de dispersão)
    if not all(isinstance(v, (int, float)) for v in valores1) or not all(isinstance(v, (int, float)) for v in valores2):
        flash("As colunas selecionadas não são do tipo correto para comparação. Por favor, escolha colunas que possam ser comparadas.")
        return redirect(url_for("comparar_variaveis"))

    return render_template("resultado_comparacao.html", valores1=json.dumps(valores1), valores2=json.dumps(valores2))



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)