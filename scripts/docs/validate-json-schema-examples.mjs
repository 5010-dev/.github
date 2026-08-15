#!/usr/bin/env node

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { resolve } from "node:path";

import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";

const scriptDirectory = fileURLToPath(new URL(".", import.meta.url));
const repositoryRoot = resolve(scriptDirectory, "../..");
const schemaRoot = resolve(
  repositoryRoot,
  "docs/standards/release-versioning/schemas",
);

const validations = [
  {
    schema: "protected-package-tag-profile-v1.schema.json",
    documents: ["examples/protected-package-tag-profile-v1.valid.json"],
  },
  {
    schema: "package-release-intent-v1.schema.json",
    documents: ["examples/package-release-intent-v1.valid.json"],
  },
  {
    schema: "package-release-recovery-intent-v1.schema.json",
    documents: ["examples/package-release-recovery-intent-v1.valid.json"],
  },
  {
    schema: "package-release-tag-only-completion-intent-v1.schema.json",
    documents: [
      "examples/package-release-tag-only-completion-intent-v1.valid.json",
    ],
  },
  {
    schema:
      "package-release-tag-only-completion-recovery-intent-v1.schema.json",
    documents: [
      "examples/package-release-tag-only-completion-recovery-intent-v1.valid.json",
      "../validation/fixtures/2026-08-15-core-tag-only-completion-recovery-intent.valid.json",
    ],
  },
];

function parseJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

let documentCount = 0;
for (const validation of validations) {
  const schemaPath = resolve(schemaRoot, validation.schema);
  const ajv = new Ajv2020({
    allErrors: true,
    strict: true,
    strictTypes: false,
  });
  addFormats(ajv);
  const validate = ajv.compile(parseJson(schemaPath));

  for (const relativeDocument of validation.documents) {
    const documentPath = resolve(schemaRoot, relativeDocument);
    const valid = validate(parseJson(documentPath));
    if (!valid) {
      const details = ajv.errorsText(validate.errors, {
        dataVar: relativeDocument,
        separator: "\n",
      });
      throw new Error(
        `${relativeDocument} does not conform to ${validation.schema}:\n${details}`,
      );
    }
    documentCount += 1;
  }
}

console.log(
  `release-versioning JSON Schema validation: OK (${documentCount} documents, ${validations.length} schemas)`,
);
