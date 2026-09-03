-- A JOIN query that lists every book together with its author's name in one result set
USE LibraryDb_Week3;
GO

SELECT
    b.Title,
    a.FullName AS Author
FROM Books b JOIN Authors a ON b.AuthorId = a.AuthorId ORDER BY a.FullName;


-- A JOIN query that returns all categories for one specific book 
SELECT
    b.Title,
    c.CategoryName
FROM Books b JOIN BookCategories bc ON b.BookId = bc.BookId JOIN Categories c 
ON bc.CategoryId = c.CategoryId WHERE b.BookId = 1;