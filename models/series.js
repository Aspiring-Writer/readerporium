const mongoose = require("mongoose");
const Book = require("./book");

const seriesSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
  },
  accessLevel: {
    type: Number,
    required: true,
  },
});

seriesSchema.pre("remove", function (next) {
  Book.find({ series: this.id }, (err, books) => {
    if (err) {
      next(err);
    } else if (books.length > 0) {
      next(new Error("This series still has books"));
    } else {
      next();
    }
  });
});

module.exports = mongoose.model("Series", seriesSchema);
