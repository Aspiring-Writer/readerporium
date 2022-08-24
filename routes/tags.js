const express = require("express");
const router = express.Router();
const { isLoggedIn, isAdmin } = require("../auth");
const Tag = require("../models/tag");
const Book = require("../models/book");
const User = require("../models/user");

// All Tags Route
router.get("/", isLoggedIn, async (req, res) => {
  let query = Tag.find({ accessLevel: { $lte: req.user.accessLevel } });
  if (req.query.name != null && req.query.name !== "") {
    query = query.regex("name", new RegExp(req.query.name, "i"));
  }
  try {
    const user = await User.find({});
    const tags = await query.exec();
    res.render("tags/index", {
      user: user,
      tags: tags,
      searchOptions: req.query,
    });
  } catch {
    res.redirect("/");
  }
});

// New Tag Route
router.get("/new", isLoggedIn, isAdmin, (req, res) => {
  res.render("tags/new", { tag: new Tag() });
});

// Create Tag Route
router.post("/", async (req, res) => {
  const tag = new Tag({
    name: req.body.name,
    accessLevel: req.body.accessLevel,
  });
  try {
    const newTag = await tag.save();
    res.redirect(`tags/${newTag.id}`);
  } catch {
    res.render("tags/new", {
      tag: tag,
      errorMessage: "Error creating tag",
    });
  }
});

// Show Tag Route
router.get("/:id", isLoggedIn, hasAccessLevel, async (req, res) => {
  try {
    const user = await User.find({});
    const tag = await Tag.findById(req.params.id);
    const books = await Book.find({
      tags: tag.id,
      accessLevel: { $lte: req.user.accessLevel },
    });
    res.render("tags/show", {
      user: user,
      tag: tag,
      booksWithTag: books,
    });
  } catch {
    res.redirect("/");
  }
});

// Edit Tag Route
router.get("/:id/edit", isLoggedIn, isAdmin, async (req, res) => {
  try {
    const tag = await Tag.findById(req.params.id);
    res.render("tags/edit", { tag: tag });
  } catch {
    res.redirect("/tags");
  }
});

// Update Tag Route
router.put("/:id", async (req, res) => {
  let tag;
  try {
    tag = await Tag.findById(req.params.id);
    tag.name = req.body.name;
    tag.accessLevel = req.body.accessLevel;
    await tag.save();
    res.redirect(`/tags/${tag.id}`);
  } catch {
    if (tag == null) {
      res.redirect("/");
    } else {
      res.render("tags/edit", {
        tag: tag,
        errorMessage: "Error updating tag",
      });
    }
  }
});

// Delete Tag Route
router.delete("/:id", isLoggedIn, isAdmin, async (req, res) => {
  let tag;
  try {
    tag = await Tag.findById(req.params.id);
    await tag.remove();
    res.redirect("/tags");
  } catch {
    if (tag == null) {
      res.redirect("/");
    } else {
      res.redirect(`/tags/${tag.id}`);
    }
  }
});

async function hasAccessLevel(req, res, next) {
  const tag = await Tag.findById(req.params.id);
  if (tag.accessLevel <= req.user.accessLevel) return next();
  res.redirect("/tags");
}

module.exports = router;
