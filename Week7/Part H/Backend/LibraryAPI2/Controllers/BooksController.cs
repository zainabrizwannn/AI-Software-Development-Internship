using System.Security.Claims;
using LibraryAPI.Data;
using LibraryAPI.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace LibraryAPI.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class BooksController : ControllerBase
    {
        private readonly LibraryDbContext _context;

        public BooksController(LibraryDbContext context)
        {
            _context = context;
        }

        // GET: api/Books
        [HttpGet]
        public async Task<IActionResult> GetBooks()
        {
            var books = await _context.Books
                .Include(b => b.Author)
                .Include(b => b.Categories)
                .Select(b => new
                {
                    bookId = b.BookId,
                    title = b.Title,
                    author = b.Author != null
                        ? b.Author.FullName
                        : "Unknown",
                    categories = b.Categories
                        .Select(c => c.CategoryName)
                        .ToList()
                })
                .ToListAsync();

            return Ok(books);
        }

        // GET: api/Books/author/2
        [HttpGet("author/{authorId}")]
        public async Task<IActionResult> GetBooksByAuthor(
            int authorId)
        {
            var books = await _context.Books
                .Where(b => b.AuthorId == authorId)
                .Include(b => b.Author)
                .Include(b => b.Categories)
                .Select(b => new
                {
                    bookId = b.BookId,
                    title = b.Title,
                    author = b.Author != null
                        ? b.Author.FullName
                        : "Unknown",
                    categories = b.Categories
                        .Select(c => c.CategoryName)
                        .ToList()
                })
                .ToListAsync();

            return Ok(books);
        }

        // GET: api/Books/4/availability
        [AllowAnonymous]
        [HttpGet("{id}/availability")]
        public async Task<IActionResult> GetBookAvailability(
            int id)
        {
            var book = await _context.Books
                .AsNoTracking()
                .FirstOrDefaultAsync(
                    b => b.BookId == id);

            if (book == null)
            {
                return NotFound(new
                {
                    message = "Book not found."
                });
            }

            return Ok(new
            {
                bookId = book.BookId,
                title = book.Title,
                isAvailable = book.IsAvailable
            });
        }

        // POST: api/Books/4/reserve
        [Authorize]
        [HttpPost("{id}/reserve")]
        public async Task<IActionResult> ReserveBook(
            int id,
            [FromHeader(Name = "Idempotency-Key")]
            string? idempotencyKey)
        {
            // 1. Read authenticated user from JWT
            var userId = User.FindFirstValue(
                ClaimTypes.NameIdentifier);

            if (string.IsNullOrWhiteSpace(userId))
            {
                return Unauthorized(new
                {
                    message =
                        "Authenticated user identity is missing."
                });
            }

            // 2. Validate Idempotency-Key
            if (string.IsNullOrWhiteSpace(
                    idempotencyKey))
            {
                return BadRequest(new
                {
                    message =
                        "Idempotency-Key header is required."
                });
            }

            var suppliedKey =
                idempotencyKey.Trim();

            // Scope key to authenticated user
            var storedKey =
                $"{userId}:{suppliedKey}";

            // 3. Same request already processed?
            var existingByKey =
                await _context.Reservations
                    .AsNoTracking()
                    .Include(r => r.Book)
                    .FirstOrDefaultAsync(
                        r =>
                            r.UserId == userId &&
                            r.IdempotencyKey ==
                                storedKey);

            if (existingByKey != null)
            {
                return Ok(new
                {
                    reservationId =
                        existingByKey.Id,

                    bookId =
                        existingByKey.BookId,

                    title =
                        existingByKey.Book != null
                            ? existingByKey.Book.Title
                            : "Unknown",

                    userId =
                        existingByKey.UserId,

                    createdAt =
                        existingByKey.CreatedAt
                });
            }

            // 4. Find book
            var book = await _context.Books
                .FirstOrDefaultAsync(
                    b => b.BookId == id);

            if (book == null)
            {
                return NotFound(new
                {
                    message =
                        "Book not found."
                });
            }

            // 5. Check existing reservation
            var reservationAlreadyExists =
                await _context.Reservations
                    .AnyAsync(
                        r => r.BookId == id);

            if (
                reservationAlreadyExists ||
                !book.IsAvailable)
            {
                return Conflict(new
                {
                    message =
                        $"Book {id} is already reserved."
                });
            }

            // 6. Create reservation
            var reservation =
                new Reservation
                {
                    BookId = id,

                    UserId = userId,

                    CreatedAt =
                        DateTime.UtcNow,

                    IdempotencyKey =
                        storedKey
                };

            _context.Reservations.Add(
                reservation);

            book.IsAvailable = false;

            await _context.SaveChangesAsync();

            // 7. Return result
            return Ok(new
            {
                reservationId =
                    reservation.Id,

                bookId =
                    reservation.BookId,

                title =
                    book.Title,

                userId =
                    reservation.UserId,

                createdAt =
                    reservation.CreatedAt
            });
        }

        // POST: api/Books
        [Authorize]
        [HttpPost]
        public async Task<IActionResult> AddBook(
            Book book)
        {
            _context.Books.Add(book);

            await _context.SaveChangesAsync();

            return Ok(book);
        }

        // PUT: api/Books/5
        [Authorize]
        [HttpPut("{id}")]
        public async Task<IActionResult> UpdateBook(
            int id,
            Book updatedBook)
        {
            var book =
                await _context.Books.FindAsync(id);

            if (book == null)
            {
                return NotFound(
                    "Book not found.");
            }

            book.Title =
                updatedBook.Title;

            book.AuthorId =
                updatedBook.AuthorId;

            await _context.SaveChangesAsync();

            return Ok(book);
        }

        // DELETE: api/Books/5
        [Authorize(Roles = "Admin")]
        [HttpDelete("{id}")]
        public async Task<IActionResult> DeleteBook(
            int id)
        {
            var book =
                await _context.Books.FindAsync(id);

            if (book == null)
            {
                return NotFound(
                    "Book not found.");
            }

            _context.Books.Remove(book);

            await _context.SaveChangesAsync();

            return Ok(
                "Book deleted successfully.");
        }
    }
}