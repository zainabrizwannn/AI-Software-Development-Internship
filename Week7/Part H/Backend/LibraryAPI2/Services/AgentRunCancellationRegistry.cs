using System.Collections.Concurrent;

namespace LibraryAPI.Services
{
    public class AgentRunCancellationRegistry
    {
        private readonly ConcurrentDictionary<
            string,
            CancellationTokenSource
        > _runs = new();


        public CancellationTokenSource Register(
            string threadId
        )
        {
            var cts =
                new CancellationTokenSource();

            _runs[threadId] =
                cts;

            return cts;
        }


        public bool Cancel(
            string threadId
        )
        {
            if (
                !_runs.TryGetValue(
                    threadId,
                    out var cts
                )
            )
            {
                return false;
            }

            if (!cts.IsCancellationRequested)
            {
                cts.Cancel();
            }

            return true;
        }


        public void Remove(
            string threadId
        )
        {
            if (
                _runs.TryRemove(
                    threadId,
                    out var cts
                )
            )
            {
                cts.Dispose();
            }
        }
    }
}