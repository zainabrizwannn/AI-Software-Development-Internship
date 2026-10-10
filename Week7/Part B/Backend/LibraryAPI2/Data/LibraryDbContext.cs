using LibraryAPI.Models;
using Microsoft.EntityFrameworkCore;

namespace LibraryAPI.Data
{
    public class LibraryDbContext : DbContext
    {
        public LibraryDbContext(DbContextOptions<LibraryDbContext> options)
            : base(options)
        {
        }

        public DbSet<Book> Books { get; set; }

        public DbSet<Author> Authors { get; set; }

        public DbSet<Category> Categories { get; set; }

        public DbSet<User> Users { get; set; }

        public DbSet<Reservation> Reservations { get; set; }

        public DbSet<AgentThread> AgentThreads { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            modelBuilder.Entity<Reservation>(entity =>
            {
                entity.HasKey(r => r.Id);

                entity.Property(r => r.UserId)
                    .IsRequired();

                entity.Property(r => r.IdempotencyKey)
                    .IsRequired();

                entity.HasIndex(r => r.IdempotencyKey)
                    .IsUnique();

                entity.HasOne(r => r.Book)
                    .WithMany()
                    .HasForeignKey(r => r.BookId)
                    .OnDelete(DeleteBehavior.Restrict);
            });

            modelBuilder.Entity<AgentThread>(entity =>
            {
                entity.HasKey(t => t.ThreadId);

                entity.Property(t => t.ThreadId)
                    .IsRequired();

                entity.Property(t => t.UserId)
                    .IsRequired();
            });
        }
    }
}