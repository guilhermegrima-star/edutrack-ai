# Especificação: Geração de Relatório de Desempenho em PDF e Download no Xano

## 1. Especificação do Script Python (`scripts/generate_report.py`)

### 1.1 Entradas e Parâmetros CLI
O script deve poder ser executado via linha de comando ou importado como módulo:
- `--token` (string, opcional se definido na variável de ambiente `EDUTRACK_TOKEN`): Token JWT Bearer do aluno.
- `--output` (string, opcional): Caminho de destino para salvar o PDF gerado. Valor padrão: `relatorios/relatorio_desempenho_<user_id>.pdf`.
- `--upload` (flag booleana, opcional): Se acionada, envia automaticamente o arquivo gerado para o endpoint do Xano via `POST /student/report`.
- `--base-url` (string, opcional): URL base do Xano (padrão lido de `EDUTRACK_BASE_URL`).

### 1.2 Regras de Negócio de Consolidação
1. **Identificação do Aluno**: Os dados cadastrais são obtidos de `GET /auth/me`. Caso o endpoint não retorne o nome, utilizar fallback para o e-mail ou `Aluno #<ID>`.
2. **Cálculo de Progresso por Matéria**:
   - Cada disciplina listada em `GET /subjects` tem suas tarefas consultadas via `GET /academic_tasks?subject_id=<id>`.
   - Tarefas com campo `status == "done"` (case-insensitive, com trim) são computadas como concluídas.
   - Progresso individual = `(tarefas_concluidas / total_tarefas) * 100` (arredondado em 1 casa decimal).
   - Se uma disciplina não tiver tarefas cadastradas, o progresso é `0.0%` e o status exibido é "Sem tarefas".
3. **Métricas Consolidadas do Aluno**:
   - Total de disciplinas cadastradas.
   - Carga horária total (soma de `hours` de todas as disciplinas).
   - Total acumulado de tarefas.
   - Total acumulado de tarefas concluídas e pendentes.
   - Progresso acadêmico geral: percentual de tarefas concluídas sobre o total de todas as disciplinas.
4. **Tratamento de Exceções**:
   - Falha de conexão ou erro HTTP 401/403/500 deve emitir mensagem descritiva em formato JSON e código de saída apropriado (`sys.exit(1)`).

### 1.3 Saída do Script
- O arquivo `.pdf` gerado fisicamente no caminho indicado.
- Saída padrão (stdout) em JSON estruturado para consumo por automações e pela interface:
  ```json
  {
    "status": "success",
    "pdf_path": "relatorios/relatorio_desempenho_101.pdf",
    "file_size_bytes": 48210,
    "user_id": 101,
    "user_name": "Guilherme Grima",
    "total_subjects": 4,
    "total_tasks": 12,
    "completed_tasks": 9,
    "global_progress_percent": 75.0,
    "uploaded_to_xano": false
  }
  ```

---

## 2. Especificação dos Endpoints Xano (XanoScript)

### 2.1 Endpoint: `GET /student/report`
- **Arquivo**: `apis/edutrack_ai/student_report_GET.xs`
- **Grupo de API**: `edutrack.ai` (canonical: `gTfD518O`)
- **Autenticação**: `auth = "user"`
- **Entrada (Query/Params)**:
  - `int report_id?` (opcional: se não fornecido, retorna o relatório mais recente do usuário autenticado).
- **Lógica e Isolamento**:
  - Consulta a tabela `student_reports` com cláusula de segurança obrigatória:
    `where = ($db.student_reports.user_id == $auth.id)`
  - Ordenação por `created_at` descendente para pegar a versão mais atual caso `report_id` seja omitido.
  - Se nenhum relatório for encontrado, retorna HTTP 404 com mensagem: `"Nenhum relatório encontrado para o aluno."`.
- **Resposta de Sucesso (200 OK)**:
  ```json
  {
    "id": 1,
    "user_id": 101,
    "created_at": 1730937600000,
    "summary_progress": 75.0,
    "checksum": "a8f5f167...",
    "file": {
      "access": "public",
      "path": "/vault/.../relatorio_desempenho_101.pdf",
      "name": "relatorio_desempenho_101.pdf",
      "type": "attachment",
      "size": 48210,
      "mime": "application/pdf",
      "url": "https://...xano.io/.../relatorio_desempenho_101.pdf"
    }
  }
  ```

### 2.2 Endpoint: `POST /student/report`
- **Arquivo**: `apis/edutrack_ai/student_report_POST.xs`
- **Grupo de API**: `edutrack.ai`
- **Autenticação**: `auth = "user"`
- **Entrada**:
  - `file report_file` (arquivo binário PDF obrigatório)
  - `decimal summary_progress?` (progresso registrado no momento da emissão)
  - `text checksum?` (código de verificação)
- **Lógica e Isolamento**:
  - O campo `user_id` da gravação é forçado com o valor seguro do token: `$auth.id`.
  - Salva o arquivo na storage do Xano associado à tabela `student_reports`.
- **Resposta de Sucesso (201 Created)**:
  - Retorna o registro recém-criado com metadados e URL de acesso.

---

## 3. Especificação da Tabela: `student_reports`
- **Arquivo**: `tables/student_reports.xs`
- **Campos**:
  - `id`: int (pk, auto-increment)
  - `created_at`: timestamp (default: now)
  - `user_id`: int (referência ao usuário autenticado, com índice `btree`)
  - `report_file`: attachment (arquivo PDF)
  - `summary_progress`: decimal (armazenamento do progresso calculado)
  - `checksum`: text (hash SHA-256)
- **Índices**:
  - Chave primária em `id`.
  - Índice B-Tree em `user_id` para otimização de consultas por aluno.

