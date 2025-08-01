function makeModalResizable() {
    const dialog = $(".modal-dialog");
    if (dialog.length > 0) {
        // console.log("Applying draggable and resizable to modal-dialog");
        dialog.draggable({
            handle: ".modal-header"
        }).resizable();
    } else {
        // console.log("modal-dialog not found, retrying...");
        setTimeout(makeModalResizable, 500);
    }
}

$(document).ready(function () {
    makeModalResizable();
});
