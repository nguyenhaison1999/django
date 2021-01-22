const cv = require('opencv.js');
const exif = require('exif-parser');
const fs = require('fs');

const buffer = fs.readFileSync('images/demo.jpg');

// console.log(fileBuffer.buffer);
const image = cv.imread('images/demo.jpg');

console.log(image.data.buffer == buffer);

// function toBuffer(ab) {
// 	var buf = Buffer.alloc(ab.byteLength);
// 	var view = new Uint8Array(ab);
// 	for (var i = 0; i < buf.length; ++i) {
// 		buf[i] = view[i];
// 	}
// 	return buf;
// }

// const buffer = toBuffer(image.data);

// const parser = exif.create(buffer);

// const result = parser.parse();

// console.log(JSON.stringify(result.tags, null, 2));

// const exiftool = require('exiftool-vendored').exiftool;

// exiftool
// 	.read('images/exif1.jpg')
// 	.then((tags /*: Tags */) => console.log(JSON.stringify(tags, null, 2)))
// 	.catch((err) => console.error('Something terrible happened: ', err));
