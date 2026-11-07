# Design Técnico: Geração de Relatório de Desempenho em PDF e Download via Xano

## Visão Geral da Arquitetura
A solução é composta por duas camadas complementares integradas:
1. **Camada de Processamento e Renderização (Python Client/Script)**: Coleta dados analíticos do aluno via endpoints REST do Xano, calcula indicadores consolidados de desempenho e constrói o layout em PDF com ReportLab/FPDF2.
2. **Camada de Distribuição e Segurança (Xano Backend)**: Fornece endpoints com controle de acesso (`auth = "user"`) para disponibilização do arquivo para download e upload de novas versões geradas.

```
+-------------------+       1. Token JWT        +-------------------+
|  Interface / CLI  | ------------------------> | API Xano          |
|  (Streamlit /     | <------------------------ | (edutrack.ai)     |
|   generate_pdf)   |       2. Dados Brutos     | - /auth/me        |
+-------------------+       (Subjects + Tasks)  | - /subjects       |
          |                                     | - /academic_tasks |
          | 3. Processamento & Cálculo          +-------------------+
          |    (calculate_progress.py)
          v
+-------------------+
|  Gerador de PDF   |
|  (ReportLab /     |
|   FPDF2)          |
+-------------------+
          |
          | 4. PDF Binário / Arquivo Local
          v
+-------------------+       5. Upload / Registro +-------------------+
| Arquivo PDF Local | -------------------------> | Xano Endpoint     |
| (relatorio_*.pdf) |                            | - /student/report |
+-------------------+                            +-------------------+
```

## Estrutura do Script Python (`scripts/generate_report.py`)

### 1. Biblioteca Recomendada: `reportlab`
- **Justificativa**: Não possui dependências binárias externas de sistema (ao contrário de `weasyprint` ou `wkhtmltopdf` que exigem bibliotecas C/GTK complexas no Windows), é rápido, confiável e permite controle de páginas, cabeçalhos dinâmicos, tabelas com quebra de página automática (`Table`, `TableStyle`), fontes e paleta de cores institucional.

### 2. Coleta de Dados e Normalização
O script reutiliza a classe `EduTrackClient` de `scripts/calculate_progress.py`:
- `GET /auth/me`: Dados cadastrais do aluno autenticado (Nome, Email, ID).
- `GET /subjects`: Lista de disciplinas cadastradas pelo aluno.
- `GET /academic_tasks`: Lista de tarefas de todas as disciplinas do aluno.
- Cálculo de métricas:
  - Carga horária total acumulada.
  - Total de tarefas cadastradas.
  - Total de tarefas com status `done`.
  - Percentual global = `(total_done / total_tasks) * 100`.
  - Resumo individual de cada disciplina com cálculo de progresso específico.

### 3. Layout e Seções do Documento PDF
- **Padrão de Cores**:
  - Azul Institucional (#1E3A8A) para títulos, cabeçalhos de tabela e barras de destaque.
  - Cinza Neutro (#F3F4F6) para linhas alternadas de tabela.
  - Verde Sucesso (#10B981) para tarefas concluídas e progresso >= 70%.
  - Âmbar Atenção (#F59E0B) para progresso intermediário.
  - Vermelho Alerta (#EF4444) para pendências críticas.
- **Seções Estruturais**:
  1. **Cabeçalho**: Logo institucional EduTrack AI, título oficial "Relatório de Desempenho e Progresso Acadêmico", data e horário de emissão.
  2. **Dados Cadastrais do Aluno**: Nome, ID do Usuário, E-mail cadastrado, Data de Ingresso/Cadastro.
  3. **Quadro de Métricas Chave (KPI Cards)**: Quatro blocos destacados (Disciplinas Ativas, Total de Tarefas, Tarefas Concluídas, Taxa de Conclusão Global).
  4. **Tabela de Disciplinas**: Colunas `Disciplina`, `Professor`, `Carga Horária (h)`, `Tarefas (Concluídas/Total)`, `Progresso (%)` e `Situação`.
  5. **Quadro Resumo de Tarefas Pendentes**: Listagem de tarefas em aberto com data prevista de entrega (`due_date`).
  6. **Rodapé com Hash de Verificação**: Carimbo de data/hora UTC, hash SHA-256 dos dados para verificação de autenticidade e numeração de página ("Página X de Y").

## Arquitetura de Endpoints Xano (XanoScript)

### 1. Endpoint de Download: `student_report_pdf_GET.xs`
- **Verbo e Rota**: `GET /student/report` (Grupo `edutrack.ai`).
- **Autenticação**: `auth = "user"` (Obrigatório JWT Bearer).
- **Parâmetros**: Nenhum obrigatório (o usuário é obtido via `$auth.id`).
- **Funcionamento**:
  - Consulta o registro do relatório mais recente pertencente ao `$auth.id` na tabela de relatórios, ou gera URL assinada de download para o anexo.
  - Retorna o objeto do arquivo contendo `name`, `path`, `mime: "application/pdf"`, `size` e URL pública/assinada de download seguro.

### 2. Endpoint de Upload/Armazenamento: `student_report_upload_POST.xs`
- **Verbo e Rota**: `POST /student/report` (Grupo `edutrack.ai`).
- **Autenticação**: `auth = "user"`.
- **Payload**: Arquivo binário (`attachment`) e metadados opcionais (`periodo`, `checksum`).
- **Funcionamento**:
  - Realiza o upload do anexo no storage privado do Xano.
  - Insere registro na tabela `student_reports` atribuindo obrigatoriamente `user_id = $auth.id`.
  - Retorna a confirmação e metadados do arquivo gravado.

### 3. Tabela de Suporte: `tables/student_reports.xs`
- `id`: int (pk, auto-increment)
- `created_at`: timestamp (default: now)
- `user_id`: int (fk -> user.id, index btree)
- `report_file`: attachment/file (PDF)
- `summary_progress`: decimal/float (progresso gravado no momento da emissão)
- `checksum`: text (SHA-256 do arquivo gerado)

