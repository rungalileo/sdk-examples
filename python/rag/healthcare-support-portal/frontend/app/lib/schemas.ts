import { z } from 'zod';

// Auth Schemas
export const loginSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
});

export const registerSchema = z.object({
  username: z.string()
    .min(3, 'Username must be at least 3 characters')
    .max(50, 'Username must be less than 50 characters')
    .regex(/^[a-zA-Z0-9_]+$/, 'Username can only contain letters, numbers, and underscores'),
  email: z.string()
    .email('Invalid email address'),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/(?=.*[a-z])/, 'Password must contain at least one lowercase letter')
    .regex(/(?=.*[A-Z])/, 'Password must contain at least one uppercase letter')
    .regex(/(?=.*[0-9])/, 'Password must contain at least one number'),
  role: z.enum(['doctor', 'nurse', 'admin']),
  department: z.enum([
    'cardiology',
    'neurology',
    'pediatrics',
    'oncology',
    'emergency',
    'endocrinology',
    'general'
  ]),
});

// Patient Schemas
export const patientCreateSchema = z.object({
  name: z.string()
    .min(1, 'Name is required')
    .max(100, 'Name must be less than 100 characters'),
  date_of_birth: z.string()
    .optional()
    .refine((val) => !val || !isNaN(Date.parse(val)), 'Invalid date format'),
  medical_record_number: z.string()
    .min(1, 'Medical record number is required')
    .regex(/^MRN-\d{6}$/, 'Medical record number must be in format MRN-XXXXXX'),
  department: z.enum([
    'cardiology',
    'neurology',
    'pediatrics',
    'oncology',
    'emergency',
    'endocrinology',
    'general'
  ]),
  assigned_doctor_id: z.number()
    .int()
    .positive()
    .optional()
    .or(z.string().transform(val => val ? parseInt(val, 10) : undefined)),
});

export const patientUpdateSchema = patientCreateSchema.partial().extend({
  is_active: z.boolean().optional(),
});

// Document Schemas
export const documentCreateSchema = z.object({
  title: z.string()
    .min(1, 'Title is required')
    .max(200, 'Title must be less than 200 characters'),
  content: z.string()
    .min(1, 'Content is required')
    .max(10000, 'Content must be less than 10000 characters'),
  document_type: z.enum([
    'protocol',
    'policy',
    'guideline',
    'research',
    'report',
    'medical_record'
  ]),
  patient_id: z.number()
    .int()
    .positive()
    .optional()
    .or(z.string().transform(val => val ? parseInt(val, 10) : undefined)),
  department: z.enum([
    'cardiology',
    'neurology',
    'pediatrics',
    'oncology',
    'emergency',
    'endocrinology',
    'general'
  ]),
  is_sensitive: z.boolean()
    .optional()
    .default(false),
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
export type RegisterInput = z.infer<typeof registerSchema>;
export type PatientCreateInput = z.infer<typeof patientCreateSchema>;
export type PatientUpdateInput = z.infer<typeof patientUpdateSchema>;
export type DocumentCreateInput = z.infer<typeof documentCreateSchema>;
export type DocumentUpdateInput = z.infer<typeof documentUpdateSchema>;
export type ChatMessageInput = z.infer<typeof chatMessageSchema>;
export type ChatRequestInput = z.infer<typeof chatRequestSchema>;
export type SearchRequestInput = z.infer<typeof searchRequestSchema>;