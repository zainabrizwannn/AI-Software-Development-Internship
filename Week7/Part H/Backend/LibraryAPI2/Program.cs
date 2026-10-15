using System.Security.Claims;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.RateLimiting;
using LibraryAPI.Clients;
using LibraryAPI.Data;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.RateLimiting;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi;
using Polly;
using Polly.Extensions.Http;
using Polly.Timeout;
using LibraryAPI.Services;


var builder = WebApplication.CreateBuilder(args);


// =========================================================
// EXISTING AI SERVICE CLIENT
// =========================================================

builder.Services
    .AddHttpClient<IAiServiceClient, AiServiceClient>(
        client =>
        {
            var baseUrl =
                builder.Configuration[
                    "AiService:BaseUrl"
                ];

            if (
                string.IsNullOrWhiteSpace(
                    baseUrl
                )
            )
            {
                throw new InvalidOperationException(
                    "AiService:BaseUrl is not configured."
                );
            }

            client.BaseAddress =
                new Uri(baseUrl);

            client.Timeout =
                Timeout.InfiniteTimeSpan;
        }
    )
    .AddPolicyHandler(
        GetCircuitBreakerPolicy()
    )
    .AddPolicyHandler(
        GetRetryPolicy()
    )
    .AddPolicyHandler(
        GetTimeoutPolicy()
    );


// =========================================================
// PART H AGENT HTTP CLIENT
// =========================================================

builder.Services.AddHttpClient(
    "AgentService",
    client =>
    {
        var baseUrl =
            builder.Configuration[
                "AgentService:BaseUrl"
            ]
            ??
            "http://127.0.0.1:8000";

        client.BaseAddress =
            new Uri(baseUrl);

        // SSE may remain open for a long time.
        client.Timeout =
            Timeout.InfiniteTimeSpan;
    }
);


// =========================================================
// CONTROLLERS
// =========================================================

builder.Services
    .AddControllers()
    .AddJsonOptions(
        options =>
        {
            options
                .JsonSerializerOptions
                .ReferenceHandler =
                ReferenceHandler.IgnoreCycles;
        }
    );


// =========================================================
// SWAGGER
// =========================================================

builder.Services.AddEndpointsApiExplorer();

builder.Services.AddSwaggerGen(
    options =>
    {
        options.AddSecurityDefinition(
            "Bearer",
            new OpenApiSecurityScheme
            {
                Name =
                    "Authorization",

                Type =
                    SecuritySchemeType.Http,

                Scheme =
                    "bearer",

                BearerFormat =
                    "JWT",

                In =
                    ParameterLocation.Header,

                Description =
                    "Enter your JWT token."
            }
        );

        options.AddSecurityRequirement(
            document =>
                new OpenApiSecurityRequirement
                {
                    [
                        new OpenApiSecuritySchemeReference(
                            "Bearer",
                            document
                        )
                    ] = []
                }
        );
    }
);


// =========================================================
// DATABASE
// =========================================================

builder.Services.AddDbContext<
    LibraryDbContext
>(
    options =>
        options.UseSqlServer(
            builder.Configuration
                .GetConnectionString(
                    "DefaultConnection"
                )
        )
);


// =========================================================
// JWT
// =========================================================

var jwtKey =
    builder.Configuration[
        "Jwt:Key"
    ];

if (
    string.IsNullOrWhiteSpace(
        jwtKey
    )
)
{
    throw new InvalidOperationException(
        "JWT signing key is missing."
    );
}

var key =
    Encoding.UTF8.GetBytes(
        jwtKey
    );

builder.Services
    .AddAuthentication(
        options =>
        {
            options
                .DefaultAuthenticateScheme =
                JwtBearerDefaults
                    .AuthenticationScheme;

            options
                .DefaultChallengeScheme =
                JwtBearerDefaults
                    .AuthenticationScheme;
        }
    )
    .AddJwtBearer(
        options =>
        {
            options.TokenValidationParameters =
                new TokenValidationParameters
                {
                    ValidateIssuerSigningKey =
                        true,

                    IssuerSigningKey =
                        new SymmetricSecurityKey(
                            key
                        ),

                    ValidateIssuer =
                        true,

                    ValidIssuer =
                        builder.Configuration[
                            "Jwt:Issuer"
                        ],

                    ValidateAudience =
                        true,

                    ValidAudience =
                        builder.Configuration[
                            "Jwt:Audience"
                        ],

                    ValidateLifetime =
                        true,

                    ClockSkew =
                        TimeSpan.Zero
                };
        }
    );

builder.Services.AddAuthorization();


// =========================================================
// PART H RATE LIMITING
// =========================================================

builder.Services.AddRateLimiter(
    options =>
    {
        options.RejectionStatusCode =
            StatusCodes
                .Status429TooManyRequests;

        options.AddPolicy(
            "assistant",
            httpContext =>
            {
                var userId =
                    httpContext.User
                        .FindFirstValue(
                            ClaimTypes
                                .NameIdentifier
                        )
                    ??
                    httpContext
                        .Connection
                        .RemoteIpAddress
                        ?.ToString()
                    ??
                    "anonymous";

                return RateLimitPartition
                    .GetFixedWindowLimiter(
                        partitionKey:
                            userId,

                        factory:
                            _ =>
                                new FixedWindowRateLimiterOptions
                                {
                                    PermitLimit =
                                        5,

                                    Window =
                                        TimeSpan
                                            .FromMinutes(
                                                1
                                            ),

                                    QueueLimit =
                                        0,

                                    AutoReplenishment =
                                        true
                                }
                    );
            }
        );
    }
);


// =========================================================
// CORS
// =========================================================

builder.Services.AddCors(
    options =>
    {
        options.AddPolicy(
            "AllowAngular",
            policy =>
            {
                policy
                    .WithOrigins(
                        "http://localhost:4200"
                    )
                    .AllowAnyHeader()
                    .AllowAnyMethod();
            }
        );
    }
);


// =========================================================
// EXISTING STREAMING CLIENT
// =========================================================

builder.Services.AddHttpClient(
    "AiStreaming",
    client =>
    {
        var baseUrl =
            builder.Configuration[
                "AiService:BaseUrl"
            ];

        if (
            string.IsNullOrWhiteSpace(
                baseUrl
            )
        )
        {
            throw new InvalidOperationException(
                "AiService:BaseUrl is not configured."
            );
        }

        client.BaseAddress =
            new Uri(baseUrl);

        client.Timeout =
            Timeout.InfiniteTimeSpan;
    }
);

builder.Services.AddSingleton<
    AgentRunCancellationRegistry
>();

var app =
    builder.Build();


if (
    app.Environment
        .IsDevelopment()
)
{
    app.UseSwagger();
    app.UseSwaggerUI();
}


app.UseHttpsRedirection();

app.UseCors(
    "AllowAngular"
);

app.UseAuthentication();

app.UseAuthorization();


// MUST BE AFTER AUTHENTICATION
app.UseRateLimiter();


app.MapControllers();


app.Run();


// =========================================================
// POLLY
// =========================================================

static IAsyncPolicy<
    HttpResponseMessage
>
GetRetryPolicy()
{
    return HttpPolicyExtensions
        .HandleTransientHttpError()
        .WaitAndRetryAsync(
            retryCount: 3,

            sleepDurationProvider:
                attempt =>
                    TimeSpan
                        .FromSeconds(
                            Math.Pow(
                                2,
                                attempt
                            )
                        ),

            onRetry:
                (
                    outcome,
                    delay,
                    attempt,
                    context
                ) =>
                {
                    Console.WriteLine(
                        $"AI retry {attempt} " +
                        $"after " +
                        $"{delay.TotalSeconds} seconds."
                    );
                }
        );
}


static IAsyncPolicy<
    HttpResponseMessage
>
GetCircuitBreakerPolicy()
{
    return HttpPolicyExtensions
        .HandleTransientHttpError()
        .CircuitBreakerAsync(
            handledEventsAllowedBeforeBreaking:
                3,

            durationOfBreak:
                TimeSpan.FromSeconds(
                    30
                ),

            onBreak:
                (
                    outcome,
                    breakDelay
                ) =>
                {
                    Console.WriteLine(
                        $"AI circuit opened for " +
                        $"{breakDelay.TotalSeconds} seconds."
                    );
                },

            onReset:
                () =>
                {
                    Console.WriteLine(
                        "AI circuit closed again."
                    );
                }
        );
}


static IAsyncPolicy<
    HttpResponseMessage
>
GetTimeoutPolicy()
{
    return Policy
        .TimeoutAsync<
            HttpResponseMessage
        >(
            TimeSpan.FromSeconds(
                10
            )
        );
}


public partial class Program
{
}