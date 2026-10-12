using System.Net.Http.Json;
using LibraryAPI.DTOs;

namespace LibraryAPI.Clients
{
    public class AiServiceClient : IAiServiceClient
    {
        private readonly HttpClient _httpClient;

        public AiServiceClient(
            HttpClient httpClient
        )
        {
            _httpClient = httpClient;
        }

        public async Task<AiAskResponse> AskAsync(
            string question,
            string sessionId
        )
        {
            var request = new
            {
                question = question,
                session_id = sessionId
            };

            var response =
                await _httpClient.PostAsJsonAsync(
                    "/ask",
                    request
                );

            response.EnsureSuccessStatusCode();

            var result =
                await response.Content
                    .ReadFromJsonAsync<AiAskResponse>();

            if (result == null)
            {
                throw new InvalidOperationException(
                    "AI service returned an empty response."
                );
            }

            return result;
        }
    }
}