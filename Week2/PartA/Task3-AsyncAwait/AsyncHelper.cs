public class AsyncHelper
{
    public async Task<string> GetMessageAsync()
    {
        await Task.Delay(2000);

        return "Task Completed";
    }
}