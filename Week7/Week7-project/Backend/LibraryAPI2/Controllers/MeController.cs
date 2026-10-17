using System.Security.Claims;
using LibraryAPI.Data;
using LibraryAPI.Models;
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

        // -------------------------------------------------
        // GET: api/me/reservations
        // -------------------------------------------------

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
                return Unauthorized();
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

        // -------------------------------------------------
        // GET: api/me/preferences
        // -------------------------------------------------

        [HttpGet("preferences")]
        public async Task<IActionResult>
            GetPreferences()
        {
            var userId =
                User.FindFirstValue(
                    ClaimTypes.NameIdentifier);

            if (string.IsNullOrWhiteSpace(
                    userId))
            {
                return Unauthorized();
            }

            var preferences =
                await _context.UserPreferences
                    .AsNoTracking()
                    .Where(
                        p => p.UserId == userId)
                    .Select(
                        p => new
                        {
                            key =
                                p.Key,

                            value =
                                p.Value
                        })
                    .ToListAsync();

            return Ok(
                preferences);
        }

        // -------------------------------------------------
        // POST: api/me/preferences
        // -------------------------------------------------

        [HttpPost("preferences")]
        public async Task<IActionResult>
            SavePreference(
                PreferenceRequest request)
        {
            var userId =
                User.FindFirstValue(
                    ClaimTypes.NameIdentifier);

            if (string.IsNullOrWhiteSpace(
                    userId))
            {
                return Unauthorized();
            }

            if (
                string.IsNullOrWhiteSpace(
                    request.Key)
                ||
                string.IsNullOrWhiteSpace(
                    request.Value))
            {
                return BadRequest(
                    new
                    {
                        message =
                            "Preference key and value are required."
                    });
            }

            var key =
                request.Key.Trim();

            var value =
                request.Value.Trim();

            var existing =
                await _context.UserPreferences
                    .FirstOrDefaultAsync(
                        p =>
                            p.UserId == userId
                            &&
                            p.Key == key);

            if (existing != null)
            {
                existing.Value =
                    value;
            }
            else
            {
                _context.UserPreferences.Add(
                    new UserPreference
                    {
                        UserId =
                            userId,

                        Key =
                            key,

                        Value =
                            value
                    });
            }

            await _context.SaveChangesAsync();

            return Ok(
                new
                {
                    message =
                        "Preference saved.",

                    key,

                    value
                });
        }

        // -------------------------------------------------
        // DELETE: api/me/preferences
        // -------------------------------------------------

        [HttpDelete("preferences")]
        public async Task<IActionResult>
            DeletePreferences()
        {
            var userId =
                User.FindFirstValue(
                    ClaimTypes.NameIdentifier);

            if (string.IsNullOrWhiteSpace(
                    userId))
            {
                return Unauthorized();
            }

            var preferences =
                await _context.UserPreferences
                    .Where(
                        p => p.UserId == userId)
                    .ToListAsync();

            _context.UserPreferences.RemoveRange(
                preferences);

            await _context.SaveChangesAsync();

            return Ok(
                new
                {
                    message =
                        "All saved preferences were deleted."
                });
        }
    }


    public class PreferenceRequest
    {
        public string Key { get; set; }
            = string.Empty;

        public string Value { get; set; }
            = string.Empty;
    }
}