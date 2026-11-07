# Proposta: Geração de Relatório de Desempenho em PDF e Endpoint de Download no Xano

## Motivação
Atualmente, o **EduTrack AI** consolida o progresso das disciplinas e tarefas através do dashboard Streamlit e do script de cálculo de progresso (`scripts/calculate_progress.py`). No entanto, alunos e tutores precisam de um comprovante físico/digital formal em formato PDF que documente o desempenho individual, a carga horária cursada, as taxas de conclusão de tarefas e a situação geral do aluno.

Esta mudança propõe a implementação de:
1. Um **script Python** (`scripts/generate_report.py`) responsável por coletar os dados do aluno e suas disciplinas/tarefas na API Xano e compilar um relatório visualmente estruturado e profissional em PDF.
2. Um **endpoint no Xano** (XanoScript) pertencente ao grupo `edutrack.ai` que viabiliza o armazenamento e/ou download seguro do arquivo de relatório gerado, garantindo o isolamento estrito por usuário autenticado (`user_id == $auth.id`).
3. Integração inicial opcional com a interface Streamlit (`3_🔒_Perfil.py` e/ou `app.py`) para fornecer um botão direto de download do relatório acadêmico.

## Escopo
- **Script de Geração de PDF (`scripts/generate_report.py`)**:
  - Consumo dos endpoints CRUD existentes via token JWT do aluno (`/auth/me`, `/subjects`, `/academic_tasks`).
  - Reutilização da lógica de cálculo de métricas e progresso por disciplina.
  - Geração de documento PDF contendo cabeçalho institucional do EduTrack AI, resumo do aluno, métricas globais (disciplinas totais, tarefas concluídas vs. pendentes, percentual global de conclusão), tabela detalhada por disciplina e rodapé com data de emissão e código de autenticidade.
  - Suporte a execução via CLI com argumentos `--token`, `--output` e `--upload`.
- **Backend Xano (XanoScript)**:
  - Definição do endpoint `GET /student/report` (ou `student_report_pdf_GET.xs`) com autenticação obrigatória (`auth = "user"`).
  - Tratamento de metadados de arquivo PDF (retorno de URL de download ou stream com cabeçalho `Content-Type: application/pdf` e `Content-Disposition: attachment`).
  - Suporte ao upload do arquivo gerado para armazenamento no Xano (`POST /student/report/upload`).
- **Validação de Segurança**:
  - Restrição para que nenhum aluno consiga visualizar ou baixar relatórios de outros alunos.

## Não-Escopo (Non-goals)
- Implementação de relatórios em outros formatos como planilhas XLSX ou arquivos CSV nesta etapa.
- Disparo e envio automático de e-mails contendo o PDF em anexo.
- Assinatura digital com certificado ICP-Brasil / PKCS#7 (o relatório conterá hash/código de autenticidade emitido pelo sistema).

