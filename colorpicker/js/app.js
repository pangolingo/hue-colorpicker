var doms = {
  canvas: document.getElementById('canvas'),
  image: document.getElementById('cie-diagram-image'),
  colorBlock: document.getElementById('colorblock'),
  fields: {
    rgb_r: document.getElementById('rgb_r'),
    rgb_g: document.getElementById('rgb_g'),
    rgb_b: document.getElementById('rgb_b'),

    xyy_x: document.getElementById('xyy_x'),
    xyy_y: document.getElementById('xyy_y'),
    xyy_lum: document.getElementById('xyy_lum'),

    hex_picker: document.getElementById('hex_picker'),
    hex_value: document.getElementById('hex_value'),
  }
}


var ctx = doms.canvas.getContext('2d');
var cursorPos = [0,0];
var RGB_cursorPos = [0,0];
var isDragging = false;

// red, green, blue
// gamut for Hue light strips
// https://developers.meethue.com/documentation/color-conversions-rgb-xy
let hue_gamut_XY = [
    [0.704, 0.296],
    [0.2151, 0.7106],
    [0.138, 0.08],
];
// from wikipedia SRGB table
let srgb_gamut_XY = [
    [0.6400, 0.3300],
    [0.3000, 0.6000],
    [0.1500, 0.0600],
]


let original_image = {
    dimensions: [1200, 1275],
    xGraphOffset: 145, // from left 
    yGraphOffset: 125, // from bottom
    xAxisLength: 993 * 1.25, // multiply because this graph only shows up to 0.9, 0.8
    yAxisLength: 1115 * 1.111111111,
}
let new_dimensions = [300, 300];
let ratio = [
    new_dimensions[0] / original_image.dimensions[0],
    new_dimensions[1] / original_image.dimensions[1],
]
let new_image = {
    dimensions: new_dimensions,
    xGraphOffset: original_image.xGraphOffset * ratio[0],
    yGraphOffset: original_image.yGraphOffset * ratio[1],
    xAxisLength: original_image.xAxisLength * ratio[0],
    yAxisLength: original_image.xAxisLength * ratio[1],
}

function round_rgb_values(rgb){
  return [Math.round(rgb[0]), Math.round(rgb[1]), Math.round(rgb[2])];
}


function draw() {
    // clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // draw color chart
    ctx.drawImage(doms.image, 0, 0, canvas.width, canvas.height);
    // gamut triangles
    draw_gamuts(ctx);
    // cursors
    drawing_helpers.draw_cursor(cursorPos, ctx);
    drawing_helpers.draw_cursor(RGB_cursorPos, ctx);

    window.requestAnimationFrame(draw);
}
window.requestAnimationFrame(draw);


doms.fields.rgb_r.addEventListener('change', on_RGB_input_update);
doms.fields.rgb_g.addEventListener('change', on_RGB_input_update);
doms.fields.rgb_b.addEventListener('change', on_RGB_input_update);

doms.fields.xyy_x.addEventListener('change', on_XY_input_update);
doms.fields.xyy_y.addEventListener('change', on_XY_input_update);

doms.fields.hex_picker.addEventListener("input", on_hex_picker_update, false);

doms.canvas.addEventListener('mousedown', function(e) {
  isDragging = true;
  update_mouse_pos([e.clientX, e.clientY]);
});
doms.canvas.addEventListener('mouseup', function(e) {
  isDragging = false;
});
doms.canvas.addEventListener('mousemove', function(e) {
  if(isDragging){
      update_mouse_pos([e.clientX, e.clientY]);
  }
});

function on_RGB_input_update(e){
    let rgb = [
        parseInt(doms.fields.rgb_r.value),
        parseInt(doms.fields.rgb_g.value),
        parseInt(doms.fields.rgb_b.value),
    ];
    let roundedRGB = round_rgb_values(rgb);
    let hex = color_helpers.RGB_to_hex(roundedRGB[0], roundedRGB[1], roundedRGB[2]);
    let xyY = color_helpers.RGB_to_XYY(rgb);
    cursorPos = position_helpers.CIE_XY_to_canvas_position(xyY);
    RGB_cursorPos = position_helpers.CIE_XY_to_canvas_position(xyY);
    update_form_fields(hex, xyY, rgb);
}

function on_XY_input_update(e){
    let xyy = [
        parseFloat(doms.fields.xyy_x.value),
        parseFloat(doms.fields.xyy_y.value),
        parseFloat(doms.fields.xyy_lum.value),
    ];
    let rgb = round_rgb_values(color_helpers.xyY_TO_RGB(xyy));
    let hex = color_helpers.RGB_to_hex(rgb[0], rgb[1], rgb[2]);
    cursorPos = position_helpers.CIE_XY_to_canvas_position(xyy);
    let rgbxy = color_helpers.RGB_to_XYY(rgb);
    RGB_cursorPos = position_helpers.CIE_XY_to_canvas_position(rgbxy);
    update_form_fields(hex, xyy, rgb);
}

function on_hex_picker_update(e){
  let hex = e.target.value;
  let rgb = color_helpers.hex_to_RGB(hex);
  let xyy = color_helpers.RGB_to_XYY(rgb);
  cursorPos = position_helpers.CIE_XY_to_canvas_position(xyy);
  RGB_cursorPos = position_helpers.CIE_XY_to_canvas_position(xyy);
  update_form_fields(hex, xyy, rgb);
}


function draw_gamuts(ctx){
  drawing_helpers.draw_shape(srgb_gamut_XY.map(point => position_helpers.CIE_XY_to_canvas_position(point)), '#000000', ctx);
  drawing_helpers.draw_shape(hue_gamut_XY.map(point => position_helpers.CIE_XY_to_canvas_position(point)), '#ffffff', ctx);
}



function update_form_fields(hex, xyy, rgb){
    doms.fields.hex_picker.value = hex;
    doms.fields.hex_value.value = hex;

    doms.fields.xyy_x.value = xyy[0];
    doms.fields.xyy_y.value = xyy[1];
    doms.fields.xyy_lum.value = xyy[2] || 100;

    var roundedRGB = round_rgb_values(rgb)
    doms.fields.rgb_r.value = roundedRGB[0];
    doms.fields.rgb_g.value = roundedRGB[1];
    doms.fields.rgb_b.value = roundedRGB[2];

    doms.colorBlock.style.backgroundColor = hex;
}

function update_mouse_pos(offset){
    // the offset is relative to the window
    // find the offset relative to the canvas
    var rect = canvas.getBoundingClientRect();
    offset[0] = offset[0] - rect.left;
    offset[1] = offset[1] - rect.top;

    // find the position relative to the graph image
    let position = position_helpers.canvas_pos_to_graph_pos(event.offsetX, event.offsetY);
    // find the xy value, then the RGB and hex values from that
    let xy = position_helpers.graph_pos_to_CIE_XY(position);
    let rgb = round_rgb_values(color_helpers.xyY_TO_RGB([xy[0], xy[1], 100]));
    let hex = color_helpers.RGB_to_hex(rgb[0], rgb[1], rgb[2])
    let rgbxy = color_helpers.RGB_to_XYY(rgb);

    // update fields and cursors
    update_form_fields(hex, xy, rgb);
    cursorPos = offset;
    RGB_cursorPos = position_helpers.CIE_XY_to_canvas_position(rgbxy);
}


var position_helpers = {
  canvas_pos_to_graph_pos: function(offsetXFromLeft, offsetYFromTop){
    // canvas width and height = 300
    let offsetYFromBottom = new_image.dimensions[0] - offsetYFromTop;
    let offsetX = offsetXFromLeft - new_image.xGraphOffset;
    let offsetY = offsetYFromBottom - new_image.yGraphOffset;
    return [offsetX, offsetY];
  },
  graph_pos_to_CIE_XY: function(position) {
      let xPercent = position[0] / new_image.xAxisLength;
      let xPos = xPercent;

      let yPercent = position[1] / new_image.yAxisLength;
      let yPos = yPercent;
      return [xPos, yPos]
  },
  CIE_XY_to_canvas_position: function(xy){
    let x = new_image.xAxisLength * xy[0] + new_image.xGraphOffset;
    let y = new_image.dimensions[1] - (new_image.yAxisLength * xy[1] + new_image.yGraphOffset);
    return [x,y]
  },
}


var drawing_helpers = {
  // draw a crosshairs
  draw_cursor: function(point, ctx){
    var padding = 2;
    var lineLength = 5;
    ctx.fillRect(point[0], point[1] - padding - lineLength ,1,lineLength);
    ctx.fillRect(point[0], point[1] + padding ,1,lineLength);

    ctx.fillRect(point[0] - padding - lineLength, point[1],lineLength,1);
    ctx.fillRect(point[0] + padding, point[1],lineLength,1);
  },

  draw_shape: function(points, color, ctx){
    ctx.beginPath();
    ctx.strokeStyle = color;
    points.forEach((point) => {
        ctx.lineTo(point[0], point[1]);
    });
    ctx.closePath();
    ctx.stroke();
  },
}

var color_helpers = {
  RGB_to_XYY: function(rgb){
    return colorSpace.rgb.xyy(rgb);
  },
  
  xyY_TO_RGB: function(xyY){
    return colorSpace.xyy.rgb(xyY);
  },

  // from stackoverflow
  // https://stackoverflow.com/questions/5623838/rgb-to-hex-and-hex-to-rgb
  RGB_to_hex: function(r, g, b) {
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
  },
  hex_to_RGB: function(hex) {
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? [
        parseInt(result[1], 16),
        parseInt(result[2], 16),
        parseInt(result[3], 16)
    ]   : null;
  },
}