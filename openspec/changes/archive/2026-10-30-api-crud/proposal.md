# Proposta: Endpoints CRUD e Controle de Acesso para Subjects e Academic Tasks

## Motivação
Fornecer operações completas de manipulação de dados (com foco em PATCH e DELETE, além de POST e GET) para as tabelas `subjects` (matérias) e `academic_tasks` (tarefas acadêmicas) no backend Xano (XanoScript), garantindo isolamento total por usuário autenticado (multitenancy por `user_id`).

## Escopo
- Criação e validação das tabelas `subjects` e `academic_tasks`.
- Implementação dos endpoints de consulta, criação, atualização (`PATCH`) e exclusão (`DELETE`) para `subjects`.
- Implementação dos endpoints de consulta, criação, atualização (`PATCH`) e exclusão (`DELETE`) para `academic_tasks`.
- Validação e imposição de segurança: o usuário só pode ler, modificar ou deletar seus próprios registros (`$auth.id == record.user_id`).

