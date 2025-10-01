# Shared Resources

This directory contains shared utilities, components, and resources that can be used across multiple projects in this monorepo.

## Structure

```
shared/
├── utilities/           # Common utility functions
├── components/         # Reusable UI components
├── configs/           # Shared configuration files
├── types/             # Common TypeScript types
└── docs/              # Shared documentation
```

## Usage

Projects can import shared resources using relative paths:

```typescript
// From a project's frontend
import { CommonComponent } from '../../../shared/components/CommonComponent'
import { utilityFunction } from '../../../shared/utilities/helpers'
```

## Contributing

When adding shared resources:
1. Ensure they are truly reusable across projects
2. Document usage and dependencies
3. Follow consistent naming conventions
4. Include TypeScript types where applicable
