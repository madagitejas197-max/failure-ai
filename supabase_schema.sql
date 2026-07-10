-- FailureAI Database Schema Migration for Supabase
-- This SQL script creates all tables, relationships, indexes, and constraints.
-- You can run this directly in the Supabase SQL Editor.

BEGIN;

-- ── 1. USERS TABLE ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id UUID NOT NULL, 
    email VARCHAR(255) NOT NULL, 
    password_hash VARCHAR(255), 
    display_name VARCHAR(255) NOT NULL, 
    avatar_url VARCHAR(512), 
    bio TEXT, 
    role VARCHAR(50) DEFAULT 'user' NOT NULL, 
    github_id VARCHAR(100), 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (github_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email);
CREATE INDEX IF NOT EXISTS ix_users_id ON users (id);

-- ── 2. PROJECTS TABLE ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS projects (
    id UUID NOT NULL, 
    owner_id UUID NOT NULL, 
    name VARCHAR(255) NOT NULL, 
    description TEXT, 
    tech_stack VARCHAR[] NOT NULL, 
    visibility VARCHAR(50) DEFAULT 'public' NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(owner_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_projects_id ON projects (id);

-- ── 3. FAILURES TABLE ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS failures (
    id UUID NOT NULL, 
    project_id UUID, 
    author_id UUID NOT NULL, 
    category VARCHAR(50) NOT NULL, 
    tech_stack VARCHAR[] NOT NULL, 
    title VARCHAR(255) NOT NULL, 
    problem TEXT NOT NULL, 
    root_cause TEXT NOT NULL, 
    solution TEXT NOT NULL, 
    lesson_learned TEXT NOT NULL, 
    severity VARCHAR(50) NOT NULL, 
    logs_redacted TEXT, 
    github_url VARCHAR(512), 
    time_to_detect_seconds INTEGER, 
    time_to_resolve_seconds INTEGER, 
    visibility VARCHAR(50) DEFAULT 'public' NOT NULL, 
    status VARCHAR(50) DEFAULT 'draft' NOT NULL, 
    embedding_id VARCHAR(255), 
    upvote_count INTEGER DEFAULT '0' NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(author_id) REFERENCES users (id) ON DELETE CASCADE, 
    FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS ix_failures_id ON failures (id);

-- ── 4. COMMENTS TABLE ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS comments (
    id UUID NOT NULL, 
    failure_id UUID NOT NULL, 
    author_id UUID NOT NULL, 
    body TEXT NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(author_id) REFERENCES users (id) ON DELETE CASCADE, 
    FOREIGN KEY(failure_id) REFERENCES failures (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_comments_id ON comments (id);

-- ── 5. TAGS TABLE ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tags (
    id UUID NOT NULL, 
    name VARCHAR(100) NOT NULL, 
    category VARCHAR(100), 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS ix_tags_id ON tags (id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_tags_name ON tags (name);

-- ── 6. FAILURE TAGS TABLE (M2M) ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS failure_tags (
    failure_id UUID NOT NULL, 
    tag_id UUID NOT NULL, 
    PRIMARY KEY (failure_id, tag_id), 
    FOREIGN KEY(failure_id) REFERENCES failures (id) ON DELETE CASCADE, 
    FOREIGN KEY(tag_id) REFERENCES tags (id) ON DELETE CASCADE
);

-- ── 7. AUDIT LOGS TABLE ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID NOT NULL, 
    actor_id UUID, 
    action VARCHAR(255) NOT NULL, 
    resource_type VARCHAR(100) NOT NULL, 
    resource_id UUID, 
    metadata_json JSONB, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(actor_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS ix_audit_logs_id ON audit_logs (id);

COMMIT;
