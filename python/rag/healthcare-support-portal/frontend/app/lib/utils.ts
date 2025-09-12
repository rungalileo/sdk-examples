import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
  const d = new Date(date)
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

export function formatDateTime(date: string | Date): string {
  const d = new Date(date)
  return d.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export function getRoleColor(role: string): string {
  switch (role.toLowerCase()) {
    case 'doctor':
      return 'text-blue-600 bg-blue-50 border-blue-200'
    case 'nurse':
      return 'text-green-600 bg-green-50 border-green-200'
    case 'admin':
      return 'text-purple-600 bg-purple-50 border-purple-200'
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200'
  }
}

export function getDepartmentColor(department: string): string {
  switch (department.toLowerCase()) {
    case 'cardiology':
      return 'border-red-500'
    case 'neurology':
      return 'border-purple-500'
    case 'pediatrics':
      return 'border-yellow-500'
    case 'oncology':
      return 'border-pink-500'
    case 'emergency':
      return 'border-orange-500'
    case 'endocrinology':
      return 'border-teal-500'
    default:
      return 'border-blue-500'
  }
}

export function getStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'active':
      return 'text-green-600 bg-green-50 border-green-200'
    case 'inactive':
      return 'text-gray-600 bg-gray-50 border-gray-200'
    case 'pending':
      return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    case 'urgent':
      return 'text-red-600 bg-red-50 border-red-200'
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200'
  }
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

export function generateInitials(name: string): string {
  return name
    .split(' ')
    .map(word => word.charAt(0))
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null
  
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

export function isValidMRN(mrn: string): boolean {
  // Basic MRN validation - adjust pattern as needed
  const mrnRegex = /^MRN-\d{4}-\d{3}$/
  return mrnRegex.test(mrn)
}

export function sanitizeInput(input: string): string {
  return input.trim().replace(/[<>]/g, '')
}