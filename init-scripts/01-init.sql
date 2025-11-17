-- Initialization script for PostgreSQL database
-- Executed automatically on first container startup

-- Database 2fa_app_db is already created by POSTGRES_DB variable
-- This script can contain additional configurations

-- Create extensions (if needed)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Successful initialization notification
DO $$
BEGIN
    RAISE NOTICE 'Database 2fa_app_db has been successfully initialized!';
END $$;
