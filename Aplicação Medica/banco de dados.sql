-- Criação do banco de dados
CREATE DATABASE IF NOT EXISTS SistemaMedico;
USE SistemaMedico;

-- Criação da tabela de pacientes
CREATE TABLE Pacientes (
  id INT PRIMARY KEY AUTO_INCREMENT,  -- Identificador único interno do paciente
  nome VARCHAR(100) NOT NULL,  -- Nome do paciente
  cpf VARCHAR(11) UNIQUE NOT NULL,  -- CPF do paciente, chave única
  tipo_sanguíneo VARCHAR(3),  -- Tipo sanguíneo do paciente
  data_nascimento DATE,  -- Data de nascimento do paciente
  endereco VARCHAR(255),  -- Endereço do paciente
  telefone VARCHAR(20),  -- Telefone do paciente
  email VARCHAR(100)  -- E-mail do paciente
);

-- Criação do índice para CPF na tabela de pacientes para otimizar a busca
CREATE INDEX idx_paciente_cpf ON Pacientes(cpf);

-- Criação da tabela de hemogramas
CREATE TABLE Hemogramas (
  id INT PRIMARY KEY AUTO_INCREMENT,  -- Identificador único do hemograma
  paciente_id INT NOT NULL,  -- Relacionamento com a tabela Pacientes
  data DATE NOT NULL,  -- Data do exame
  hemoglobina FLOAT,  -- Valor de hemoglobina
  hematocrito FLOAT,  -- Valor de hematócrito
  eritrócitos INT,  -- Contagem de eritrócitos
  leucócitos INT,  -- Contagem de leucócitos
  plaquetas INT,  -- Contagem de plaquetas
  FOREIGN KEY (paciente_id) REFERENCES Pacientes(id) ON DELETE CASCADE  -- Chave estrangeira para a tabela Pacientes
);

-- Criação da tabela de exames de urina
CREATE TABLE Exames_Urina (
  id INT PRIMARY KEY AUTO_INCREMENT,  -- Identificador único do exame de urina
  paciente_id INT NOT NULL,  -- Relacionamento com a tabela Pacientes
  data DATE NOT NULL,  -- Data do exame
  densidade FLOAT,  -- Densidade da urina
  ph FLOAT,  -- pH da urina
  proteina FLOAT,  -- Proteína na urina
  glicose FLOAT,  -- Glicose na urina
  cetonas FLOAT,  -- Cetonas na urina
  hemoglobina FLOAT,  -- Hemoglobina na urina
  leucócitos FLOAT,  -- Leucócitos na urina
  FOREIGN KEY (paciente_id) REFERENCES Pacientes(id) ON DELETE CASCADE  -- Chave estrangeira para a tabela Pacientes
);

-- Criação da tabela para histórico de peso
CREATE TABLE Historico_Peso (
  id INT PRIMARY KEY AUTO_INCREMENT,  -- Identificador único do registro de peso
  paciente_id INT NOT NULL,  -- Relacionamento com a tabela Pacientes
  data DATE NOT NULL,  -- Data do registro do peso
  peso FLOAT,  -- Peso do paciente
  FOREIGN KEY (paciente_id) REFERENCES Pacientes(id) ON DELETE CASCADE  -- Chave estrangeira para a tabela Pacientes
);

-- Índices adicionais para melhorar o desempenho das consultas
CREATE INDEX idx_hemogramas_paciente ON Hemogramas(paciente_id);  -- Índice para buscas por paciente
CREATE INDEX idx_exames_urina_paciente ON Exames_Urina(paciente_id);  -- Índice para buscas por paciente
CREATE INDEX idx_historico_peso_paciente ON Historico_Peso(paciente_id);  -- Índice para buscas por paciente
