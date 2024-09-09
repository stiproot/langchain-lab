```mermaid
C4Context
    title System Context Diagram

    Person(user, "User", "Wants to translate meeting transcripts into Azure DevOps Work Items")

    System_Boundary(webApp, "Web Application") {
        Container(frontend, "Frontend", "Vue.js", "Allows users to upload transcripts and approve work item hierarchy")
        Container_Backend(backend, "Backend", "Python", "Processes transcripts and interacts with Azure DevOps")
        ContainerDb(database, "Database", "NoSQL", "Stores transcripts and work item data")
    }

    System_Ext(azureDevOps, "Azure DevOps", "External system for managing work items")

    Rel(user, frontend, "Uploads transcripts and approves hierarchy")
    Rel(frontend, backend, "Sends transcripts for processing")
    Rel(backend, database, "Stores and retrieves data")
    Rel(backend, azureDevOps, "Creates work items")
    Rel(backend, frontend, "Sends work item hierarchy for approval")
```