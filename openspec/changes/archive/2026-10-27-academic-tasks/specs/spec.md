# Academic Tasks Specification

## Purpose

Define persistent storage for academic obligations associated with a subject and an owning student.

## Requirements

### Requirement: Store academic tasks

The system MUST store academic tasks in an `academic_tasks` table. Each record MUST include:

- `title` as text.
- `description` as optional text.
- `due_date` as a date.
- `status` as text.
- `subject_id` as a required reference to `subjects`.
- `user_id` as a required reference to `user` for ownership and student-level data isolation.

The table MUST also include the platform-standard `id` and `created_at` fields.

#### Scenario: Create a task for a subject

- GIVEN a student and a subject exist
- WHEN an academic task is stored
- THEN its title, due date, status, subject reference, and owning user are persisted
- AND its description may be omitted

### Requirement: Scope task access to the owning student

Any future database query or API operation that reads or changes academic task data MUST scope the operation to the authenticated user's `user_id`.

#### Scenario: Access tasks as an authenticated student

- GIVEN an authenticated student requests academic task data
- WHEN the application reads or changes tasks
- THEN it MUST only operate on records whose `user_id` matches the authenticated user's id

### Requirement: Preserve free-form task status

The `status` field MUST remain text. This change MUST NOT impose a fixed status vocabulary or workflow.

#### Scenario: Store a task status

- GIVEN an academic task has a status value
- WHEN the record is stored
- THEN the value is stored as text without applying an enum restriction

## Dependencies

- The target Xano workspace MUST provide a `subjects` table for the `subject_id` reference. This repository does not currently contain its schema export.
