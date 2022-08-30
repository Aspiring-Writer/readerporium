FilePond.registerPlugin(
  FilePondPluginImagePreview,
  FilePondPluginImageResize,
  FilePondPluginFileEncode
);

FilePond.setOptions({
  imageResizeTargetWidth: 457,
  imageResizeTargetHeight: 300,
});

FilePond.parse(document.body);
