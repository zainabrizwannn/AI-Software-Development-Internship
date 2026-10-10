using LibraryAPI.Clients;
using LibraryAPI.DTOs;
using Microsoft.AspNetCore.Mvc;
using Polly.CircuitBreaker;
using Polly.Timeout;
using System.Net.Http.Json;

namespace LibraryAPI.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AssistantController : ControllerBase
    {
        private readonly IAiServiceClient _aiServiceClient;
        private readonly IHttpClientFactory _httpClientFactory;

        public AssistantController(
            IAiServiceClient aiServiceClient,
            IHttpClientFactory httpClientFactory)
        {
            _aiServiceClient = aiServiceClient;
            _httpClientFactory = httpClientFactory;
        }


        [HttpPost("ask")]
        public async Task<IActionResult> Ask(
            AskDto dto)
        {
            if (
                string.IsNullOrWhiteSpace(
                    dto.Question
                )
            )
            {
                return BadRequest(
                    new
                    {
                        message =
                            "Question is required."
                    }
                );
            }

            try
            {
                var result =
                    await _aiServiceClient
                        .AskAsync(
                            dto.Question,
                            dto.SessionId
                        );

                return Ok(result);
            }
            catch (BrokenCircuitException)
            {
                return StatusCode(
                    503,
                    new
                    {
                        message =
                            "The AI assistant is temporarily unavailable. Please try again shortly."
                    }
                );
            }
            catch (TimeoutRejectedException)
            {
                return StatusCode(
                    503,
                    new
                    {
                        message =
                            "The AI assistant took too long to respond. Please try again shortly."
                    }
                );
            }
            catch (HttpRequestException)
            {
                return StatusCode(
                    503,
                    new
                    {
                        message =
                            "The AI assistant is temporarily unavailable. Please try again shortly."
                    }
                );
            }
        }


        [HttpPost("ask/stream")]
        public async Task AskStream(
            AskDto dto,
            CancellationToken cancellationToken)
        {
            if (
                string.IsNullOrWhiteSpace(
                    dto.Question
                )
            )
            {
                Response.StatusCode = 400;

                await Response.WriteAsJsonAsync(
                    new
                    {
                        message =
                            "Question is required."
                    },
                    cancellationToken
                );

                return;
            }

            var client =
                _httpClientFactory.CreateClient(
                    "AiStreaming"
                );

            using var upstreamRequest =
                new HttpRequestMessage(
                    HttpMethod.Post,
                    "/ask/stream"
                )
                {
                    Content =
                        JsonContent.Create(
                            new
                            {
                                question =
                                    dto.Question,

                                session_id =
                                    dto.SessionId
                            }
                        )
                };

            try
            {
                using var upstreamResponse =
                    await client.SendAsync(
                        upstreamRequest,
                        HttpCompletionOption
                            .ResponseHeadersRead,
                        cancellationToken
                    );

                if (
                    !upstreamResponse
                        .IsSuccessStatusCode
                )
                {
                    Response.StatusCode = 503;

                    await Response.WriteAsJsonAsync(
                        new
                        {
                            message =
                                "The AI assistant is temporarily unavailable. Please try again shortly."
                        },
                        cancellationToken
                    );

                    return;
                }

                Response.ContentType =
                    "text/event-stream";

                Response.Headers.CacheControl =
                    "no-cache";

                await using var stream =
                    await upstreamResponse.Content
                        .ReadAsStreamAsync(
                            cancellationToken
                        );

                using var reader =
                    new StreamReader(
                        stream
                    );

                while (
                    !reader.EndOfStream
                )
                {
                    var line =
                        await reader.ReadLineAsync(
                            cancellationToken
                        );

                    if (
                        string.IsNullOrWhiteSpace(
                            line
                        )
                    )
                    {
                        continue;
                    }

                    await Response.WriteAsync(
                        line + "\n\n",
                        cancellationToken
                    );

                    await Response.Body
                        .FlushAsync(
                            cancellationToken
                        );
                }
            }
            catch (
                OperationCanceledException
            )
            {
                Console.WriteLine(
                    "Streaming request was cancelled."
                );
            }
            catch (
                HttpRequestException
            )
            {
                if (!Response.HasStarted)
                {
                    Response.StatusCode =
                        503;

                    await Response
                        .WriteAsJsonAsync(
                            new
                            {
                                message =
                                    "The AI assistant is temporarily unavailable. Please try again shortly."
                            },
                            CancellationToken.None
                        );
                }
            }
        }
    }
}