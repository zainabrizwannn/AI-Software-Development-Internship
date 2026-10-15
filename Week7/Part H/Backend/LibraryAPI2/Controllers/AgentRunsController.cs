using System.Net.Http.Json;
using System.Security.Claims;
using System.Text.Json;
using LibraryAPI.Data;
using LibraryAPI.Dtos;
using LibraryAPI.Models;
using LibraryAPI.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.RateLimiting;
using Microsoft.EntityFrameworkCore;

namespace LibraryAPI.Controllers
{
    [ApiController]
    [Authorize]
    [EnableRateLimiting("assistant")]
    [Route("api/assistant/agent/runs")]
    public class AgentRunsController : ControllerBase
    {
        private readonly LibraryDbContext _db;
        private readonly IHttpClientFactory _httpClientFactory;
        private readonly IConfiguration _configuration;
        private readonly AgentRunCancellationRegistry _cancellationRegistry;

        public AgentRunsController(
            LibraryDbContext db,
            IHttpClientFactory httpClientFactory,
            IConfiguration configuration,
            AgentRunCancellationRegistry cancellationRegistry
        )
        {
            _db = db;
            _httpClientFactory = httpClientFactory;
            _configuration = configuration;
            _cancellationRegistry = cancellationRegistry;
        }

        // =================================================
        // CURRENT USER
        // =================================================

        private string? GetCurrentUserId()
        {
            return User.FindFirstValue(
                ClaimTypes.NameIdentifier
            );
        }

        // =================================================
        // FORWARDED JWT
        // =================================================

        private string? GetAuthorizationHeader()
        {
            return Request
                .Headers
                .Authorization
                .FirstOrDefault();
        }

        // =================================================
        // SERVICE KEY
        // =================================================

        private string GetServiceKey()
        {
            var key =
                _configuration[
                    "AgentService:ServiceKey"
                ];

            if (
                string.IsNullOrWhiteSpace(
                    key
                )
            )
            {
                throw new InvalidOperationException(
                    "AgentService service key is not configured."
                );
            }

            return key;
        }

        // =================================================
        // START RUN
        // =================================================

        [HttpPost]
        public async Task StartRun(
            [FromBody]
            StartAgentRunRequest request,
            CancellationToken cancellationToken
        )
        {
            var userId =
                GetCurrentUserId();

            if (
                string.IsNullOrWhiteSpace(
                    userId
                )
            )
            {
                Response.StatusCode =
                    StatusCodes
                        .Status401Unauthorized;

                return;
            }

            if (
                string.IsNullOrWhiteSpace(
                    request.Message
                )
            )
            {
                Response.StatusCode =
                    StatusCodes
                        .Status400BadRequest;

                return;
            }

            var threadId =
                Guid.NewGuid()
                    .ToString("N");

            // =================================================
            // REGISTER ACTIVE RUN FOR SERVER-SIDE CANCELLATION
            // =================================================

            var runCancellation =
                _cancellationRegistry
                    .Register(
                        threadId
                    );

            using var linkedCancellation =
                CancellationTokenSource
                    .CreateLinkedTokenSource(
                        cancellationToken,
                        runCancellation.Token
                    );

            var runToken =
                linkedCancellation.Token;

            var thread =
                new AgentThread
                {
                    ThreadId =
                        threadId,

                    UserId =
                        userId,

                    UserMessage =
                        request.Message,

                    Status =
                        "running",

                    CreatedAt =
                        DateTime.UtcNow,

                    UpdatedAt =
                        DateTime.UtcNow,

                    IsCancelled =
                        false
                };

            _db.AgentThreads.Add(
                thread
            );

            await _db.SaveChangesAsync(
                cancellationToken
            );

            Response.ContentType =
                "text/event-stream";

            Response.Headers.CacheControl =
                "no-cache";

            Response.Headers.Connection =
                "keep-alive";

            // First event always tells UI
            // which thread was created.
            await WriteLocalEvent(
                "step",
                new
                {
                    threadId,

                    kind =
                        "run_started",

                    name =
                        "agent",

                    summary =
                        "Agent run started."
                },
                runToken
            );

            var client =
                _httpClientFactory
                    .CreateClient(
                        "AgentService"
                    );

            using var upstreamRequest =
                new HttpRequestMessage(
                    HttpMethod.Post,
                    "/agent/runs"
                );

            upstreamRequest.Content =
                JsonContent.Create(
                    new
                    {
                        thread_id =
                            threadId,

                        message =
                            request.Message
                    }
                );

            upstreamRequest.Headers.Add(
                "X-Service-Key",
                GetServiceKey()
            );

            var auth =
                GetAuthorizationHeader();

            if (
                !string.IsNullOrWhiteSpace(
                    auth
                )
            )
            {
                upstreamRequest
                    .Headers
                    .TryAddWithoutValidation(
                        "Authorization",
                        auth
                    );
            }

            try
            {
                using var upstream =
                    await client.SendAsync(
                        upstreamRequest,

                        HttpCompletionOption
                            .ResponseHeadersRead,

                        runToken
                    );

                if (
                    !upstream
                        .IsSuccessStatusCode
                )
                {
                    thread.Status =
                        "failed";

                    thread.ErrorCode =
                        "UPSTREAM_ERROR";

                    thread.ErrorMessage =
                        "Agent service returned " +
                        $"{(int)upstream.StatusCode}.";

                    thread.UpdatedAt =
                        DateTime.UtcNow;

                    await _db
                        .SaveChangesAsync(
                            runToken
                        );

                    await WriteLocalEvent(
                        "error",
                        new
                        {
                            code =
                                thread
                                    .ErrorCode,

                            message =
                                thread
                                    .ErrorMessage,

                            retryable =
                                true
                        },
                        runToken
                    );

                    return;
                }

                await using var stream =
                    await upstream.Content
                        .ReadAsStreamAsync(
                            runToken
                        );

                using var reader =
                    new StreamReader(
                        stream
                    );

                string? eventName =
                    null;

                while (
                    !reader.EndOfStream
                )
                {
                    runToken
                        .ThrowIfCancellationRequested();

                    var line =
                        await reader
                            .ReadLineAsync(
                                runToken
                            );

                    if (
                        line == null
                    )
                    {
                        break;
                    }

                    if (
                        line.StartsWith(
                            "event:"
                        )
                    )
                    {
                        eventName =
                            line[
                                "event:".Length..
                            ]
                            .Trim();

                        continue;
                    }

                    if (
                        line.StartsWith(
                            "data:"
                        )
                    )
                    {
                        var data =
                            line[
                                "data:".Length..
                            ]
                            .Trim();

                        await PersistEvent(
                            thread,
                            eventName,
                            data,
                            runToken
                        );

                        if (
                            eventName != null
                        )
                        {
                            await Response
                                .WriteAsync(
                                    $"event: {eventName}\n",
                                    runToken
                                );
                        }

                        await Response
                            .WriteAsync(
                                $"data: {data}\n\n",
                                runToken
                            );

                        await Response
                            .Body
                            .FlushAsync(
                                runToken
                            );

                        eventName =
                            null;
                    }
                }
            }
            catch (
                OperationCanceledException
            )
            {
                // Either:
                // 1. Browser disconnected
                // 2. User pressed Cancel
                //
                // Both stop the upstream FastAPI stream.

                thread.Status =
                    "cancelled";

                thread.IsCancelled =
                    true;

                thread.PendingApprovalJson =
                    null;

                thread.UpdatedAt =
                    DateTime.UtcNow;

                try
                {
                    await _db
                        .SaveChangesAsync(
                            CancellationToken.None
                        );
                }
                catch
                {
                    // Do not allow a secondary
                    // persistence failure to crash
                    // cancellation cleanup.
                }

                Console.WriteLine(
                    $"Agent run cancelled: {threadId}"
                );
            }
            catch (
                Exception ex
            )
            {
                thread.Status =
                    "failed";

                thread.ErrorCode =
                    "AGENT_UNAVAILABLE";

                thread.ErrorMessage =
                    "The agent service is unavailable.";

                thread.UpdatedAt =
                    DateTime.UtcNow;

                await _db
                    .SaveChangesAsync(
                        CancellationToken.None
                    );

                if (
                    !HttpContext
                        .RequestAborted
                        .IsCancellationRequested
                )
                {
                    try
                    {
                        await WriteLocalEvent(
                            "error",
                            new
                            {
                                code =
                                    thread
                                        .ErrorCode,

                                message =
                                    thread
                                        .ErrorMessage,

                                retryable =
                                    true
                            },
                            CancellationToken.None
                        );
                    }
                    catch
                    {
                        // Client may already
                        // have disconnected.
                    }
                }

                Console.WriteLine(
                    $"Agent run error: {ex.Message}"
                );
            }
            finally
            {
                // Remove and dispose CTS after
                // the upstream run has ended.
                _cancellationRegistry
                    .Remove(
                        threadId
                    );
            }
        }

        // =================================================
        // PERSIST TYPED EVENT STATE
        // =================================================

        private async Task PersistEvent(
            AgentThread thread,
            string? eventName,
            string data,
            CancellationToken token
        )
        {
            switch (
                eventName
            )
            {
                case "approval_required":

                    thread.Status =
                        "pending_approval";

                    thread
                        .PendingApprovalJson =
                        data;

                    break;

                case "final":

                    thread.Status =
                        "completed";

                    thread
                        .PendingApprovalJson =
                        null;

                    try
                    {
                        using var json =
                            JsonDocument.Parse(
                                data
                            );

                        if (
                            json.RootElement
                                .TryGetProperty(
                                    "answer",
                                    out var answer
                                )
                        )
                        {
                            thread.FinalAnswer =
                                answer
                                    .GetString();
                        }
                    }
                    catch
                    {
                    }

                    break;

                case "error":

                    thread.Status =
                        "failed";

                    try
                    {
                        using var json =
                            JsonDocument.Parse(
                                data
                            );

                        if (
                            json.RootElement
                                .TryGetProperty(
                                    "code",
                                    out var code
                                )
                        )
                        {
                            thread.ErrorCode =
                                code.GetString();
                        }

                        if (
                            json.RootElement
                                .TryGetProperty(
                                    "message",
                                    out var message
                                )
                        )
                        {
                            thread.ErrorMessage =
                                message.GetString();
                        }
                    }
                    catch
                    {
                    }

                    break;
            }

            thread.UpdatedAt =
                DateTime.UtcNow;

            await _db.SaveChangesAsync(
                token
            );
        }

        // =================================================
        // LOCAL SSE EVENT
        // =================================================

        private async Task WriteLocalEvent(
            string eventName,
            object data,
            CancellationToken token
        )
        {
            var json =
                JsonSerializer.Serialize(
                    data
                );

            await Response.WriteAsync(
                $"event: {eventName}\n",
                token
            );

            await Response.WriteAsync(
                $"data: {json}\n\n",
                token
            );

            await Response.Body
                .FlushAsync(
                    token
                );
        }

        // =================================================
        // GET STATE
        // =================================================

        [HttpGet("{threadId}")]
        public async Task<IActionResult> GetRun(
            string threadId
        )
        {
            var userId =
                GetCurrentUserId();

            var thread =
                await _db.AgentThreads
                    .AsNoTracking()
                    .FirstOrDefaultAsync(
                        x =>
                            x.ThreadId ==
                                threadId
                            &&
                            x.UserId ==
                                userId
                    );

            // IMPORTANT:
            // missing thread and foreign-user thread
            // both return 404.
            if (
                thread == null
            )
            {
                return NotFound();
            }

            object?
                pendingApproval =
                    null;

            if (
                !string.IsNullOrWhiteSpace(
                    thread
                        .PendingApprovalJson
                )
            )
            {
                try
                {
                    pendingApproval =
                        JsonSerializer
                            .Deserialize<
                                object
                            >(
                                thread
                                    .PendingApprovalJson
                            );
                }
                catch
                {
                    pendingApproval =
                        null;
                }
            }

            return Ok(
                new
                {
                    threadId =
                        thread
                            .ThreadId,

                    status =
                        thread.Status,

                    userMessage =
                        thread
                            .UserMessage,

                    pendingApproval,

                    finalAnswer =
                        thread
                            .FinalAnswer,

                    errorCode =
                        thread
                            .ErrorCode,

                    errorMessage =
                        thread
                            .ErrorMessage,

                    isCancelled =
                        thread
                            .IsCancelled,

                    createdAt =
                        thread
                            .CreatedAt,

                    updatedAt =
                        thread
                            .UpdatedAt
                }
            );
        }

        // =================================================
        // RESUME
        // =================================================

        [HttpPost(
            "{threadId}/resume"
        )]
        public async Task ResumeRun(
            string threadId,
            [FromBody]
            ResumeAgentRunRequest request,
            CancellationToken cancellationToken
        )
        {
            var userId =
                GetCurrentUserId();

            var thread =
                await _db.AgentThreads
                    .FirstOrDefaultAsync(
                        x =>
                            x.ThreadId ==
                                threadId
                            &&
                            x.UserId ==
                                userId,
                        cancellationToken
                    );

            // Foreign thread and missing thread:
            // both return 404.
            if (
                thread == null
            )
            {
                Response.StatusCode =
                    StatusCodes
                        .Status404NotFound;

                return;
            }

            // =================================================
            // IDEMPOTENT DOUBLE-CLICK PROTECTION
            // =================================================

            if (
                thread.Status !=
                    "pending_approval"
            )
            {
                await Response
                    .WriteAsJsonAsync(
                        new
                        {
                            threadId,

                            status =
                                thread.Status,

                            alreadyProcessed =
                                true,

                            previousDecision =
                                thread
                                    .LastApprovalDecision
                        },
                        cancellationToken
                    );

                return;
            }

            thread
                .LastApprovalDecision =
                request.Approved;

            thread.Status =
                "running";

            thread.UpdatedAt =
                DateTime.UtcNow;

            await _db.SaveChangesAsync(
                cancellationToken
            );

            Response.ContentType =
                "text/event-stream";

            Response.Headers.CacheControl =
                "no-cache";

            Response.Headers.Connection =
                "keep-alive";

            var client =
                _httpClientFactory
                    .CreateClient(
                        "AgentService"
                    );

            using var upstreamRequest =
                new HttpRequestMessage(
                    HttpMethod.Post,
                    $"/agent/runs/{threadId}/resume"
                );

            upstreamRequest.Content =
                JsonContent.Create(
                    new
                    {
                        thread_id =
                            threadId,

                        approved =
                            request.Approved
                    }
                );

            upstreamRequest.Headers.Add(
                "X-Service-Key",
                GetServiceKey()
            );

            var auth =
                GetAuthorizationHeader();

            if (
                !string.IsNullOrWhiteSpace(
                    auth
                )
            )
            {
                upstreamRequest.Headers
                    .TryAddWithoutValidation(
                        "Authorization",
                        auth
                    );
            }

            try
            {
                using var upstream =
                    await client.SendAsync(
                        upstreamRequest,

                        HttpCompletionOption
                            .ResponseHeadersRead,

                        cancellationToken
                    );

                if (
                    !upstream
                        .IsSuccessStatusCode
                )
                {
                    thread.Status =
                        "failed";

                    thread.ErrorCode =
                        "UPSTREAM_ERROR";

                    thread.ErrorMessage =
                        "Agent service returned " +
                        $"{(int)upstream.StatusCode}.";

                    thread.UpdatedAt =
                        DateTime.UtcNow;

                    await _db
                        .SaveChangesAsync(
                            cancellationToken
                        );

                    await WriteLocalEvent(
                        "error",
                        new
                        {
                            code =
                                thread.ErrorCode,

                            message =
                                thread.ErrorMessage,

                            retryable =
                                true
                        },
                        cancellationToken
                    );

                    return;
                }

                await using var stream =
                    await upstream.Content
                        .ReadAsStreamAsync(
                            cancellationToken
                        );

                using var reader =
                    new StreamReader(
                        stream
                    );

                string? eventName =
                    null;

                while (
                    !reader.EndOfStream
                )
                {
                    cancellationToken
                        .ThrowIfCancellationRequested();

                    var line =
                        await reader
                            .ReadLineAsync(
                                cancellationToken
                            );

                    if (
                        line == null
                    )
                    {
                        break;
                    }

                    if (
                        line.StartsWith(
                            "event:"
                        )
                    )
                    {
                        eventName =
                            line[
                                "event:".Length..
                            ]
                            .Trim();

                        continue;
                    }

                    if (
                        line.StartsWith(
                            "data:"
                        )
                    )
                    {
                        var data =
                            line[
                                "data:".Length..
                            ]
                            .Trim();

                        await PersistEvent(
                            thread,
                            eventName,
                            data,
                            cancellationToken
                        );

                        if (
                            eventName != null
                        )
                        {
                            await Response
                                .WriteAsync(
                                    $"event: {eventName}\n",
                                    cancellationToken
                                );
                        }

                        await Response
                            .WriteAsync(
                                $"data: {data}\n\n",
                                cancellationToken
                            );

                        await Response.Body
                            .FlushAsync(
                                cancellationToken
                            );

                        eventName =
                            null;
                    }
                }
            }
            catch (
                OperationCanceledException
            )
            {
                thread.Status =
                    "cancelled";

                thread.IsCancelled =
                    true;

                thread.UpdatedAt =
                    DateTime.UtcNow;

                await _db.SaveChangesAsync(
                    CancellationToken.None
                );
            }
            catch (
                Exception ex
            )
            {
                thread.Status =
                    "failed";

                thread.ErrorCode =
                    "AGENT_UNAVAILABLE";

                thread.ErrorMessage =
                    "The agent service is unavailable.";

                thread.UpdatedAt =
                    DateTime.UtcNow;

                await _db.SaveChangesAsync(
                    CancellationToken.None
                );

                try
                {
                    await WriteLocalEvent(
                        "error",
                        new
                        {
                            code =
                                thread.ErrorCode,

                            message =
                                thread.ErrorMessage,

                            retryable =
                                true
                        },
                        CancellationToken.None
                    );
                }
                catch
                {
                }

                Console.WriteLine(
                    $"Agent resume error: {ex.Message}"
                );
            }
        }

        // =================================================
        // CANCEL
        // =================================================

        [HttpPost(
            "{threadId}/cancel"
        )]
        public async Task<IActionResult> CancelRun(
            string threadId
        )
        {
            var userId =
                GetCurrentUserId();

            var thread =
                await _db.AgentThreads
                    .FirstOrDefaultAsync(
                        x =>
                            x.ThreadId ==
                                threadId
                            &&
                            x.UserId ==
                                userId
                    );

            // Foreign/missing thread:
            // always 404.
            if (
                thread == null
            )
            {
                return NotFound();
            }

            // Idempotent cancellation.
            if (
                thread.Status ==
                    "cancelled"
            )
            {
                return Ok(
                    new
                    {
                        threadId,

                        status =
                            "cancelled",

                        alreadyCancelled =
                            true
                    }
                );
            }

            // =================================================
            // ACTUALLY STOP ACTIVE UPSTREAM REQUEST
            // =================================================

            var activeRunCancelled =
                _cancellationRegistry
                    .Cancel(
                        threadId
                    );

            thread.Status =
                "cancelled";

            thread.IsCancelled =
                true;

            thread.PendingApprovalJson =
                null;

            thread.UpdatedAt =
                DateTime.UtcNow;

            await _db.SaveChangesAsync();

            return Ok(
                new
                {
                    threadId,

                    status =
                        "cancelled",

                    alreadyCancelled =
                        false,

                    upstreamCancellationSignalled =
                        activeRunCancelled
                }
            );
        }
    }
}