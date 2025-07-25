/**
 * Custom error thrown when circular tool invocation is detected
 */
export class CircularToolError extends Error {
  constructor(message: string, public readonly toolPattern: string[]) {
    super(message);
    this.name = 'CircularToolError';
  }
}
