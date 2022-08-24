const express = require("express");
const router = express.Router();
const { isLoggedIn, isAdmin } = require("../auth");
const Series = require("../models/series");
const Book = require("../models/book");
const User = require("../models/user");

// All Series Route
router.get("/", isLoggedIn, async (req, res) => {
  let query = Series.find({ accessLevel: { $lte: req.user.accessLevel } });
  if (req.query.name != null && req.query.name !== "") {
    query = query.regex("name", new RegExp(req.query.name, "i"));
  }
  try {
    const user = await User.find({});
    const series = await query.exec();
    res.render("series/index", {
      user: user,
      series: series,
      searchOptions: req.query,
    });
  } catch {
    res.redirect("/");
  }
});

// New Series Route
router.get("/new", isLoggedIn, isAdmin, (req, res) => {
  res.render("series/new", { series: new Series() });
});

// Create Series Route
router.post("/", async (req, res) => {
  const series = new Series({
    name: req.body.name,
    accessLevel: req.body.accessLevel,
  });
  try {
    const newSeries = await series.save();
    res.redirect(`series/${newSeries.id}`);
  } catch {
    res.render("series/new", {
      series: series,
      errorMessage: "Error creating series",
    });
  }
});

// Show Series Route
router.get("/:id", isLoggedIn, hasAccessLevel, async (req, res) => {
  try {
    const user = await User.find({});
    const series = await Series.findById(req.params.id);
    const books = await Book.find({
      series: series.id,
      accessLevel: { $lte: req.user.accessLevel },
    });
    res.render("series/show", {
      user: user,
      series: series,
      booksInSeries: books,
    });
  } catch {
    res.redirect("/");
  }
});

// Edit Series Route
router.get("/:id/edit", isLoggedIn, isAdmin, async (req, res) => {
  try {
    const series = await Series.findById(req.params.id);
    res.render("series/edit", { series: series });
  } catch {
    res.redirect("/series");
  }
});

// Update Series Route
router.put("/:id", async (req, res) => {
  let series;
  try {
    series = await Series.findById(req.params.id);
    series.name = req.body.name;
    series.accessLevel = req.body.accessLevel;
    await series.save();
    res.redirect(`/series/${series.id}`);
  } catch {
    if (series == null) {
      res.redirect("/");
    } else {
      res.render("series/edit", {
        series: series,
        errorMessage: "Error updating series",
      });
    }
  }
});

// Delete Series Route
router.delete("/:id", isLoggedIn, isAdmin, async (req, res) => {
  let series;
  try {
    series = await Series.findById(req.params.id);
    await series.remove();
    res.redirect("/series");
  } catch {
    if (series == null) {
      res.redirect("/");
    } else {
      res.redirect(`/series/${series.id}`);
    }
  }
});

async function hasAccessLevel(req, res, next) {
  const series = await Series.findById(req.params.id);
  if (series.accessLevel <= req.user.accessLevel) return next();
  res.redirect("/series");
}

module.exports = router;
