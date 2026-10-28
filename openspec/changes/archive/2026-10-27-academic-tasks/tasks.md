## 1. Add academic task storage

- [x] 1.1 Add the `academic_tasks` Xano schema with `title`, optional `description`, `due_date`, text `status`, and references to `subjects` and `user`.
- [x] 1.2 Include the standard `id` and private `created_at` fields and the standard primary key and creation-time indexes.
- [x] 1.3 Verify the schema export is consistent with the academic task specification and existing Xano table syntax.

## 2. Verify integration prerequisites

- [ ] 2.1 Confirm that a `subjects` table exists in the target Xano workspace before applying the table schema.
- [ ] 2.2 Ensure future task queries and API operations enforce ownership using the authenticated user's `user_id`.
