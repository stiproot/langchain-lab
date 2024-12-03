using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.DependencyInjection;
using Xo.TaskTree;

namespace XxxAPI
{
    class Program
    {
        static async Task Main(string[] args)
        {
            var serviceCollection = new ServiceCollection();
            ConfigureServices(serviceCollection);

            var serviceProvider = serviceCollection.BuildServiceProvider();
            var stateManager = serviceProvider.GetService<IStateManager>();

            var cancellationToken = new CancellationToken();

            var workflow = stateManager
                .RootIf<ITranscriptProcessor>()
                .Then<IHierarchyBuilder>(
                    configure => configure.MatchArg("<<transcript-data>>"),
                    then => then.Then<IWorkItemCreator>(configure: c => c.RequireResult())
                )
                .Else<IApiGateway>(c => c.MatchArg<IDaprIntegration>(c => c.MatchArg("<<api-data>>")));

            var node = workflow.Build();

            var msgs = await node.Resolve(cancellationToken);
            var msg = msgs.First();
            var result = msg.Data<bool>();

            Console.WriteLine($"Workflow execution result: {result}");
        }

        private static void ConfigureServices(IServiceCollection services)
        {
            services.AddSingleton<IStateManager, StateManager>();
            services.AddTransient<ITranscriptProcessor, TranscriptProcessor>();
            services.AddTransient<IHierarchyBuilder, HierarchyBuilder>();
            services.AddTransient<IWorkItemCreator, WorkItemCreator>();
            services.AddTransient<IApiGateway, ApiGateway>();
            services.AddTransient<IDaprIntegration, DaprIntegration>();
        }
    }

    public interface ITranscriptProcessor
    {
        Task ProcessTranscriptAsync(string transcriptData);
    }

    public interface IHierarchyBuilder
    {
        Task BuildHierarchyAsync(string processedData);
    }

    public interface IWorkItemCreator
    {
        Task CreateWorkItemsAsync(string hierarchyData);
    }

    public interface IApiGateway
    {
        Task HandleApiRequestAsync(string apiData);
    }

    public interface IDaprIntegration
    {
        Task IntegrateWithDaprAsync(string daprData);
    }

    public class TranscriptProcessor : ITranscriptProcessor
    {
        public Task ProcessTranscriptAsync(string transcriptData)
        {
            // Implementation here
            return Task.CompletedTask;
        }
    }

    public class HierarchyBuilder : IHierarchyBuilder
    {
        public Task BuildHierarchyAsync(string processedData)
        {
            // Implementation here
            return Task.CompletedTask;
        }
    }

    public class WorkItemCreator : IWorkItemCreator
    {
        public Task CreateWorkItemsAsync(string hierarchyData)
        {
            // Implementation here
            return Task.CompletedTask;
        }
    }

    public class ApiGateway : IApiGateway
    {
        public Task HandleApiRequestAsync(string apiData)
        {
            // Implementation here
            return Task.CompletedTask;
        }
    }

    public class DaprIntegration : IDaprIntegration
    {
        public Task IntegrateWithDaprAsync(string daprData)
        {
            // Implementation here
            return Task.CompletedTask;
        }
    }
}
