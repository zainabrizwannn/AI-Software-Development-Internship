USE LibraryDb_Week3;
GO

-- Insert Authors
INSERT INTO Authors (FullName)
VALUES
('Robert C. Martin'),
('James Clear'),
('Andrew Hunt');

-- Insert Books
INSERT INTO Books (Title, AuthorId)
VALUES
('Clean Code', 1),
('Clean Architecture', 1),
('Atomic Habits', 2),
('The Pragmatic Programmer', 3),
('Pragmatic Thinking and Learning', 3),
('The Clean Coder', 1);

-- Insert Categories
INSERT INTO Categories (CategoryName)
VALUES
('Programming'),
('Software Engineering'),
('Self Help'),
('Productivity');

-- Insert BookCategories (Many-to-Many)
INSERT INTO BookCategories (BookId, CategoryId)
VALUES
(1,1),
(1,2),
(2,1),
(2,2),
(3,3),
(3,4),
(4,1),
(4,2),
(5,2),
(6,1);