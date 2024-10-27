using System;
using System.Threading;
using System.Threading.Tasks;
using Xo.TaskTree;

namespace XxxAPI
{
    class Program
    {
        static async Task Main(string[] args)
        {
            var cancellationToken = new CancellationToken();
            IStateManager stateManager = new StateManager();

            var workflow = stateManager
                .RootIf<ITranscriptUploadService>()
                .Then<ITranscriptProcessingService>(
                    configure => configure.MatchArg("<<transcript>>"),
                    then => then.Then<IHierarchyApprovalService>(configure: c => c.RequireResult())
                )
                .Else<IErrorHandlingService>(c => c.MatchArg("<<error>>"));

            var node = workflow.Build();

            var msgs = await node.Resolve(cancellationToken);
            var msg = msgs.First();
            var result = msg.Data<bool>();

            Console.WriteLine($"Workflow completed with result: {result}");
        }
    }

    public interface ITranscriptUploadService
    {
        bool UploadTranscript();
    }

    public interface ITranscriptProcessingService
    {
        Task<int> ProcessTranscriptAsync(string transcript);
    }

    public interface IHierarchyApprovalService
    {
        Task<bool> ApproveHierarchyAsync(int hierarchyId);
    }

    public interface IErrorHandlingService
    {
        Task HandleErrorAsync(string error);
    }
}
