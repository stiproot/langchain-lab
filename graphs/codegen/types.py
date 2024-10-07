from enum import Enum


class C4_DIAGRAM_TYPES(Enum):
    CONTEXT = "C4 System Context Diagram"
    CONTAINER = "C4 Container Diagram"
    COMPONENT = "C4 Component Diagram"
    CODE = "C4 Code Diagram"


class C4_COLLECTIONS(Enum):
    CONTEXT = "c4-system-context-diagram"
    CONTAINER = "c4-container-diagram"
    COMPONENT = "c4-component-diagram"
    CODE = "c4-code-diagram"
