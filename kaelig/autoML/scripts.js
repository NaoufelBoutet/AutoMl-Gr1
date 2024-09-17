const drag_object= getElementbyId("object_draggable")
const zone_drag=getElementbyId('zone_drag')

drag_object.addEventListener('startdrag', (e) => {
    console.log("dragging");
})