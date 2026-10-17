using System.Net;
using System.Net.Http.Headers;
using LibraryAPI.Data;
using LibraryAPI.Models;
using Microsoft.Extensions.DependencyInjection;
using Xunit;

namespace BackendTests;

public class ReservationTests
    : IClassFixture<CustomFactory>
{
    private readonly HttpClient _client;
    private readonly CustomFactory _factory;

    public ReservationTests(
        CustomFactory factory
    )
    {
        _factory = factory;
        _client = factory.CreateClient();
    }


    // =========================================================
    // HELPERS
    // =========================================================

    private void Authorize(
        string userId = "1002"
    )
    {
        _client
            .DefaultRequestHeaders
            .Authorization =
            new AuthenticationHeaderValue(
                "Bearer",
                $"test-user-{userId}"
            );
    }


    private void ClearAuthorization()
    {
        _client
            .DefaultRequestHeaders
            .Authorization = null;
    }


    private async Task SeedBook(
        int bookId,
        bool available
    )
    {
        using var scope =
            _factory.Services
                .CreateScope();

        var db =
            scope.ServiceProvider
                .GetRequiredService<
                    LibraryDbContext
                >();

        var existing =
            await db.Books
                .FindAsync(
                    bookId
                );

        if (
            existing != null
        )
        {
            existing.IsAvailable =
                available;

            await db
                .SaveChangesAsync();

            return;
        }


        var author =
            new Author
            {
                FullName =
                    $"Test Author {bookId}"
            };

        db.Authors.Add(
            author
        );

        await db
            .SaveChangesAsync();


        db.Books.Add(
            new Book
            {
                BookId =
                    bookId,

                Title =
                    $"Test Book {bookId}",

                AuthorId =
                    author.AuthorId,

                IsAvailable =
                    available
            }
        );

        await db
            .SaveChangesAsync();
    }


    // =========================================================
    // TEST 1
    // Reservation requires authentication
    // =========================================================

    [Fact]
    public async Task
        Reserve_WithoutToken_Returns401()
    {
        ClearAuthorization();

        var request =
            new HttpRequestMessage(
                HttpMethod.Post,
                "/api/Books/1/reserve"
            );

        request.Headers.Add(
            "Idempotency-Key",
            "test-no-token"
        );


        var response =
            await _client
                .SendAsync(
                    request
                );


        Assert.Equal(
            HttpStatusCode.Unauthorized,
            response.StatusCode
        );
    }


    // =========================================================
    // TEST 2
    // My reservations require authentication
    // =========================================================

    [Fact]
    public async Task
        MyReservations_WithoutToken_Returns401()
    {
        ClearAuthorization();

        var response =
            await _client
                .GetAsync(
                    "/api/me/reservations"
                );


        Assert.Equal(
            HttpStatusCode.Unauthorized,
            response.StatusCode
        );
    }


    // =========================================================
    // TEST 3
    // Preferences require authentication
    // =========================================================

    [Fact]
    public async Task
        Preferences_WithoutToken_Returns401()
    {
        ClearAuthorization();

        var response =
            await _client
                .GetAsync(
                    "/api/me/preferences"
                );


        Assert.Equal(
            HttpStatusCode.Unauthorized,
            response.StatusCode
        );
    }


    // =========================================================
    // TEST 4
    // Unknown book -> 404
    // =========================================================

    [Fact]
    public async Task
        Reserve_UnknownBook_Returns404()
    {
        Authorize("1002");


        var request =
            new HttpRequestMessage(
                HttpMethod.Post,
                "/api/Books/999999/reserve"
            );

        request.Headers.Add(
            "Idempotency-Key",
            Guid.NewGuid()
                .ToString()
        );


        var response =
            await _client
                .SendAsync(
                    request
                );


        Assert.Equal(
            HttpStatusCode.NotFound,
            response.StatusCode
        );
    }


    // =========================================================
    // TEST 5
    // Unavailable book -> 409
    // =========================================================

    [Fact]
    public async Task
        Reserve_UnavailableBook_Returns409()
    {
        await SeedBook(
            5001,
            false
        );

        Authorize("1002");


        var request =
            new HttpRequestMessage(
                HttpMethod.Post,
                "/api/Books/5001/reserve"
            );

        request.Headers.Add(
            "Idempotency-Key",
            Guid.NewGuid()
                .ToString()
        );


        var response =
            await _client
                .SendAsync(
                    request
                );


        Assert.Equal(
            HttpStatusCode.Conflict,
            response.StatusCode
        );
    }


    // =========================================================
    // TEST 6
    // Same idempotency key -> one reservation
    // =========================================================

    [Fact]
    public async Task
        Reserve_SameIdempotencyKeyTwice_CreatesOneReservation()
    {
        await SeedBook(
            5002,
            true
        );

        Authorize("1002");


        var key =
            $"pytest-{Guid.NewGuid()}";


        var request1 =
            new HttpRequestMessage(
                HttpMethod.Post,
                "/api/Books/5002/reserve"
            );

        request1.Headers.Add(
            "Idempotency-Key",
            key
        );


        var response1 =
            await _client
                .SendAsync(
                    request1
                );


        var request2 =
            new HttpRequestMessage(
                HttpMethod.Post,
                "/api/Books/5002/reserve"
            );

        request2.Headers.Add(
            "Idempotency-Key",
            key
        );


        var response2 =
            await _client
                .SendAsync(
                    request2
                );


        Assert.Equal(
            HttpStatusCode.OK,
            response1.StatusCode
        );

        Assert.Equal(
            HttpStatusCode.OK,
            response2.StatusCode
        );


        using var scope =
            _factory.Services
                .CreateScope();

        var db =
            scope.ServiceProvider
                .GetRequiredService<
                    LibraryDbContext
                >();


        var count =
            db.Reservations
                .Count(
                    r =>
                        r.BookId ==
                            5002
                        &&
                        r.UserId ==
                            "1002"
                );


        Assert.Equal(
            1,
            count
        );
    }


    // =========================================================
    // TEST 7
    // Foreign thread -> 404
    // =========================================================

    [Fact]
    public async Task
        ResumeThread_OwnedByAnotherUser_Returns404()
    {
        var threadId =
            $"private-{Guid.NewGuid()}";


        using (
            var scope =
                _factory.Services
                    .CreateScope()
        )
        {
            var db =
                scope.ServiceProvider
                    .GetRequiredService<
                        LibraryDbContext
                    >();


            db.AgentThreads.Add(
                new AgentThread
                {
                    ThreadId =
                        threadId,

                    UserId =
                        "1002"
                }
            );


            await db
                .SaveChangesAsync();
        }


        // User B
        Authorize(
            "2002"
        );


        var response =
            await _client
                .GetAsync(
                    $"/api/assistant/threads/{threadId}"
                );


        Assert.Equal(
            HttpStatusCode.NotFound,
            response.StatusCode
        );
    }


    // =========================================================
    // TEST 8
    // Same book + different idempotency key -> 409
    // =========================================================

    [Fact]
    public async Task
        Reserve_SameBookWithDifferentKey_Returns409()
    {
        await SeedBook(
            5003,
            true
        );

        Authorize(
            "1002"
        );


        var firstRequest =
            new HttpRequestMessage(
                HttpMethod.Post,
                "/api/Books/5003/reserve"
            );

        firstRequest
            .Headers
            .Add(
                "Idempotency-Key",
                $"first-{Guid.NewGuid()}"
            );


        var firstResponse =
            await _client
                .SendAsync(
                    firstRequest
                );


        Assert.Equal(
            HttpStatusCode.OK,
            firstResponse.StatusCode
        );


        var secondRequest =
            new HttpRequestMessage(
                HttpMethod.Post,
                "/api/Books/5003/reserve"
            );

        secondRequest
            .Headers
            .Add(
                "Idempotency-Key",
                $"second-{Guid.NewGuid()}"
            );


        var secondResponse =
            await _client
                .SendAsync(
                    secondRequest
                );


        Assert.Equal(
            HttpStatusCode.Conflict,
            secondResponse.StatusCode
        );
    }
}