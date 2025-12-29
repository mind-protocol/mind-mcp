/**
 * Runtime Schema Loader
 *
 * Loads schema.yaml at runtime — types are dynamic, not generated.
 *
 * Usage:
 *   import { loadSchema, getNodeTypes, validateNode } from './schema';
 *
 *   const schema = await loadSchema();
 *   const nodeTypes = getNodeTypes(schema);
 *   const isValid = validateNode(schema, node);
 */

import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'js-yaml';

// =============================================================================
// Schema Types (minimal, just for parsing)
// =============================================================================

export interface SchemaField {
  type: string;
  required?: boolean;
  nullable?: boolean;
  default?: unknown;
  range?: [number, number] | string;
  values?: string[];
  description?: string;
  items?: string | string[];
  length?: number;
  auto?: boolean;
  computed?: boolean;
}

export interface SchemaSection {
  fields?: Record<string, SchemaField>;
  role?: string;
  behavior?: string;
  description?: string;
  extends?: string;
}

export interface Schema {
  version: string;
  updated: string;
  status: string;
  nodes: Record<string, SchemaSection>;
  links: Record<string, SchemaSection>;
  NodeBase: SchemaSection;
  MomentBase?: SchemaSection;
  LinkBase: SchemaSection;
  SubEntity?: SchemaSection;
  invariants?: string[];
}

// =============================================================================
// Schema Loading
// =============================================================================

let cachedSchema: Schema | null = null;

const SCHEMA_PATHS = [
  '.mind/schema.yaml',
  'docs/schema/schema.yaml',
  '../../../.mind/schema.yaml',
  '../../../docs/schema/schema.yaml',
];

/**
 * Find schema.yaml in known locations
 */
export function findSchemaPath(basePath?: string): string | null {
  const base = basePath || process.cwd();

  for (const relative of SCHEMA_PATHS) {
    const candidate = path.resolve(base, relative);
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }

  return null;
}

/**
 * Load schema.yaml at runtime
 * Caches result for performance
 */
export async function loadSchema(schemaPath?: string): Promise<Schema> {
  if (cachedSchema) {
    return cachedSchema;
  }

  const resolvedPath = schemaPath || findSchemaPath();
  if (!resolvedPath) {
    throw new Error('schema.yaml not found. Run `mind init` or provide path.');
  }

  const content = await fs.promises.readFile(resolvedPath, 'utf-8');
  cachedSchema = yaml.load(content) as Schema;

  return cachedSchema;
}

/**
 * Load schema synchronously (for initialization)
 */
export function loadSchemaSync(schemaPath?: string): Schema {
  if (cachedSchema) {
    return cachedSchema;
  }

  const resolvedPath = schemaPath || findSchemaPath();
  if (!resolvedPath) {
    throw new Error('schema.yaml not found. Run `mind init` or provide path.');
  }

  const content = fs.readFileSync(resolvedPath, 'utf-8');
  cachedSchema = yaml.load(content) as Schema;

  return cachedSchema;
}

/**
 * Clear cached schema (for testing)
 */
export function clearSchemaCache(): void {
  cachedSchema = null;
}

// =============================================================================
// Schema Accessors
// =============================================================================

/**
 * Get node type names from schema
 */
export function getNodeTypes(schema: Schema): string[] {
  return Object.keys(schema.nodes);
}

/**
 * Get node type metadata
 */
export function getNodeTypeMeta(schema: Schema, nodeType: string): SchemaSection | undefined {
  return schema.nodes[nodeType];
}

/**
 * Get all NodeBase fields
 */
export function getNodeFields(schema: Schema): Record<string, SchemaField> {
  return schema.NodeBase.fields || {};
}

/**
 * Get all LinkBase fields
 */
export function getLinkFields(schema: Schema): Record<string, SchemaField> {
  return schema.LinkBase.fields || {};
}

/**
 * Get field default value
 */
export function getFieldDefault(field: SchemaField): unknown {
  return field.default;
}

/**
 * Get enum values for a field
 */
export function getEnumValues(field: SchemaField): string[] | undefined {
  return field.values;
}

// =============================================================================
// Validation
// =============================================================================

export interface ValidationError {
  field: string;
  message: string;
  value?: unknown;
}

/**
 * Validate a value against a schema field
 */
export function validateField(
  field: SchemaField,
  value: unknown,
  fieldName: string
): ValidationError | null {
  // Check required
  if (field.required && (value === undefined || value === null)) {
    return { field: fieldName, message: 'Required field is missing', value };
  }

  // Allow null if nullable
  if (value === null && field.nullable) {
    return null;
  }

  // Skip if undefined and not required
  if (value === undefined) {
    return null;
  }

  // Type check
  switch (field.type) {
    case 'string':
      if (typeof value !== 'string') {
        return { field: fieldName, message: `Expected string, got ${typeof value}`, value };
      }
      break;

    case 'int':
    case 'float':
      if (typeof value !== 'number') {
        return { field: fieldName, message: `Expected number, got ${typeof value}`, value };
      }
      // Range check
      if (field.range && Array.isArray(field.range)) {
        const [min, max] = field.range;
        if (value < min || value > max) {
          return { field: fieldName, message: `Value ${value} outside range [${min}, ${max}]`, value };
        }
      }
      break;

    case 'bool':
    case 'boolean':
      if (typeof value !== 'boolean') {
        return { field: fieldName, message: `Expected boolean, got ${typeof value}`, value };
      }
      break;

    case 'enum':
      if (field.values && !field.values.includes(value as string)) {
        return { field: fieldName, message: `Invalid enum value. Expected one of: ${field.values.join(', ')}`, value };
      }
      break;

    case 'vector':
    case 'array':
      if (!Array.isArray(value)) {
        return { field: fieldName, message: `Expected array, got ${typeof value}`, value };
      }
      if (field.length && value.length !== field.length) {
        return { field: fieldName, message: `Expected array of length ${field.length}, got ${value.length}`, value };
      }
      break;
  }

  return null;
}

/**
 * Validate a node against schema
 */
export function validateNode(schema: Schema, node: Record<string, unknown>): ValidationError[] {
  const errors: ValidationError[] = [];
  const fields = getNodeFields(schema);

  for (const [fieldName, field] of Object.entries(fields)) {
    const error = validateField(field, node[fieldName], fieldName);
    if (error) {
      errors.push(error);
    }
  }

  // Check node_type is valid
  const nodeType = node.node_type as string;
  if (nodeType && !getNodeTypes(schema).includes(nodeType)) {
    errors.push({
      field: 'node_type',
      message: `Invalid node_type. Expected one of: ${getNodeTypes(schema).join(', ')}`,
      value: nodeType,
    });
  }

  return errors;
}

/**
 * Validate a link against schema
 */
export function validateLink(schema: Schema, link: Record<string, unknown>): ValidationError[] {
  const errors: ValidationError[] = [];
  const fields = getLinkFields(schema);

  for (const [fieldName, field] of Object.entries(fields)) {
    const error = validateField(field, link[fieldName], fieldName);
    if (error) {
      errors.push(error);
    }
  }

  return errors;
}

// =============================================================================
// Defaults
// =============================================================================

/**
 * Apply default values from schema to a node
 */
export function applyNodeDefaults(schema: Schema, node: Record<string, unknown>): Record<string, unknown> {
  const result = { ...node };
  const fields = getNodeFields(schema);

  for (const [fieldName, field] of Object.entries(fields)) {
    if (result[fieldName] === undefined && field.default !== undefined) {
      result[fieldName] = field.default;
    }
  }

  return result;
}

/**
 * Apply default values from schema to a link
 */
export function applyLinkDefaults(schema: Schema, link: Record<string, unknown>): Record<string, unknown> {
  const result = { ...link };
  const fields = getLinkFields(schema);

  for (const [fieldName, field] of Object.entries(fields)) {
    if (result[fieldName] === undefined && field.default !== undefined) {
      result[fieldName] = field.default;
    }
  }

  return result;
}
