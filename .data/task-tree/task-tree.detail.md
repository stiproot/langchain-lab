# TaskTree

## Summary
TaskTree is a .NET library that allows you to build complex workflows easily.

## Important Components
### StateManager
The `StateManager` class, whic his the implementation of the `IStateManager` interface.
Using `IStateManager` allows for the building of workflows by chaining services together.

## Examples

Given the following test services:

```cs
// Test service, consisting of single method that returns a bool.
public interface IY_OutConstBool_SyncService 
{ 
	bool GetBool(); 
}

// Test service, consisting of single async method that accepts a single argument of type string and returning an int.
public interface IY_InStr_OutConstInt_AsyncService 
{ 
	Task<int> GetConstIntAsync(string args); 
}

// Test service, consisting of single async void method that accepts a single argument of type string.
public interface IY_InStr_AsyncService 
{ 
	Task ProcessStrAsync(string args3); 
}

// Test service, consisting of single async method that accepts a single argument of type string and returns a string.
public interface IY_InStr_OutConstStr_AsyncService
{
	Task<string> GetConstStrAsync(string arg1);
}

// Test service, consisting of single async method that accepts a single argument of type string.
public interface IY_InStr_AsyncService
{ 
	Task ProcessStrAsync(string args3); 
}
```

Using the `StateManager` class, we can build a workflow out of our test services: 

```cs
CancellationToken cancellationToken = new CancellationToken();
IStateManager stateManager = new StateManager();

var metaNode = stateManager
	.RootIf<IY_OutConstBool_SyncService>()
	.Then<IY_InStr_OutConstInt_AsyncService>(
		configure => configure.MatchArg("<<arg-1>>"),
		then => then.Then<IY_InInt_OutBool_SyncService>(configure: c => c.RequireResult())
	)
	.Else<IY_InStr_AsyncService>(c => c.MatchArg<IY_InStr_OutConstStr_AsyncService>(c => c.MatchArg("<<arg-2>>")));

var node = metaNode.Build();

var msgs = await node.Resolve(cancellationToken);
var msg = msgs.First(); 
var d = msg.Data<bool>(); 
```

Let's examine the above code in detail.

1. **Meta workflow construction**

The `StateManager` builds a meta workflow, out of our services, using "meta nodes".
`StateManager`'s `RootIf<IY_OutConstBool_SyncService>()` method constructs a meta node around `IY_OutConstBool_SyncService` (root node).
`StateManager`'s `Then<IY_InStr_OutConstInt_AsyncService>` method constructs a meta node around `IY_InStr_OutConstInt_AsyncService` (then node).
`StateManager`'s `Else<IY_InStr_AsyncService>` method constructs a meta node around `IY_InStr_AsyncService` (else node).

`StateManager` allows nested meta nodes to be added to a meta node.
A meta node around `IY_InInt_OutBool_SyncService` (nested then node).
A meta node around `IY_InStr_OutConstStr_AsyncService` (argument node for `IY_InStr_AsyncService`).

What this flow looks like when executing?
If the output of `IY_OutConstBool_SyncService` is true, meaning the value of the method `IY_OutConstBool_SyncService.GetBool()` is true, then `IY_InStr_OutConstInt_AsyncService.GetConstIntAsync(string)` is executed, otherwise the `IY_InStr_AsyncService.ProcessStrAsync(string)` is executed.
If `IY_InStr_OutConstInt_AsyncService.GetConstIntAsync(string)` executes, then `IY_InInt_OutBool_SyncService.GetBool(int)`.
`IY_InStr_OutConstStr_AsyncService.GetConstStrAsync(string)` is an argument for `IY_InStr_AsyncService.ProcessStrAsync(string)`, which means it return value will be used as an argument for `IY_InStr_AsyncService.ProcessStrAsync(string)`.

2. **Workflow construction**

The `StateManager` builds the concrete workflow, out of the meta workflow. Meta nodes get translated to nodes, which are components that can be resolved.

This process uses .NET's built in dependency injection framework to get the concrete implementations of the interfaces in each meta node. This is done by using `ServiceProvider`.

`IStateManager.Build()` method returns the root node of the constructed workflow.

3. **Workflow execution**

The root node can be executed using the `Resolve` method.

Each node in the workflow is an implementation of the `INode` interface.
The `Resove` method signature is `Task<IMsg[]> Resolve(CancellationToken cancellationToken);`.