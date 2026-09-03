USE LibraryDb_Week3;
GO

-- Authors Table
CREATE TABLE Authors
(
    AuthorId INT PRIMARY KEY IDENTITY(1,1),
    FullName NVARCHAR(100) NOT NULL
);

-- Books Table
CREATE TABLE Books
(
    BookId INT PRIMARY KEY IDENTITY(1,1),
    Title NVARCHAR(150) NOT NULL,
    AuthorId INT NOT NULL,

    FOREIGN KEY (AuthorId)
    REFERENCES Authors(AuthorId)
);

-- Categories Table
CREATE TABLE Categories
(
    CategoryId INT PRIMARY KEY IDENTITY(1,1),
    CategoryName NVARCHAR(100) NOT NULL
);

-- BookCategories Table
CREATE TABLE BookCategories
(
    BookId INT,
    CategoryId INT,

    PRIMARY KEY (BookId, CategoryId),

    FOREIGN KEY (BookId)
    REFERENCES Books(BookId),

    FOREIGN KEY (CategoryId)
    REFERENCES Categories(CategoryId)
);