/**
 * Custom error classes for the Knowledge Twin Platform
 */

export class KnowledgeTwinError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 500,
    public details?: Record<string, any>
  ) {
    super(message);
    this.name = 'KnowledgeTwinError';
    Error.captureStackTrace(this, this.constructor);
  }
}

export class ValidationError extends KnowledgeTwinError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, 'VALIDATION_ERROR', 400, details);
    this.name = 'ValidationError';
  }
}

export class AuthenticationError extends KnowledgeTwinError {
  constructor(message: string = 'Authentication failed') {
    super(message, 'AUTHENTICATION_ERROR', 401);
    this.name = 'AuthenticationError';
  }
}

export class AuthorizationError extends KnowledgeTwinError {
  constructor(message: string = 'Unauthorized access') {
    super(message, 'AUTHORIZATION_ERROR', 403);
    this.name = 'AuthorizationError';
  }
}

export class NotFoundError extends KnowledgeTwinError {
  constructor(resource: string, id?: string) {
    const message = id ? `${resource} with id ${id} not found` : `${resource} not found`;
    super(message, 'NOT_FOUND', 404);
    this.name = 'NotFoundError';
  }
}

export class ExtractionError extends KnowledgeTwinError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, 'EXTRACTION_ERROR', 422, details);
    this.name = 'ExtractionError';
  }
}

export class PathGenerationError extends KnowledgeTwinError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, 'PATH_GENERATION_ERROR', 422, details);
    this.name = 'PathGenerationError';
  }
}

export class InsufficientDataError extends KnowledgeTwinError {
  constructor(message: string, missing_fields?: string[]) {
    super(message, 'INSUFFICIENT_DATA', 422, { missing_fields });
    this.name = 'InsufficientDataError';
  }
}

export class DatabaseError extends KnowledgeTwinError {
  constructor(message: string, originalError?: Error) {
    super(message, 'DATABASE_ERROR', 500, { originalError: originalError?.message });
    this.name = 'DatabaseError';
  }
}

export class ExternalServiceError extends KnowledgeTwinError {
  constructor(service: string, message: string) {
    super(`${service}: ${message}`, 'EXTERNAL_SERVICE_ERROR', 502);
    this.name = 'ExternalServiceError';
  }
}
