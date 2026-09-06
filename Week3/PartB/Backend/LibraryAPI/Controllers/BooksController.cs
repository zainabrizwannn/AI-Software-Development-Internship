using LibraryAPI.Data;
using LibraryAPI.Models;
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
        public async Task<ActionResult<IEnumerable<Book>>> GetBooks()
        {
            return await _context.Books
                .Include(b => b.Author)
                .ToListAsync();
        }

        // GET: api/Books/author/2
        [HttpGet("author/{authorId}")]
        public async Task<ActionResult<IEnumerable<Book>>> GetBooksByAuthor(int authorId)
        {
            return await _context.Books
                .Where(b => b.AuthorId == authorId)
                .ToListAsync();
        }

        // POST: api/Books
        [HttpPost]
        public async Task<IActionResult> AddBook(Book book)
        {
            try
            {
                _context.Books.Add(book);

                await _context.SaveChangesAsync();

                return Ok(book);
            }
            catch (Exception ex)
            {
                return BadRequest("Error saving book: " + ex.Message);
            }
        }

        // PUT: api/Books/5
        [HttpPut("{id}")]
        public async Task<IActionResult> UpdateBook(int id, Book updatedBook)
        {
            var book = await _context.Books.FindAsync(id);

            if (book == null)
            {
                return NotFound("Book not found.");
            }

            try
            {
                book.Title = updatedBook.Title;
                book.AuthorId = updatedBook.AuthorId;

                await _context.SaveChangesAsync();

                return Ok(book);
            }
            catch (Exception ex)
            {
                return BadRequest("Error updating book: " + ex.Message);
            }
        }

        // DELETE: api/Books/5
        [HttpDelete("{id}")]
        public async Task<IActionResult> DeleteBook(int id)
        {
            var book = await _context.Books.FindAsync(id);

            if (book == null)
            {
                return NotFound("Book not found.");
            }

            try
            {
                _context.Books.Remove(book);

                await _context.SaveChangesAsync();

                return Ok("Book deleted successfully.");
            }
            catch (Exception ex)
            {
                return BadRequest("Error deleting book: " + ex.Message);
            }
        }
    }
}