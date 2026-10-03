using LibraryAPI.DTOs;

namespace LibraryAPI.Clients
{
    public interface IAiServiceClient
    {
        Task<AiAskResponse> AskAsync(string question);
    }
}