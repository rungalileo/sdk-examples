/**
 * Custom error thrown when circular tool invocation is detected
 */
export declare class CircularToolError extends Error {
    readonly toolPattern: string[];
    constructor(message: string, toolPattern: string[]);
}
//# sourceMappingURL=CircularToolError.d.ts.map