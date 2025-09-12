import { z } from 'zod';

export const loginSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
});

export const userCreateSchema = z.object({
  username: z.string().min(3, 'Username must be at least 3 characters'),
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  role: z.enum(['doctor', 'nurse', 'admin']),
  department: z.enum(['cardiology', 'neurology', 'pediatrics', 'oncology', 'emergency', 'endocrinology', 'general']),
});

export const userUpdateSchema = userCreateSchema.partial().omit({ password: true });

export const patientCreateSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  date_of_birth: z.string().optional(),
  medical_record_number: z.string().min(1, 'Medical record number is required'),
  department: z.enum(['cardiology', 'neurology', 'pediatrics', 'oncology', 'emergency', 'endocrinology', 'general']),
  assigned_doctor_id: z.string().optional(),
});

export const patientUpdateSchema = patientCreateSchema.partial();

export const documentCreateSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  content: z.string().min(1, 'Content is required'),
  document_type: z.enum(['protocol', 'policy', 'guideline', 'research', 'report', 'medical_record']),
  patient_id: z.string().optional(),
  department: z.enum(['cardiology', 'neurology', 'pediatrics', 'oncology', 'emergency', 'endocrinology', 'general']),
  is_sensitive: z.boolean().default(false),
});

export const documentUpdateSchema = documentCreateSchema.partial();

// Chat/RAG Schemas
export const chatMessageSchema = z.object({
  message: z.string()
    .min(1, 'Message is required')
    .max(1000, 'Message must be less than 1000 characters'),
});

export const chatRequestSchema = z.object({
  message: z.string()
    .min(1, 'Message is required')
    .max(1000, 'Message must be less than 1000 characters'),
  context_department: z.string().optional(),
  max_results: z.number()
    .int()
    .min(1)
    .max(10)
    .optional()
    .default(5),
});

// Search Schema
export const searchRequestSchema = z.object({
  query: z.string()
    .min(1, 'Search query is required')
    .max(200, 'Search query must be less than 200 characters'),
  department: z.string().optional(),
  document_type: z.string().optional(),
  limit: z.number()
    .int()
    .min(1)
    .max(50)
    .optional()
    .default(10),
});

// Type exports
export type LoginInput = z.infer<typeof loginSchema>;
export type UserCreateInput = z.infer<typeof userCreateSchema>;
export type UserUpdateInput = z.infer<typeof userUpdateSchema>;
export type PatientCreateInput = z.infer<typeof patientCreateSchema>;
export type PatientUpdateInput = z.infer<typeof patientUpdateSchema>;
export type DocumentCreateInput = z.infer<typeof documentCreateSchema>;
export type DocumentUpdateInput = z.infer<typeof documentUpdateSchema>;
export type ChatMessageInput = z.infer<typeof chatMessageSchema>;
export type ChatRequestInput = z.infer<typeof chatRequestSchema>;
export type SearchRequestInput = z.infer<typeof searchRequestSchema>;