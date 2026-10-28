# Change: academic-tasks

## Why

Students need a reliable way to record and manage lessons, exams, and assignments for each subject. EduTrack AI currently has no academic task table in its Xano schema exports.

## What Changes

- Add an `academic_tasks` table to store task title, optional description, due date, and text status.
- Link each task to a `subjects` record and to its owning `user` for per-student data isolation.
- Keep task lifecycle values as text; defining a controlled status vocabulary and task-management APIs are out of scope.

## Impact

- Adds a Xano table schema export.
- Depends on the `subjects` table being available in the target Xano workspace. It is not currently represented in this repository.
- No existing APIs or application behavior are changed.
