using LibraryAPI.Models;

namespace LibraryAPI.Repositories
{
    public interface IBookRepository
    {
        List<Book> GetAll();

        Book? GetById(int id);

        void Add(Book book);

        void Update(Book book);

        void Delete(int id);
    }
}