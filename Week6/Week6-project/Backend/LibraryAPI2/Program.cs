using System.Text;
using LibraryAPI.Data;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi;
using System.Text.Json.Serialization;
using LibraryAPI.Clients;
using Polly;
using Polly.Extensions.Http;
using Polly.Timeout;
var builder = WebApplication.CreateBuilder(args);
builder.Services
    .AddHttpClient<IAiServiceClient, AiServiceClient>(
        client =>
        {
            var baseUrl =
                builder.Configuration[
                    "AiService:BaseUrl" ];
            if (string.IsNullOrWhiteSpace(baseUrl)) {
                throw new InvalidOperationException(
                    "AiService:BaseUrl is not configured.");}
            client.BaseAddress =
                new Uri(baseUrl);
            client.Timeout =
                Timeout.InfiniteTimeSpan;})
    .AddPolicyHandler(
        GetCircuitBreakerPolicy())
    .AddPolicyHandler(
        GetRetryPolicy())
    .AddPolicyHandler(
        GetTimeoutPolicy());

// Controllers
builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        options.JsonSerializerOptions.ReferenceHandler = ReferenceHandler.IgnoreCycles;
    });

// Swagger
builder.Services.AddEndpointsApiExplorer();

builder.Services.AddSwaggerGen(options =>
{
    options.AddSecurityDefinition(
        "Bearer",
        new OpenApiSecurityScheme
        {
            Name = "Authorization",
            Type = SecuritySchemeType.Http,
            Scheme = "bearer",
            BearerFormat = "JWT",
            In = ParameterLocation.Header,
            Description = "Enter your JWT token."
        }
    );

    options.AddSecurityRequirement(document =>
        new OpenApiSecurityRequirement
        {
            [new OpenApiSecuritySchemeReference("Bearer", document)] = []
        }
    );
});

// Database
builder.Services.AddDbContext<LibraryDbContext>(options =>
    options.UseSqlServer(
        builder.Configuration.GetConnectionString("DefaultConnection")
    ));

// JWT
var jwtKey = builder.Configuration["Jwt:Key"];

if (string.IsNullOrWhiteSpace(jwtKey))
{
    throw new InvalidOperationException("JWT signing key is missing.");
}

var key = Encoding.UTF8.GetBytes(jwtKey);

builder.Services
    .AddAuthentication(options =>
    {
        options.DefaultAuthenticateScheme =
            JwtBearerDefaults.AuthenticationScheme;
        options.DefaultChallengeScheme =
            JwtBearerDefaults.AuthenticationScheme;
    })
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters =
            new TokenValidationParameters
            {
                ValidateIssuerSigningKey = true,
                IssuerSigningKey = new SymmetricSecurityKey(key),

                ValidateIssuer = true,
                ValidIssuer = builder.Configuration["Jwt:Issuer"],

                ValidateAudience = true,
                ValidAudience = builder.Configuration["Jwt:Audience"],

                ValidateLifetime = true,
                ClockSkew = TimeSpan.Zero
            };
    });

builder.Services.AddAuthorization();

builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAngular", policy =>
    {
        policy.WithOrigins("http://localhost:4200")
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});
builder.Services.AddHttpClient(
    "AiStreaming",
    client =>
    {
        var baseUrl =
            builder.Configuration[
                "AiService:BaseUrl"
            ];

        if (string.IsNullOrWhiteSpace(baseUrl))
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

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

app.UseCors("AllowAngular");

app.UseAuthentication();

app.UseAuthorization();

app.MapControllers();
app.Run();
static IAsyncPolicy<HttpResponseMessage>
    GetRetryPolicy(){
    return HttpPolicyExtensions
        .HandleTransientHttpError()
        .WaitAndRetryAsync(
            retryCount: 3,
            sleepDurationProvider: attempt =>
                TimeSpan.FromSeconds(
                    Math.Pow(2, attempt)),
            onRetry: (
                outcome,
                delay,
                attempt,
                context
            ) =>{
                Console.WriteLine(
                    $"AI retry {attempt} after {delay.TotalSeconds} seconds.");});}
static IAsyncPolicy<HttpResponseMessage>
    GetCircuitBreakerPolicy()
{
    return HttpPolicyExtensions
        .HandleTransientHttpError()
        .CircuitBreakerAsync(
            handledEventsAllowedBeforeBreaking: 3,
            durationOfBreak:
                TimeSpan.FromSeconds(30),
            onBreak: (
                outcome,
                breakDelay) =>{
                Console.WriteLine(
                    $"AI circuit opened for {breakDelay.TotalSeconds} seconds.");},
            onReset: () =>{
                Console.WriteLine(
                    "AI circuit closed again.");});}
static IAsyncPolicy<HttpResponseMessage>
    GetTimeoutPolicy(){
    return Policy.TimeoutAsync<HttpResponseMessage>(
        TimeSpan.FromSeconds(10));}