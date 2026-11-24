# Spec Delta: Integração com IA (Google Gemini) no Modo Prova

## Purpose
Adicionar capacidades de inteligência artificial generativa via Google Gemini ao Modo Prova do EduTrack AI, viabilizando a geração de questões adaptativas contextualizadas, cronogramas de estudo inteligentes, resumos teóricos estruturados, flashcards e revisões focadas na véspera (D-1), com garantia de operação resiliente através de fallback heurístico local.

## ADDED Requirements

### Requirement: Gemini API Configuration and Credential Management
O sistema DEVE / SHALL gerenciar a credencial de autenticação da API do Google Gemini de forma centralizada e segura, verificando em primeiro lugar os segredos do Streamlit (`st.secrets["GEMINI_API_KEY"]`), seguido por variáveis de ambiente (`os.environ["GEMINI_API_KEY"]`) e arquivos de ambiente locais (`.env`), sem expor o valor da chave em logs, prints ou na interface do usuário.

#### Scenario: Chave de API configurada com sucesso
- **WHEN** a chave `GEMINI_API_KEY` estiver definida em `st.secrets` ou nas variáveis de ambiente com formato válido
- **THEN** o sistema inicializa o cliente da API Gemini no modelo `gemini-1.5-flash` ou compatível e reporta status ativo para os módulos dependentes

#### Scenario: Chave de API ausente ou inválida
- **WHEN** nenhuma chave `GEMINI_API_KEY` for localizada no ambiente de execução
- **THEN** o sistema opera silenciosamente em modo de degradação graciosa (fallback heurístico), indicando na interface de usuário que a IA generativa está inativa e orientando onde configurar a credencial

---

### Requirement: AI-Generated Adaptive Mock Exam Questions
O sistema DEVE / SHALL permitir a geração de questões de múltipla escolha e simulados adaptativos a partir do conteúdo programático da avaliação, utilizando prompts estruturados que demandem retornos estritamente em JSON contendo enunciado, quatro opções de resposta, índice da resposta correta, explicação didática detalhada e indicação de fonte.

#### Scenario: Geração bem-sucedida de simulado via IA
- **WHEN** o estudante cadastra ou solicita a regeneração de questões de uma prova com conteúdo programático válido e a API do Gemini estiver habilitada
- **THEN** o sistema envia o conteúdo textual ao modelo Gemini, recebe um conjunto de 3 ou mais questões estruturadas em JSON, valida a integridade do esquema e as adiciona ao banco de questões com status `"approved"`

#### Scenario: Falha ou timeout na API Gemini durante geração de questões
- **WHEN** a chamada à API Gemini falhar por problemas de conectividade, rate limit ou erro de parsing do JSON retornado
- **THEN** o sistema captura a exceção defensivamente, aciona a geração heurística padrão e preserva o fluxo do usuário sem interrupção ou travamento da aplicação

---

### Requirement: AI-Powered Dynamic Study Plan and Schedule
O sistema DEVE / SHALL gerar cronogramas de revisão diários personalizados por IA, considerando o total de dias restantes até a prova, o nível de domínio dos tópicos identificados e metodologias pedagógicas de estudo ativo.

#### Scenario: Geração de plano diário com mais de 3 dias de antecedência
- **WHEN** uma avaliação com data superior a 3 dias é analisada pelo gerador de cronograma via IA
- **THEN** o sistema gera uma sequência diária com foco distribuído, alocando prioritariamente os tópicos críticos nos primeiros dias, sessões de prática ativa no meio e revisão de consolidação nos dias finais

#### Scenario: Plano para prova iminente (1 a 2 dias)
- **WHEN** a data da prova estiver a menos de 48 horas da data atual
- **THEN** o cronograma foca unicamente em revisão de alta densidade, resolução de questões prioritárias e descanso cognitivo pré-exame

---

### Requirement: AI-Generated Summary and Flashcards
O sistema DEVE / SHALL possibilitar a extração de resumos executivos em tópicos e flashcards conceituais (pergunta/resposta) baseados no material ou ementa fornecidos pelo aluno.

#### Scenario: Extração de síntese conceitual
- **WHEN** o aluno solicita um resumo da matéria na aba de preparação
- **THEN** o sistema sintetiza os conceitos vitais em bullet points com definições claras, termos técnicos e aplicações práticas

#### Scenario: Geração de flashcards para repetição ativa
- **WHEN** o aluno acessa a área de cartões de memorização
- **THEN** o sistema gera pares conceituais de pergunta e resposta focados em fixação rápida e retenção de longo prazo

---

### Requirement: AI-Driven Emergency D-1 Revision
O sistema DEVE / SHALL produzir um relatório emergencial condensado para o dia anterior à prova (D-1), focalizando estritamente nos tópicos onde o estudante obteve domínio inferior a 60%, destacando conceitos críticos, fórmulas fundamentais e dicas rápidas de memorização.

#### Scenario: Aluno com tópicos de baixo domínio na véspera
- **WHEN** o aluno acessa a aba "⚡ Revisão D-1" e possui tópicos com taxa de acerto inferior a 60%
- **THEN** a IA recebe a lista de tópicos vulneráveis e formula um dossiê ultra-sintético destacando apenas o que é essencial revisar para não errar na prova

#### Scenario: Aluno com alto domínio em todos os tópicos
- **WHEN** todos os tópicos avaliados apresentarem domínio superior a 60%
- **THEN** a IA gera uma revisão de confiança e consolidação com checklist de calma e revisão geral dos conceitos mestres

## MODIFIED Requirements

### Requirement: Exam Configuration and Assessment Profile
O fluxo de criação e visualização da prova no Modo Prova DEVE integrar a opção de acionamento do motor de IA Gemini, mantendo o fallback transparente caso a API não esteja conectada.
