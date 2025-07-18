"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CircularToolError = void 0;
/**
 * Custom error thrown when circular tool invocation is detected
 */
class CircularToolError extends Error {
    toolPattern;
    constructor(message, toolPattern) {
        super(message);
        this.toolPattern = toolPattern;
        this.name = 'CircularToolError';
    }
}
exports.CircularToolError = CircularToolError;
//# sourceMappingURL=CircularToolError.js.map