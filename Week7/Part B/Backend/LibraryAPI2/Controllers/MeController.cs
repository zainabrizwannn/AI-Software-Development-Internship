using System.Security.Claims;
using LibraryAPI.Data;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace LibraryAPI.Controllers
{
    [ApiController]
    [Route("api/me")]
    [Authorize]
    public class MeController : ControllerBase
    {
        private readonly LibraryDbContext _context;

        public MeController(
            LibraryDbContext context)
        {
            _context = context;
        }

        // GET: api/me/reservations
        [HttpGet("reservations")]
        public async Task<IActionResult>
            GetMyReservations()
        {
            var userId =
                User.FindFirstValue(
                    ClaimTypes.NameIdentifier);

            if (string.IsNullOrWhiteSpace(
                    userId))
            {
                return Unauthorized(
                    new
                    {
                        message =
                            "Authenticated user identity is missing."
                    });
            }

            var reservations =
                await _context.Reservations
                    .AsNoTracking()
                    .Where(
                        r => r.UserId == userId)
                    .Include(
                        r => r.Book)
                    .OrderByDescending(
                        r => r.CreatedAt)
                    .Select(
                        r => new
                        {
                            reservationId =
                                r.Id,

                            bookId =
                                r.BookId,

                            title =
                                r.Book != null
                                    ? r.Book.Title
                                    : "Unknown",

                            createdAt =
                                r.CreatedAt
                        })
                    .ToListAsync();

            return Ok(
                reservations);
        }
    }
}