# TaskTree

## Summary
TaskTree is a .NET library that allows you to build complex workflows.

## Usage
```bash
dotnet add package Xo.TaskTree
```

## Examples
The most important abstraction is the `IStateManager`. It allows for the building of workflows.

```cs
public class StateManagerTests
{
	private static CancellationToken NewCancellationToken() => new CancellationToken();
	private readonly IStateManager _stateManager;

	public StateManagerTests(IStateManager stateManager) => this._stateManager = stateManager;

	[Fact]
	public async Task IF_THEN_then()
	{
		var cancellationToken = NewCancellationToken();

		var mn = this._stateManager
			.RootIf<IY_OutConstBool_SyncService>()
			.Then<IY_InStr_OutConstInt_AsyncService>(
				configure => configure.MatchArg("<<arg-1>>"),
				then => then.Then<IY_InInt_OutBool_SyncService>(configure: c => c.RequireResult())
			)
			.Else<IY_InStr_AsyncService>(c => c.MatchArg<IY_InStr_OutConstStr_AsyncService>(c => c.MatchArg("<<arg-2>>")));
		
		var n = mn.Build();

		var msgs = await n.Resolve(cancellationToken);
		var msg = msgs.First(); 
		var d = msg.Data<bool>(); 

		Assert.True(d);
	}

	[Fact]
	public async Task IF_not_null_THEN_then()
	{
		var cancellationToken = NewCancellationToken();

		var mn = this._stateManager
			.IsNotNull<IY_OutObj_SyncService>()
			.Then<IY_InObj_OutConstInt_AsyncService>(c => c.AddArg(new object(), "arg1"))
			.Else<IY_InStr_AsyncService>(c => c.AddArg("<<args>>", "args3"));
		
		var n = mn.Build();

		var msgs = await n.Resolve(cancellationToken);
		var msg = msgs.First(); 
		var d = msg.Data<int>(); 

		Assert.Equal(1, d);
	}

	[Fact]
	public async Task IF_not_null_THEN_requires_result()
	{
		var cancellationToken = NewCancellationToken();

		var mn = this._stateManager
			.IsNotNull<IY_OutObj_SyncService>()
			.Then<IY_InObj_OutConstInt_AsyncService>(c => c.RequireResult())
			.Else<IY_InStr_AsyncService>(c => c.AddArg("<<args>>", "args3"));
		
		var n = mn.Build();

		var msgs = await n.Resolve(cancellationToken);
		var msg = msgs.First(); 
		var d = msg.Data<int>(); 

		Assert.Equal(1, d);
	}

	[Fact]
	public async Task IF_then_ELSE_args()
	{
		var cancellationToken = NewCancellationToken();

		var mn = this._stateManager
			.RootIf<IY_OutConstFalseBool_SyncService>()
			.Then<IY_InStr_AsyncService>(configure => configure.MatchArg("<<arg-1>>"))
			.Else<IY_InStr_OutConstInt_AsyncService>(c => c.MatchArg<IY_InStr_OutConstStr_AsyncService>(c => c.MatchArg("<<arg-2>>")));
		
		var n = mn.Build();

		var msgs = await n.Resolve(cancellationToken);
		var msg = msgs.First(); 
		var d = msg.Data<int>(); 

		Assert.Equal(1, d);
	}

	[Fact]
	public async Task IF_THEN_if_then()
	{
		var cancellationToken = NewCancellationToken();

		var mn = this._stateManager
			.RootIf<IY_OutConstBool_SyncService>()
			.Then<IY_InStr_OutConstInt_AsyncService>(
				configure => configure.MatchArg("<<arg>>"),
				then => then.If<IY_InInt_OutBool_SyncService>(configure: c => c.RequireResult()).Then<IY_InBool_OutConstStrIfFalseElseDynamicStr_AsyncService>(c => c.RequireResult()).Else<IY_AsyncService>()
			)
			.Else<IY_InStr_AsyncService>(c => c.MatchArg<IY_InStr_OutConstStr_AsyncService>(c => c.MatchArg("<<arg>>")));

		var n = mn.Build();

		var msgs = await n.Resolve(cancellationToken);
		var msg = msgs.First(); 
		var d = msg.Data<string>(); 

		Assert.NotNull(d);
		Assert.IsType<Guid>(Guid.Parse(d));
	}

	[Fact]
	public async Task IF_ELSE_args()
	{
		var cancellationToken = NewCancellationToken();

		var mn = this._stateManager
			.RootIf<IY_OutConstFalseBool_SyncService>()
			.Else<IY_InStr_OutConstInt_AsyncService>(c => c.MatchArg<IY_InStr_OutConstStr_AsyncService>(c => c.MatchArg("<<arg>>")));

		var n = mn.Build();

		var msgs = await n.Resolve(cancellationToken);
		var msg = msgs.First(); 
		var d = msg.Data<int>(); 

		Assert.Equal(1, d);
	}

	[Fact]
	public async Task promised_ARGS_ARGS()
	{
		var cancellationToken = NewCancellationToken();

		var mn = this._stateManager
			.Root<IY_InBoolStr_OutConstInt_AsyncService>(c => 
				c
					.MatchArg<IY_OutConstBool_SyncService>()
					.MatchArg<IY_InBool_OutConstStrIfFalseElseDynamicStr_AsyncService>(c => c.MatchArg(true))
			);

		var n = mn.Build();

		var msgs = await n.Resolve(cancellationToken);
		var msg = msgs.First(); 
		var d = msg.Data<int>(); 

		Assert.Equal(1, d);
	}

	[Fact]
	public async Task ARGS_ARGS()
	{
		var cancellationToken = NewCancellationToken();

		var mn = this._stateManager
			.Root<IY_InBoolStr_OutConstInt_AsyncService>(c => 
				c
					.MatchArg("<<args>>")
					.MatchArg(true)
			);

		var n = mn.Build();

		var msgs = await n.Resolve(cancellationToken);
		var msg = msgs.First(); 
		var d = msg.Data<int>(); 

		Assert.Equal(1, d);
	}

	[Fact]
	public async Task KEY_HASH()
	{
		var cancellationToken = NewCancellationToken();

		var mn = this._stateManager
			.Root<IY_OutConstBool_SyncService>()
			.Key<IY_InBool_OutConstStr_AsyncService>(c => c.RequireResult())
			.Hash<IY_AsyncService, IY_InBoolStr_OutConstInt_AsyncService>(
				c => c.Key("key-a"),
				c => c.MatchArg(true).MatchArg("<<arg>>").Key("<<str>>")
			);

		var n = mn.Build();

		var msgs = await n.Resolve(cancellationToken);
		var msg = msgs.First(); 
		var d = msg.Data<int>(); 

		Assert.Equal(1, d);
	}

	[Fact]
	public async Task KEY_HASH_THEN()
	{
		var cancellationToken = NewCancellationToken();

		var mn = this._stateManager
			.Root<IY_OutConstBool_SyncService>()
			.Key<IY_InBool_OutConstStr_AsyncService>(c => c.RequireResult())
			.Hash<IY_InBoolStr_OutConstInt_AsyncService, IY_AsyncService>(
				c => c.MatchArg(true).MatchArg("<<arg>>").Key("<<str>>"),
				c => c.Key("key-a"),
				then => then.Then<IY_InStr_OutConstInt_AsyncService>(c => c.MatchArg("<<arg>>"))
			);

		var n = mn.Build();

		var msgs = await n.Resolve(cancellationToken);
		var msg = msgs.First(); 
		var d = msg.Data<int>(); 

		Assert.Equal(1, d);
	}

	[Fact]
	public async Task PATH_two_nodes()
	{
		var cancellationToken = NewCancellationToken();

		var mn = this._stateManager
			.Root<IY_OutConstBool_SyncService>()
			.Path<IY_InBool_OutConstStr_AsyncService, IY_InStr_OutConstInt_AsyncService>(
				c => c.RequireResult(),
				c => c.RequireResult()
			);

		var n = mn.Build();

		var msgs = await n.Resolve(cancellationToken);
		var msg = msgs.First(); 
		var d = msg.Data<int>(); 

		Assert.Equal(1, d);
	}

	[Fact]
	public async Task PATH_three_nodes()
	{
		var cancellationToken = NewCancellationToken();

		var mn = this._stateManager
			.Root<IY_OutConstBool_SyncService>()
			.Path<IY_InBool_OutConstStr_AsyncService, IY_InStr_OutConstInt_AsyncService, IY_InInt_OutConstInt_AsyncService>(
				c => c.RequireResult(),
				c => c.RequireResult(),
				c => c.RequireResult()
			);

		var n = mn.Build();

		var msgs = await n.Resolve(cancellationToken);
		var msg = msgs.First(); 
		var d = msg.Data<int>(); 

		Assert.Equal(1, d);
	}

	[Fact]
	public async Task PreProcess()
	{
		var cancellationToken = NewCancellationToken();

		var mn = this._stateManager
			.Root<IY_OutBool_ConfigurableSyncService>(
				configure => configure
					.PreProcess(c => (c as IY_OutBool_ConfigurableSyncService)!.Configure(false))
			);

		var n = mn.Build();

		var msgs = await n.Resolve(cancellationToken);
		var msg = msgs.First(); 
		var d = msg.Data<bool>(); 

		Assert.False(d);
	}
}
```