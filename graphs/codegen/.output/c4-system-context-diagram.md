```mermaid
C4Context
    title System Context Diagram for Meeting Transcript to Azure DevOps Work Items

    Person(user, "User", "A user who wants to translate meeting transcripts into Azure DevOps Work Items.")

    System(webApp, "Web Application", "Allows users to upload transcripts and create work item hierarchies.")
    System_Ext(azureDevOps, "Azure DevOps", "Platform for managing development projects.")
    SystemDb(database, "NoSQL Database", "Stores transcripts and work item data.")

    Rel(user, webApp, "Uploads transcripts and approves work item hierarchy.")
    Rel(webApp, azureDevOps, "Creates work items based on approved hierarchy.")
    Rel(webApp, database, "Stores and retrieves transcript and work item data.")

    UpdateElementStyle(webApp, $backgroundColor="lightblue", $borderColor="blue")
    UpdateElementStyle(azureDevOps, $backgroundColor="lightgray", $borderColor="gray")
    UpdateElementStyle(database, $backgroundColor="lightyellow", $borderColor="orange")
```

### Explanation

- **User**: The person who interacts with the system to translate meeting transcripts into Azure DevOps Work Items.
- **Web Application**: The main system that allows users to upload transcripts, build work item hierarchies, and create work items in Azure DevOps.
- **Azure DevOps**: An external system where the work items are created and managed.
- **NoSQL Database**: Used to store transcripts and work item data, supporting horizontal scaling and large data storage.

The web application is built using Vue.js for the frontend and Python for the backend, utilizing Dapr for microservices to ensure scalability and performance.