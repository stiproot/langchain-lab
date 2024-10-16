```mermaid
C4Context
    title System Context Diagram for Meeting Transcript to Azure DevOps Work Items

    Person(user, "User", "Wants to translate meeting transcripts into Azure DevOps Work Items.")

    System(webApp, "Web Application", "Allows users to upload transcripts and manage work items.")

    System_Ext(azureDevOps, "Azure DevOps", "Platform for managing work items.")

    System_Ext(noSqlDb, "NoSQL Database", "Stores transcript data and work item hierarchy.")

    System_Ext(dapr, "Dapr", "Microservices framework for distributed systems.")

    System_Ext(frontend, "Vue.js Frontend", "User interface for the web application.")

    System_Ext(backend, "Python Backend", "Handles business logic and processing.")

    Rel(user, webApp, "Uploads transcript and manages work items.")
    Rel(webApp, azureDevOps, "Creates work items upon approval.")
    Rel(webApp, noSqlDb, "Stores and retrieves transcript data.")
    Rel(webApp, dapr, "Utilizes for microservices communication.")
    Rel(webApp, frontend, "Provides user interface.")
    Rel(webApp, backend, "Processes business logic.")
```

### Explanation

- **User**: The person who wants to translate meeting transcripts into Azure DevOps Work Items.
- **Web Application**: The main system where users upload transcripts and manage work items.
- **Azure DevOps**: External system where work items are created and managed.
- **NoSQL Database**: Used to store transcript data and work item hierarchy.
- **Dapr**: Used for microservices communication within the system.
- **Vue.js Frontend**: Provides the user interface for the web application.
- **Python Backend**: Handles the business logic and processing of transcripts.