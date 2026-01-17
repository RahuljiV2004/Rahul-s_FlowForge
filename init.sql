-- Initialize FlowForge database
-- This file runs when PostgreSQL container starts for the first time

-- Create database if it doesn't exist
-- (PostgreSQL automatically creates the database from POSTGRES_DB)

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom types if needed
-- (Add any custom enum types here)

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE flowforge_db TO flowforge_user;

-- Insert default data if needed
-- (Add any initial data here)

-- Create indexes for better performance
-- (Indexes will be created by Alembic migrations)

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'FlowForge database initialized successfully';
END;
$$;
