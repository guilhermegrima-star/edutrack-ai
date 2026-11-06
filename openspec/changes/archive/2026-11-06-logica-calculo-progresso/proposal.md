# Proposta: Lógica de Cálculo de Progresso por Disciplina

## Motivação

O EduTrack AI precisa fornecer ao usuário uma visão clara do quanto ele já avançou em cada disciplina com base nas tarefas cadastradas. Atualmente não existe nenhum mecanismo que calcule automaticamente essa métrica — o dado existe no backend (campo `status` em `academic_tasks`), mas não há script ou função que o agregue e o exponha como um percentual de progresso.

## O que será feito

Implementar `scripts/calculate_progress.py`: um script Python que consome os endpoints CRUD do grupo `edutrack.ai` no Xano e calcula, para uma dada disciplina (`subject_id`), a porcentagem de tarefas concluídas em relação ao total de tarefas cadastradas, retornando o resultado como JSON.

## Por que é necessário

- Permite integrar o indicador de progresso na interface Streamlit (`app.py` e páginas futuras).
- Serve como base para funcionalidades de IA/agente que monitoram engajamento acadêmico.
- Reutiliza os endpoints CRUD já implementados (`GET /academic_tasks`, `GET /subjects/{id}`), sem necessidade de novos endpoints no backend.

## Escopo

- Criação do arquivo `scripts/calculate_progress.py` com:
  - Classe `EduTrackClient`: cliente HTTP autenticado (Bearer JWT) para todos os endpoints CRUD de `academic_tasks` e `subjects`.
  - Função `calculate_progress(client, subject_id)`: calcula `progress_percent = (completed / total) × 100`, retorna dict com metadados da disciplina e detalhes por tarefa.
  - Função auxiliar `progress_to_json(result)`: serializa o resultado para string JSON formatada.
  - Suporte a execução via linha de comando (`--subject-id`, `--token`, `--done-status`).
- Adição da variável `EDUTRACK_BASE_URL` no `.env`.

## Fora do escopo

- Criação de novo endpoint no Xano.
- Alteração da interface Streamlit (fase futura).
- Persistência do progresso calculado em banco de dados.
