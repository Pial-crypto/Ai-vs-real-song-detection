"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.onDrop = void 0;

var _axios = _interopRequireDefault(require("axios"));

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }

/**
 * Handles audio file upload and prediction via FastAPI backend
 */
var onDrop = function onDrop(acceptedFiles, setError, setUploading, setUploadedFile, setActiveStep, setPredictions) {
  var file, formData, response, data;
  return regeneratorRuntime.async(function onDrop$(_context) {
    while (1) {
      switch (_context.prev = _context.next) {
        case 0:
          console.log(acceptedFiles, "ACCEPTED files");
          file = acceptedFiles[0]; // Only process the first file

          if (file) {
            _context.next = 4;
            break;
          }

          return _context.abrupt("return");

        case 4:
          if (["audio/mpeg", "audio/wav"].includes(file.type)) {
            _context.next = 7;
            break;
          }

          setError("Please upload only MP3 or WAV files");
          return _context.abrupt("return");

        case 7:
          setError(null);
          setUploading(true);
          setUploadedFile(file);
          _context.prev = 10;
          // Move UI to "uploading" step
          setActiveStep(1); // === Prepare form data ===

          formData = new FormData();
          formData.append("file", file); // === Send to backend ===

          _context.next = 16;
          return regeneratorRuntime.awrap(_axios["default"].post("http://127.0.0.1:8000/prediction", formData, {
            headers: {
              "Content-Type": "multipart/form-data"
            }
          }));

        case 16:
          response = _context.sent;
          // === Extract predictions ===
          data = response.data; // Optionally log for debugging

          console.log("Prediction response:", data); // Update UI states

          setPredictions(data);
          setActiveStep(2); // Move to "results" step

          _context.next = 27;
          break;

        case 23:
          _context.prev = 23;
          _context.t0 = _context["catch"](10);
          console.error(_context.t0);
          setError("An error occurred during prediction");

        case 27:
          _context.prev = 27;
          setUploading(false);
          return _context.finish(27);

        case 30:
        case "end":
          return _context.stop();
      }
    }
  }, null, null, [[10, 23, 27, 30]]);
};

exports.onDrop = onDrop;