var boxArray = document.getElementsByClassName("grid-item");
var boxes = Array.prototype.slice.call(boxArray);
dragula({ containers: boxes });
