var boxArray = document.getElementsByClassName("grid-item draggable");
var boxes = Array.prototype.slice.call(boxArray);
dragula({ containers: boxes });
