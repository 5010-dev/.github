# Platform contracts

Platform contracts define shared engineering requirements for repositories that
participate in a common runtime or delivery platform.

## ECS

- [ECS deployment contract](./ecs-deployment-contract.md)
- [ECS service delivery workflow standard](./ecs-service-delivery-workflow-standard.md)
- [ECS health and readiness profiles](./ecs-health-readiness-profiles.md)
- [ECS service contract ownership directory](./ecs-service-health-matrix.md)

Repository-local architecture links to these contracts and owns exact service
configuration, implementation, deployment commands, and conformance evidence.
Existing contract paths remain stable because participating repositories link
to them directly.
