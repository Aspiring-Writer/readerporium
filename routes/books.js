const express = require("express");
const router = express.Router();
const { isLoggedIn, isAdmin } = require("../auth");
const Book = require("../models/book");
const Author = require("../models/author");
const Series = require("../models/series");
const Tag = require("../models/tag");
const imageMimeTypes = ["image/jpeg", "image/png", "image/gif"];
const User = require("../models/user");

const MarkdownIt = require('markdown-it'),
    md = new MarkdownIt();

// All Books Route
router.get("/", isLoggedIn, async (req, res) => {
  let query = Book.find({ accessLevel: { $lte: req.user.accessLevel } }).sort("title");
  if (req.query.title != null && req.query.title != "") {
    query = query.regex("title", new RegExp(req.query.title, "i"));
  }
  if (req.query.maxWordCount != null && req.query.maxWordCount != "") {
    query = query.lte("wordCount", req.query.maxWordCount);
  }
  if (req.query.minWordCount != null && req.query.minWordCount != "") {
    query = query.gte("wordCount", req.query.minWordCount);
  }
  if (req.query.publishedBefore != null && req.query.publishedBefore != "") {
    query = query.lte("publishDate", req.query.publishedBefore);
  }
  if (req.query.publishedAfter != null && req.query.publishedAfter != "") {
    query = query.gte("publishDate", req.query.publishedAfter);
  }
  try {
    const books = await query.exec();
    res.render("books/index", {
      books: books,
      searchOptions: req.query,
    });
  } catch {
    res.redirect("/");
  }
});

// New Book Route
router.get("/new", isLoggedIn, isAdmin, async (req, res) => {
  renderNewPage(res, new Book());
});

// Create Book Route
router.post("/", async (req, res) => {
  const book = new Book({
    title: req.body.title,
    author: req.body.author,
    publishDate: new Date(req.body.publishDate),
    wordCount: req.body.wordCount,
    description: req.body.description,
    accessLevel: req.body.accessLevel,
    series: req.body.series,
    seriesIndex: req.body.seriesIndex,
    tags: req.body.tags,
  });
  saveCover(book, req.body.cover);

  try {
    const newBook = await book.save();
    res.redirect(`books/${newBook.id}`);
  } catch {
    renderNewPage(res, book, true);
  }
});

// Show Book Route
router.get("/:id", isLoggedIn, hasAccessLevel, async (req, res) => {
  try {
    const user = await User.findById(req.user.id);
    const book = await Book.findById(req.params.id)
      .populate("author")
      .populate("series")
      .populate("tags")
      .exec();
    const description = md.render(book.description);
    res.render("books/show", {
      user: user,
      book: book,
      description: description,
    });
  } catch {
    res.redirect("/");
  }
});

// Edit Book Route
router.get("/:id/edit", isLoggedIn, isAdmin, async (req, res) => {
  try {
    const book = await Book.findById(req.params.id);
    renderEditPage(res, book);
  } catch {
    res.redirect("/");
  }
});

// Update Book Route
router.put("/:id", async (req, res) => {
  let book;
  try {
    book = await Book.findById(req.params.id);
    book.title = req.body.title;
    book.author = req.body.author;
    book.publishDate = new Date(req.body.publishDate);
    book.wordCount = req.body.wordCount;
    book.description = req.body.description;
    book.accessLevel = req.body.accessLevel;
    book.series = req.body.series;
    book.seriesIndex = req.body.seriesIndex;
    book.tags = req.body.tags;
    if (req.body.cover != null && req.body.cover != "") {
      saveCover(book, req.body.cover);
    }
    await book.save();
    res.redirect(`/books/${book.id}`);
  } catch {
    if (book != null) {
      renderEditPage(res, book, true);
    } else {
      res.redirect("/");
    }
  }
});

// Delete Book Route
router.delete("/:id", isLoggedIn, isAdmin, async (req, res) => {
  let book;
  try {
    book = await Book.findById(req.params.id);
    await book.remove();
    res.redirect("/books");
  } catch {
    if (book != null) {
      res.render("books/show", {
        book: book,
        errorMessage: "Could not remove book",
      });
    } else {
      res.redirect("/");
    }
  }
});

async function renderNewPage(res, book, hasError = false) {
  renderFormPage(res, book, "new", hasError);
}

async function renderEditPage(res, book, hasError = false) {
  renderFormPage(res, book, "edit", hasError);
}

async function renderFormPage(res, book, form, hasError = false) {
  try {
    const authors = await Author.find({}).sort("name");
    const series = await Series.find({}).sort("name");
    const tags = await Tag.find({}).sort("name");
    const params = {
      authors: authors,
      series: series,
      tags: tags,
      book: book,
    };
    if (hasError) {
      if (form === "edit") {
        params.errorMessage = "Error updating book";
      } else {
        params.errorMessage = "Error creating book";
      }
    }
    res.render(`books/${form}`, params);
  } catch {
    res.redirect("/books");
  }
}

function saveCover(book, coverEncoded) {
  if (coverEncoded == null) return;
  const cover = JSON.parse(coverEncoded);
  if (cover != null && imageMimeTypes.includes(cover.type)) {
    book.coverImage = new Buffer.from(cover.data, "base64");
    book.coverImageType = cover.type;
  }
}

async function hasAccessLevel(req, res, next) {
  const book = await Book.findById(req.params.id);
  if (book.accessLevel <= req.user.accessLevel) return next();
  res.redirect("/books");
}

module.exports = router;
