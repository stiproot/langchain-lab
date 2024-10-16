using F4Lang;

public class WorkflowBuilder
{
    private readonly IStateManager _stateManager;

    public WorkflowBuilder(IStateManager stateManager)
    {
        _stateManager = stateManager;
    }

    public INode BuildWorkflow()
    {
        var workflow = _stateManager
            .RootIf<IUploaderComponent>()
            .Then<ITranscriptProcessor>(configure => configure.MatchArg("transcript"))
            .Then<IHierarchyBuilder>(configure => configure.RequireResult())
            .Then<IApprovalService>(configure => configure.RequireResult())
            .Then<IDevOpsService>(configure => configure.RequireResult())
            .Else<IErrorHandler>(configure => configure.MatchArg("error"));

        return workflow.Build();
    }
}

// Interfaces for the components
public interface IUploaderComponent
{
    bool Upload(string file);
}

public interface ITranscriptProcessor
{
    Task<string> ProcessTranscriptAsync(string transcript);
}

public interface IHierarchyBuilder
{
    Task<bool> BuildHierarchyAsync(string data);
}

public interface IApprovalService
{
    Task<bool> ApproveAsync(string hierarchy);
}

public interface IDevOpsService
{
    Task<bool> CreateWorkItemsAsync(string approvedHierarchy);
}

public interface IErrorHandler
{
    void HandleError(string error);
}
