-- SQL dump generated using DBML (dbml.dbdiagram.io)
-- Database: PostgreSQL
-- Generated at: 2026-01-26T12:57:45.160Z

CREATE TYPE "roles" AS ENUM (
  'Admin',
  'Manager',
  'Member'
);

CREATE TYPE "team_roles" AS ENUM (
  'Owner',
  'Admin',
  'Member'
);

CREATE TYPE "project_roles" AS ENUM (
  'Lead',
  'Technical Lead',
  'Member'
);

CREATE TYPE "invite_status" AS ENUM (
  'pending',
  'accepted',
  'declined'
);

CREATE TYPE "priority_level" AS ENUM (
  'Critical',
  'High',
  'Medium',
  'Low'
);

CREATE TYPE "task_status" AS ENUM (
  'Done',
  'Unplanned',
  'Pending',
  'In-Progress'
);

CREATE TABLE "user_teams" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid,
  "team_id" uuid,
  "team_role" team_roles,
  "created_at" timestamp,
  "updated_at" timestamp,
  "deleted_at" timestamp
);

CREATE TABLE "project_members" (
  "id" uuid PRIMARY KEY,
  "project_id" uuid,
  "user_id" uuid,
  "role" project_roles,
  "created_at" timestamp,
  "updated_at" timestamp,
  "deleted_at" timestamp
);

CREATE TABLE "task_attachments" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid,
  "task_id" uuid,
  "s3_uri" varchar
);

CREATE TABLE "team_invites" (
  "id" uuid PRIMARY KEY,
  "team_id" uuid,
  "invitee_email" varchar,
  "expiry" timestamp,
  "status" invite_status,
  "usage_limit" integer,
  "used_count" integer,
  "created_at" timestamp,
  "updated_at" timestamp,
  "deleted_at" timestamp,
  "created_by" uuid
);

CREATE TABLE "tasks" (
  "id" uuid PRIMARY KEY,
  "name" varchar,
  "project_id" uuid,
  "description" varchar,
  "status" task_status,
  "priority" priority_level,
  "due_date" timestamp,
  "position" integer,
  "parent_id" uuid,
  "created_by" uuid,
  "assigned_to" uuid,
  "created_at" timestamp,
  "updated_at" timestamp,
  "deleted_at" timestamp
);

CREATE TABLE "task_comments" (
  "id" uuid PRIMARY KEY,
  "task_id" uuid,
  "comment" varchar,
  "reply_to" uuid,
  "created_at" timestamp,
  "created_by" uuid,
  "updated_at" timestamp,
  "deleted_at" timestamp
);

CREATE TABLE "labels" (
  "id" uuid PRIMARY KEY,
  "team_id" uuid,
  "name" varchar,
  "description" varchar,
  "created_at" timestamp,
  "created_by" uuid,
  "updated_at" timestamp,
  "deleted_at" timestamp
);

CREATE TABLE "task_labels" (
  "id" uuid PRIMARY KEY,
  "task_id" uuid,
  "label_id" uuid,
  "created_at" timestamp,
  "updated_at" timestamp,
  "deleted_at" timestamp
);

CREATE TABLE "projects" (
  "id" uuid PRIMARY KEY,
  "team_id" uuid,
  "name" varchar,
  "description" varchar,
  "created_at" timestamp,
  "created_by" uuid,
  "updated_at" timestamp,
  "deleted_at" timestamp
);

CREATE TABLE "users" (
  "id" uuid PRIMARY KEY,
  "username" varchar,
  "role" roles,
  "email" varchar UNIQUE,
  "email_verified_at" timestamp,
  "password" varchar,
  "remember_token" varchar,
  "bio" varchar,
  "avatar_token_url" varchar,
  "created_at" timestamp,
  "updated_at" timestamp,
  "deleted_at" timestamp
);

CREATE TABLE "teams" (
  "id" uuid PRIMARY KEY,
  "name" varchar,
  "description" varchar,
  "created_at" timestamp,
  "created_by" uuid,
  "updated_at" timestamp,
  "deleted_at" timestamp
);

CREATE TABLE "audit_log" (
  "id" uuid PRIMARY KEY,
  "action" varchar,
  "entity_type" varchar,
  "entity_id" uuid,
  "old_values" json,
  "new_values" json,
  "done_by" uuid,
  "done_at" timestamp
);

CREATE UNIQUE INDEX ON "user_teams" ("user_id", "team_id");

CREATE UNIQUE INDEX ON "project_members" ("project_id", "user_id");

ALTER TABLE "user_teams" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "user_teams" ADD FOREIGN KEY ("team_id") REFERENCES "teams" ("id");

ALTER TABLE "project_members" ADD FOREIGN KEY ("project_id") REFERENCES "projects" ("id");

ALTER TABLE "project_members" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "task_attachments" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "task_attachments" ADD FOREIGN KEY ("task_id") REFERENCES "tasks" ("id");

ALTER TABLE "team_invites" ADD FOREIGN KEY ("team_id") REFERENCES "teams" ("id");

ALTER TABLE "team_invites" ADD FOREIGN KEY ("created_by") REFERENCES "users" ("id");

ALTER TABLE "tasks" ADD FOREIGN KEY ("project_id") REFERENCES "projects" ("id");

ALTER TABLE "tasks" ADD FOREIGN KEY ("parent_id") REFERENCES "tasks" ("id");

ALTER TABLE "tasks" ADD FOREIGN KEY ("created_by") REFERENCES "users" ("id");

ALTER TABLE "tasks" ADD FOREIGN KEY ("assigned_to") REFERENCES "users" ("id");

ALTER TABLE "task_comments" ADD FOREIGN KEY ("task_id") REFERENCES "tasks" ("id");

ALTER TABLE "task_comments" ADD FOREIGN KEY ("reply_to") REFERENCES "task_comments" ("id");

ALTER TABLE "task_comments" ADD FOREIGN KEY ("created_by") REFERENCES "users" ("id");

ALTER TABLE "labels" ADD FOREIGN KEY ("team_id") REFERENCES "teams" ("id");

ALTER TABLE "labels" ADD FOREIGN KEY ("created_by") REFERENCES "users" ("id");

ALTER TABLE "task_labels" ADD FOREIGN KEY ("task_id") REFERENCES "tasks" ("id");

ALTER TABLE "task_labels" ADD FOREIGN KEY ("label_id") REFERENCES "labels" ("id");

ALTER TABLE "projects" ADD FOREIGN KEY ("team_id") REFERENCES "teams" ("id");

ALTER TABLE "projects" ADD FOREIGN KEY ("created_by") REFERENCES "users" ("id");

ALTER TABLE "teams" ADD FOREIGN KEY ("created_by") REFERENCES "users" ("id");

ALTER TABLE "audit_log" ADD FOREIGN KEY ("done_by") REFERENCES "users" ("id");
