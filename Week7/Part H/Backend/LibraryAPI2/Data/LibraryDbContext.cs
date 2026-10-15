using LibraryAPI.Models;
using Microsoft.EntityFrameworkCore;

namespace LibraryAPI.Data
{
    public class LibraryDbContext : DbContext
    {
        public LibraryDbContext(
            DbContextOptions<LibraryDbContext> options
        ) : base(options)
        {
        }

        public DbSet<User> Users { get; set; }

        public DbSet<Book> Books { get; set; }

        public DbSet<Author> Authors { get; set; }

        public DbSet<Category> Categories { get; set; }

        public DbSet<Reservation> Reservations { get; set; }

        public DbSet<AgentThread> AgentThreads { get; set; }

        public DbSet<UserPreference> UserPreferences { get; set; }

        protected override void OnModelCreating(
            ModelBuilder modelBuilder
        )
        {
            base.OnModelCreating(modelBuilder);

            // ---------------------------------------------
            // AGENT THREAD
            // ---------------------------------------------

            modelBuilder.Entity<AgentThread>(
                entity =>
                {
                    entity.HasKey(
                        x => x.ThreadId
                    );

                    entity.Property(
                        x => x.ThreadId
                    )
                    .IsRequired();

                    entity.Property(
                        x => x.UserId
                    )
                    .IsRequired();

                    entity.Property(
                        x => x.Status
                    )
                    .IsRequired();

                    entity.HasIndex(
                        x => x.UserId
                    );
                }
            );

            // ---------------------------------------------
            // RESERVATION
            // ---------------------------------------------

            modelBuilder.Entity<Reservation>(
                entity =>
                {
                    entity.HasKey(
                        x => x.Id
                    );

                    entity.Property(
                        x => x.UserId
                    )
                    .IsRequired();

                    entity.Property(
                        x => x.IdempotencyKey
                    )
                    .IsRequired();

                    entity.HasIndex(
                        x => x.IdempotencyKey
                    )
                    .IsUnique();

                    entity.HasOne(
                        x => x.Book
                    )
                    .WithMany()
                    .HasForeignKey(
                        x => x.BookId
                    )
                    .OnDelete(
                        DeleteBehavior.Restrict
                    );
                }
            );

            // ---------------------------------------------
            // USER PREFERENCE
            // ---------------------------------------------

            modelBuilder.Entity<UserPreference>(
                entity =>
                {
                    entity.HasKey(
                        x => x.Id
                    );

                    entity.Property(
                        x => x.UserId
                    )
                    .IsRequired();

                    entity.Property(
                        x => x.Key
                    )
                    .IsRequired();

                    entity.Property(
                        x => x.Value
                    )
                    .IsRequired();

                    entity.HasIndex(
                        x => new
                        {
                            x.UserId,
                            x.Key
                        }
                    )
                    .IsUnique();
                }
            );
        }
    }
}