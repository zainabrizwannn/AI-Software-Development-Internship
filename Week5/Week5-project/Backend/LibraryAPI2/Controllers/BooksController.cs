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
                    author = b.Author != null ? b.Author.FullName : "Unknown",
                    categories = b.Categories.Select(c => c.CategoryName).ToList()
                })
                .ToListAsync();

            return Ok(books);
        }

        // GET: api/Books/author/2
        [HttpGet("author/{authorId}")]
        public async Task<IActionResult> GetBooksByAuthor(int authorId)
        {
            var books = await _context.Books
                .Where(b => b.AuthorId == authorId)
                .Include(b => b.Author)
                .Include(b => b.Categories)
                .Select(b => new
                {
                    bookId = b.BookId,
                    title = b.Title,
                    author = b.Author != null ? b.Author.FullName : "Unknown",
                    categories = b.Categories.Select(c => c.CategoryName).ToList()
                })
                .ToListAsync();

            return Ok(books);
        }

        // POST: api/Books
        [Authorize]
        [HttpPost]
        public async Task<IActionResult> AddBook(Book book)
        {
            _context.Books.Add(book);

            await _context.SaveChangesAsync();

            return Ok(book);
        }

        // PUT: api/Books/5
        [Authorize]
        [HttpPut("{id}")]
        public async Task<IActionResult> UpdateBook(int id, Book updatedBook)
        {
            var book = await _context.Books.FindAsync(id);

            if (book == null)
            {
                return NotFound("Book not found.");
            }

            book.Title = updatedBook.Title;
            book.AuthorId = updatedBook.AuthorId;

            await _context.SaveChangesAsync();

            return Ok(book);
        }

        // DELETE: api/Books/5
        [Authorize(Roles = "Admin")]
        [HttpDelete("{id}")]
        public async Task<IActionResult> DeleteBook(int id)
        {
            var book = await _context.Books.FindAsync(id);

            if (book == null)
            {
                return NotFound("Book not found.");
            }

            _context.Books.Remove(book);

            await _context.SaveChangesAsync();

            return Ok("Book deleted successfully.");
        }
    }
}