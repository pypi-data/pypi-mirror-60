$(document).ready(()=>{
    var attribution = map_attributions;
    var point_field = $(`#id_${input_widget}`);

    let onDragEnd = (event) => {
        console.log("Marker dragged");
        console.log(event);
    }

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    let marker = L.marker([6.1720, 1.2263], {
        draggable: true,
    }).addTo(map);

    marker.on('dragend', (event)=>{
        console.log(marker.getLatLng());
        point_field.val(`[${marker.getLatLng().lat}, ${marker.getLatLng().lng}]`)
    });
});
