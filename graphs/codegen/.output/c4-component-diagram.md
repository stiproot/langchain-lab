```mermaid
C4Component

title Component Diagram for Meeting Transcript to Azure DevOps Work Items

Container_Boundary(webAppBoundary, "Web Application Boundary") {
    Component(frontendUploader, "Uploader Component", "Vue.js", "Handles transcript uploads")
    Component(frontendViewer, "Viewer Component", "Vue.js", "Displays work item hierarchy")
    
    Rel(frontendUploader, frontendViewer, "Passes uploaded data")
}

Container_Boundary(backendBoundary, "Backend Boundary") {
    Component(transcriptProcessor, "Transcript Processor", "Python", "Processes transcripts into work item hierarchy")
    Component(azureDevOpsIntegrator, "Azure DevOps Integrator", "Python", "Creates work items in Azure DevOps")
    
    Rel(transcriptProcessor, azureDevOpsIntegrator, "Sends hierarchy for approval")
}

Container_Boundary(databaseBoundary, "Database Boundary") {
    Component(transcriptStorage, "Transcript Storage", "NoSQL", "Stores raw and processed transcripts")
    Component(workItemStorage, "Work Item Storage", "NoSQL", "Stores work item data")
    
    Rel(transcriptProcessor, transcriptStorage, "Stores processed data")
    Rel(azureDevOpsIntegrator, workItemStorage, "Stores work item data")
}

Container_Boundary(microservicesBoundary, "Microservices Boundary") {
    Component(transcriptServiceComponent, "Transcript Service Component", "Python", "Processes transcripts")
    Component(azureDevOpsServiceComponent, "Azure DevOps Service Component", "Python", "Interacts with Azure DevOps")
    
    Rel(transcriptServiceComponent, azureDevOpsServiceComponent, "Sends work item hierarchy")
}

System_Boundary(daprBoundary, "Dapr Boundary") {
    Component(daprComponent, "Dapr Component", "Microservices Communication", "Facilitates communication between microservices")
    
    Rel(daprComponent, transcriptServiceComponent, "Facilitates communication")
    Rel(daprComponent, azureDevOpsServiceComponent, "Facilitates communication")
}

Rel(user, frontendUploader, "Uploads transcripts")
Rel(frontendViewer, user, "Displays hierarchy")
Rel(frontendUploader, transcriptProcessor, "Sends transcript data")
Rel(azureDevOpsIntegrator, daprComponent, "Uses for communication")
```