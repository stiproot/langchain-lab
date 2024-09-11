# C4 Component Diagram for Meeting Transcript to Azure DevOps Work Items

```mermaid
C4Context
    title System Context Diagram for Meeting Transcript to Azure DevOps Work Items

    Person(user, "User", "Wants to translate meeting transcripts into Azure DevOps Work Items")
    System(webApp, "Web Application", "Allows users to upload transcripts and manage work items")

    user -> webApp : "Uploads transcript and manages work items"

C4Container
    title Container Diagram for Meeting Transcript to Azure DevOps Work Items

    Container(webApp, "Web Application", "Vue.js", "Frontend for uploading transcripts and managing work items")
    Container(api, "API Gateway", "Python", "Handles requests and routes them to appropriate services")
    Container(transcriptService, "Transcript Service", "Python", "Processes transcripts into work item hierarchy")
    Container(workItemService, "Work Item Service", "Python", "Creates work items in Azure DevOps")
    ContainerDb(database, "NoSQL Database", "Stores transcripts and work item data")
    System_Ext(azureDevOps, "Azure DevOps", "External system for work item management")

    webApp -> api : "Sends transcript and requests work item hierarchy"
    api -> transcriptService : "Processes transcript"
    transcriptService -> database : "Stores processed data"
    api -> workItemService : "Requests work item creation"
    workItemService -> azureDevOps : "Creates work items"
    workItemService -> database : "Stores work item data"

C4Component
    title Component Diagram for Meeting Transcript to Azure DevOps Work Items

    Component(webApp, "Web Application", "Vue.js", "Frontend for user interaction")
    Component(api, "API Gateway", "Python", "Routes requests to services")
    Component(transcriptProcessor, "Transcript Processor", "Python", "Converts transcripts into work item hierarchy")
    Component(workItemCreator, "Work Item Creator", "Python", "Interacts with Azure DevOps to create work items")
    ComponentDb(transcriptDb, "Transcript Database", "NoSQL", "Stores transcripts and hierarchies")
    ComponentDb(workItemDb, "Work Item Database", "NoSQL", "Stores work item data")

    webApp -> api : "HTTP Request"
    api -> transcriptProcessor : "Processes transcript"
    transcriptProcessor -> transcriptDb : "Stores hierarchy"
    api -> workItemCreator : "Creates work items"
    workItemCreator -> azureDevOps : "API Call"
    workItemCreator -> workItemDb : "Stores work item data"
```

## Explanation

- **User**: Interacts with the web application to upload transcripts and manage work items.
- **Web Application**: Built with Vue.js, it serves as the frontend interface for users.
- **API Gateway**: A Python-based service that routes requests to the appropriate backend services.
- **Transcript Service**: Processes the uploaded transcripts into a hierarchical structure of work items.
- **Work Item Service**: Communicates with Azure DevOps to create work items based on the processed hierarchy.
- **NoSQL Database**: Stores both the raw transcripts and the resulting work item data.
- **Azure DevOps**: External system where the work items are created and managed.

This architecture supports scalability, high throughput, and efficient data storage, aligning with the technical requirements provided.