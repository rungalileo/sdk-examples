-- 01_seed_users.sql
-- This script runs automatically when the PostgreSQL container starts with an empty database
-- It seeds the database with demo users for authentication

-- Insert demo users with hashed passwords (password: "secure_password" for all)
INSERT INTO users (id, username, email, hashed_password, role, department, is_active, created_at) VALUES 
  (1, 'admin_wilson', 'jennifer.wilson@hospital.com', '$2b$12$gdtwLxe4YU648JwtZPX8/uAv9n5qpKZ8VFXJ1iyjqVU/HExd20IXC', 'admin', 'administration', true, NOW()),
  (2, 'dr_smith', 'sarah.smith@hospital.com', '$2b$12$xDK9vMsg6XD0wrbp9mTONeqZgViFvQGbUT9HMb2l1aU.nX5ssLnkS', 'doctor', 'cardiology', true, NOW()),
  (3, 'nurse_johnson', 'michael.johnson@hospital.com', '$2b$12$tVxonl15Y9xoKXKeBLQcX.mZO7ovvOtfRiI.vqPCqjRyuOVCmazfC', 'nurse', 'emergency', true, NOW())
ON CONFLICT (username) DO NOTHING;

-- Reset the sequence to ensure new users get proper IDs
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));

-- Verify users were created
DO $$
BEGIN
    IF (SELECT COUNT(*) FROM users) > 0 THEN
        RAISE NOTICE 'Successfully seeded % demo users', (SELECT COUNT(*) FROM users);
        RAISE NOTICE 'Demo credentials: admin_wilson/secure_password, dr_smith/secure_password, nurse_johnson/secure_password';
    ELSE
        RAISE WARNING 'No users were seeded - check for conflicts or errors';
    END IF;
END $$;
