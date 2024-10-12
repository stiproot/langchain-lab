```mermaid
C4Context
    title System Context Diagram for Meeting Transcript to Azure DevOps Work Items

    Person(user, "User", "Uploads meeting transcript and approves work item hierarchy.")
    
    System(webApp, "Web Application", "Processes transcript and interacts with Azure DevOps.")
    System_Ext(azureDevOps, "Azure DevOps", "Creates work items based on approved hierarchy.")
    SystemDb(database, "NoSQL Database", "Stores transcripts and related data.")
    SystemBoundary(dapr, "Dapr", "Microservices communication framework.")

    Rel(user, webApp, "Uploads transcript and approves hierarchy")
    Rel(webApp, azureDevOps, "Creates work items")
    Rel(webApp, database, "Stores and retrieves data")
    Rel(webApp, dapr, "Uses for microservices communication")
```