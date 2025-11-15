-- Initial Lexikon Database Schema
-- This file is for reference. Actual schema is managed by Alembic migrations.

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    institution VARCHAR,
    primary_domain VARCHAR,
    language VARCHAR NOT NULL DEFAULT 'fr',
    country VARCHAR(2),
    adoption_level VARCHAR NOT NULL DEFAULT 'quick-project',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- OAuth accounts table
CREATE TABLE IF NOT EXISTS oauth_accounts (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR NOT NULL,
    provider_user_id VARCHAR NOT NULL,
    access_token VARCHAR,
    refresh_token VARCHAR,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(provider, provider_user_id)
);

-- API keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    key_hash VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    scopes VARCHAR NOT NULL DEFAULT 'read',
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX idx_api_keys_hash ON api_keys(key_hash);

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    language VARCHAR NOT NULL DEFAULT 'fr',
    primary_domain VARCHAR,
    is_public BOOLEAN DEFAULT FALSE,
    owner_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    archived_at TIMESTAMP
);

-- Project members association table
CREATE TABLE IF NOT EXISTS project_members (
    project_id VARCHAR REFERENCES projects(id) ON DELETE CASCADE,
    user_id VARCHAR REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR NOT NULL DEFAULT 'viewer',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id, user_id)
);

-- Terms table
CREATE TABLE IF NOT EXISTS terms (
    id VARCHAR PRIMARY KEY,
    project_id VARCHAR NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    definition TEXT NOT NULL,
    domain VARCHAR,
    level VARCHAR NOT NULL DEFAULT 'quick-draft',
    status VARCHAR NOT NULL DEFAULT 'draft',
    examples TEXT,
    synonyms TEXT,
    formal_definition TEXT,
    citations TEXT,
    metadata TEXT,
    created_by VARCHAR NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_terms_name ON terms(name);
CREATE INDEX idx_terms_project ON terms(project_id);

-- Onboarding sessions table
CREATE TABLE IF NOT EXISTS onboarding_sessions (
    id VARCHAR PRIMARY KEY,
    adoption_level VARCHAR NOT NULL,
    user_id VARCHAR REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- LLM configurations table
CREATE TABLE IF NOT EXISTS llm_configs (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR NOT NULL,
    api_key_encrypted VARCHAR,
    model_name VARCHAR,
    base_url VARCHAR,
    max_tokens INTEGER DEFAULT 1000,
    temperature INTEGER DEFAULT 70,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
