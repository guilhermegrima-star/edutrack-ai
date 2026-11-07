# Tarefas de Implementação: Geração de Relatório PDF e Endpoint de Download

## Fase 1: Definições de Dados e Dependências
- [x] Adicionar dependência `reportlab` no arquivo `edutrack-ai/requirements.txt`
- [x] Criar schema da tabela de persistência de relatórios em `edutrack-ai/tables/student_reports.xs`

## Fase 2: Backend Xano (XanoScript)
- [x] Implementar endpoint de upload `POST /student/report` em `edutrack-ai/apis/edutrack_ai/student_report_POST.xs` vinculando obrigatoriamente `user_id = $auth.id`
- [x] Implementar endpoint de download/consulta `GET /student/report` em `edutrack-ai/apis/edutrack_ai/student_report_GET.xs` com filtro de isolamento `$db.student_reports.user_id == $auth.id`
- [x] Validar e garantir a integridade dos cabeçalhos HTTP para download de anexo (`Content-Type: application/pdf`)

## Fase 3: Script Python de Geração de PDF (`scripts/generate_report.py`)
- [x] Estruturar a classe `NumberedCanvas` e gerador de PDF utilizando `reportlab.platypus` (SimpleDocTemplate, Paragraph, Table, Spacer)
- [x] Integrar com cliente HTTP para obter dados de `GET /auth/me`, `GET /subjects` e `GET /academic_tasks`
- [x] Implementar o cálculo dos indicadores globais e por matéria (reaproveitando a lógica de `calculate_progress.py`)
- [x] Implementar o layout visual:
  - [x] Cabeçalho institucional com título e carimbo de data/hora
  - [x] Bloco de dados cadastrais do aluno
  - [x] Cartões de métricas (KPIs de progresso geral)
  - [x] Tabela estilizada de disciplinas com carga horária, tarefas e percentual de progresso
  - [x] Lista/resumo de pendências
  - [x] Rodapé com hash SHA-256 e numeração de páginas ("Página X de Y")
- [x] Implementar interface de linha de comando CLI (`--token`, `--output`, `--upload`) e saída padrão em JSON

## Fase 4: Integração na Interface Streamlit
- [x] Adicionar componente/botão de ação "📊 Compilar Relatório PDF" na página de Perfil (`pages/3_🔒_Perfil.py`)
- [x] Adicionar componente de geração e download de relatório PDF na aba de Alunos (`app.py`)
- [x] Integrar a chamada do gerador e disponibilizar botão de download `st.download_button`

## Fase 5: Testes e Validação
- [x] Validar sintaxe dos arquivos Python (`scripts/generate_report.py` e `pages/3_🔒_Perfil.py`)
- [x] Validar conformidade das regras XanoScript nos arquivos `.xs`
