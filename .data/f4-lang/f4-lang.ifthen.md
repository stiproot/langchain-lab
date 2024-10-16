# F4 Lang

## If Then Examples

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
}
```