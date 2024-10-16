using TaskTree;

public class WebApplication
{
    public static void Main()
    {
        var stateManager = new StateManager();

        var webAppBoundary = stateManager
            .Container("Web Application")
            .Component("Uploader Component", "Vue.js", "Handles file uploads and user interactions")
            .Component("Viewer Component", "Vue.js", "Displays work item hierarchy for approval");

        var backendBoundary = stateManager
            .Container("Backend")
            .Component("Transcript Processor", "Python", "Processes transcripts into structured data")
            .Component("Hierarchy Builder", "Python", "Builds work item hierarchy from transcript data")
            .Component("Azure DevOps Connector", "Python", "Interacts with Azure DevOps API to create work items");

        var databaseBoundary = stateManager
            .Container("Database")
            .ComponentDb("Transcript Store", "MongoDB", "Stores raw and processed transcript data")
            .ComponentDb("Work Item Store", "MongoDB", "Stores work item hierarchy data");

        var microservicesBoundary = stateManager
            .Container("Microservices")
            .Component("Transcript Service", "Python, Dapr", "Processes and converts transcripts into work items")
            .Component("Approval Service", "Python, Dapr", "Manages approval workflow for work item hierarchy")
            .Component("Azure DevOps Service", "Python, Dapr", "Interacts with Azure DevOps to create work items");

        stateManager
            .Rel("Uploader Component", "Transcript Processor", "Uploads transcripts for processing")
            .Rel("Transcript Processor", "Transcript Store", "Stores processed transcript data")
            .Rel("Hierarchy Builder", "Work Item Store", "Stores work item hierarchy")
            .Rel("Azure DevOps Connector", "Azure DevOps Service", "Sends work items for creation")
            .Rel("Approval Service", "Viewer Component", "Sends approval status");

        stateManager.Build();
    }
}
