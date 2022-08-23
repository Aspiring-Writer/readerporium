FilePond.registerPlugin(
  FilePondPluginImagePreview,
  FilePondPluginImageResize,
  FilePondPluginFileEncode
);

FilePond.setOptions({
  imageResizeTargetWidth: 150,
  imageResizeTargetHeight: 200,
});

FilePond.parse(document.body);
