using System;
using System.Threading;
using System.Threading.Tasks;
using Xo.TaskTree;

public class MeetingTranscriptWorkflow
{
    private readonly IStateManager _stateManager;

    public MeetingTranscriptWorkflow(IStateManager stateManager)
    {
        _stateManager = stateManager;
    }

    public async Task ExecuteWorkflow(CancellationToken cancellationToken)
    {
        var workflow = _stateManager
            .RootIf<ITranscriptProcessor>()
            .Then<IHierarchyBuilder>(configure => configure.RequireResult())
            .Then<IAzureDevOpsConnector>(configure => configure.RequireResult())
            .Else<IErrorHandler>(configure => configure.RequireResult());

        var node = workflow.Build();

        var messages = await node.Resolve(cancellationToken);
        var result = messages.First().Data<bool>();

        Console.WriteLine($"Workflow executed successfully: {result}");
    }
}

public interface ITranscriptProcessor
{
    Task<bool> ProcessTranscriptAsync(string transcript);
}

public interface IHierarchyBuilder
{
    Task<bool> BuildHierarchyAsync();
}

public interface IAzureDevOpsConnector
{
    Task<bool> CreateWorkItemsAsync();
}

public interface IErrorHandler
{
    Task HandleErrorAsync();
}
