```mermaid
C4Context
    title System Context Diagram for Meeting Transcript to Azure DevOps Work Items

    Person(user, "User", "A user who uploads meeting transcripts and approves work item hierarchies.")
    
    System_Boundary(webApp, "Web Application") {
        System(frontend, "Frontend", "Vue.js application for uploading transcripts and displaying work item hierarchies.")
        System(backend, "Backend", "Python application for processing transcripts and interacting with Azure DevOps.")
    }

    System_Ext(azureDevOps, "Azure DevOps", "Platform for managing work items.")
    System_Ext(database, "NoSQL Database", "Stores transcripts and work item data.")
    
    Rel(user, frontend, "Uploads transcripts and approves hierarchies")
    Rel(frontend, backend, "Sends transcripts for processing")
    Rel(backend, azureDevOps, "Creates work items")
    Rel(backend, database, "Stores and retrieves data")
```

### Explanation

- **User**: Interacts with the system by uploading meeting transcripts and approving the generated work item hierarchy.
- **Web Application**: Consists of a frontend and backend.
  - **Frontend**: Built with Vue.js, it allows users to upload transcripts and view the work item hierarchy.
  - **Backend**: Developed in Python, it processes the transcripts, builds the hierarchy, and communicates with Azure DevOps.
- **Azure DevOps**: External system where the work items are created.
- **NoSQL Database**: Used to store transcripts and work item data, supporting horizontal scaling and large data storage.
