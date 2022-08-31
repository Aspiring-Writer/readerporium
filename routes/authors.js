const express = require("express");
const router = express.Router();
const { isLoggedIn, isAdmin } = require("../auth");
const Author = require("../models/author");
const Book = require("../models/book");
const User = require("../models/user");

// All Authors Route
router.get("/", isLoggedIn, async (req, res) => {
  let query = Author.find({ accessLevel: { $lte: req.user.accessLevel } }).sort(
    "name"
  );
  if (req.query.name != null && req.query.name !== "") {
    query = query.regex("name", new RegExp(req.query.name, "i"));
  }
  try {
    const authors = await query.exec();
    res.render("authors/index", {
      authors: authors,
      searchOptions: req.query,
    });
  } catch {
    res.redirect("/");
  }
});

// New Author Route
router.get("/new", isLoggedIn, isAdmin, (req, res) => {
  res.render("authors/new", { author: new Author() });
});

// Create Author Route
router.post("/", async (req, res) => {
  const author = new Author({
    name: req.body.name,
    accessLevel: req.body.accessLevel,
  });
  try {
    await author.save();
    req.flash("info", "Author created successfully");
  } catch {
    req.flash("error", "Error creating Author");
  }
  res.render(`authors/new`, {
    author: author,
  });
});

// Show Author Route
router.get("/:id", isLoggedIn, hasAccessLevel, async (req, res) => {
  try {
    const user = await User.findById(req.user.id);
    const author = await Author.findById(req.params.id);
    const books = await Book.find({
      author: author.id,
      accessLevel: { $lte: req.user.accessLevel },
    }).sort("title");
    res.render("authors/show", {
      user: user,
      author: author,
      books: books,
    });
  } catch {
    res.redirect("/");
  }
});

// Edit Author Route
router.get("/:id/edit", isLoggedIn, isAdmin, async (req, res) => {
  try {
    const author = await Author.findById(req.params.id);
    res.render("authors/edit", { author: author });
  } catch {
    res.redirect("/authors");
  }
});

// Update Author Route
router.put("/:id", async (req, res) => {
  let author;
  try {
    author = await Author.findById(req.params.id);
    author.name = req.body.name;
    author.accessLevel = req.body.accessLevel;
    await author.save();
    res.redirect(`/authors/${author.id}`);
  } catch {
    if (author == null) {
      res.redirect("/");
    } else {
      req.flash("error", "Error updating author");
      res.render("authors/edit", {
        author: author,
      });
    }
  }
});

// Delete Author Route
router.delete("/:id", isLoggedIn, isAdmin, async (req, res) => {
  let author;
  try {
    author = await Author.findById(req.params.id);
    await author.remove();
    res.redirect("/authors");
  } catch {
    if (author == null) {
      res.redirect("/");
    } else {
      res.redirect(`/authors/${author.id}`);
    }
  }
});

async function hasAccessLevel(req, res, next) {
  const author = await Author.findById(req.params.id);
  if (author.accessLevel <= req.user.accessLevel) return next();
  res.redirect("/authors");
}

module.exports = router;
