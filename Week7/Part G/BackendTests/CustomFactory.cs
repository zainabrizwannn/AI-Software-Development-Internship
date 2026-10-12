using System.Security.Claims;
using System.Text.Encodings.Web;
using LibraryAPI.Data;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Data.Sqlite;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Infrastructure;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

namespace BackendTests;

public class CustomFactory : WebApplicationFactory<Program>
{
    private readonly SqliteConnection _connection;

    public const string TestScheme = "TestAuth";

    public CustomFactory()
    {
        _connection = new SqliteConnection(
            "DataSource=:memory:"
        );

        _connection.Open();
    }

    protected override void ConfigureWebHost(
        IWebHostBuilder builder
    )
    {
        builder.UseEnvironment("Testing");

        builder.ConfigureServices(services =>
        {
            // Remove SQL Server DbContext registrations.
            services.RemoveAll<
                DbContextOptions<LibraryDbContext>
            >();

            services.RemoveAll<
                IDbContextOptionsConfiguration<
                    LibraryDbContext
                >
            >();

            services.RemoveAll<
                LibraryDbContext
            >();

            // Add SQLite in-memory test database.
            services.AddDbContext<LibraryDbContext>(
                options =>
                {
                    options.UseSqlite(
                        _connection
                    );
                }
            );

            var provider =
                services.BuildServiceProvider();

            using var scope =
                provider.CreateScope();

            var db =
                scope.ServiceProvider
                    .GetRequiredService<
                        LibraryDbContext
                    >();

            db.Database.EnsureCreated();
        });

        // Replace production JWT authentication
        // with deterministic test authentication.
        builder.ConfigureTestServices(services =>
        {
            services
                .AddAuthentication(options =>
                {
                    options.DefaultAuthenticateScheme =
                        TestScheme;

                    options.DefaultChallengeScheme =
                        TestScheme;

                    options.DefaultScheme =
                        TestScheme;
                })
                .AddScheme<
                    AuthenticationSchemeOptions,
                    TestAuthHandler
                >(
                    TestScheme,
                    options => { }
                );
        });
    }

    protected override void Dispose(
        bool disposing
    )
    {
        base.Dispose(disposing);

        if (disposing)
        {
            _connection.Dispose();
        }
    }
}


// ---------------------------------------------------------
// TEST AUTHENTICATION HANDLER
// ---------------------------------------------------------

public class TestAuthHandler
    : AuthenticationHandler<
        AuthenticationSchemeOptions
    >
{
    public TestAuthHandler(
        IOptionsMonitor<
            AuthenticationSchemeOptions
        > options,
        ILoggerFactory logger,
        UrlEncoder encoder
    )
        : base(
            options,
            logger,
            encoder
        )
    {
    }

    protected override Task<
        AuthenticateResult
    > HandleAuthenticateAsync()
    {
        // No Authorization header:
        // endpoint should return 401.
        if (
            !Request.Headers.ContainsKey(
                "Authorization"
            )
        )
        {
            return Task.FromResult(
                AuthenticateResult.NoResult()
            );
        }

        var header =
            Request.Headers.Authorization
                .ToString();

        if (
            string.IsNullOrWhiteSpace(
                header
            )
            ||
            !header.StartsWith(
                "Bearer test-user-"
            )
        )
        {
            return Task.FromResult(
                AuthenticateResult.Fail(
                    "Invalid test token."
                )
            );
        }

        // Example:
        // Bearer test-user-1002
        var userId =
            header.Replace(
                "Bearer test-user-",
                ""
            );

        var claims =
            new[]
            {
                new Claim(
                    ClaimTypes.NameIdentifier,
                    userId
                ),

                new Claim(
                    ClaimTypes.Name,
                    $"pytest-user-{userId}"
                ),

                new Claim(
                    ClaimTypes.Role,
                    "User"
                )
            };

        var identity =
            new ClaimsIdentity(
                claims,
                CustomFactory.TestScheme
            );

        var principal =
            new ClaimsPrincipal(
                identity
            );

        var ticket =
            new AuthenticationTicket(
                principal,
                CustomFactory.TestScheme
            );

        return Task.FromResult(
            AuthenticateResult.Success(
                ticket
            )
        );
    }
}