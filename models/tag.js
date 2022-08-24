const mongoose = require("mongoose");
const Book = require("./book");

const tagSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
  },
  accessLevel: {
    type: Number,
    required: true,
  },
});

tagSchema.pre("remove", function (next) {
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

module.exports = mongoose.model("Tag", tagSchema);
