from enum import Enum


class COLLECTION_NAMES(Enum):
    C4_SYSCONTEXT_DIAG = "c4-system-context-diagram"
    C4_CONTAINER_DIAG = "c4-container-diagram"
    C4_COMPONENT_DIAG = "c4-component-diagram"
    C4_CODE_DIAG = "c4-code-diagram"
    TASK_TREE_LIB = "task-tree-lib"


class C4_DIAGRAM_TYPES(Enum):
    C4_SYSCONTEXT_DIAG = "C4 System Context Diagram"
    C4_CONTAINER_DIAG = "C4 Container Diagram"
    C4_COMPONENT_DIAG = "C4 Component Diagram"
    C4_CODE_DIAG = "C4 Code Diagram"
