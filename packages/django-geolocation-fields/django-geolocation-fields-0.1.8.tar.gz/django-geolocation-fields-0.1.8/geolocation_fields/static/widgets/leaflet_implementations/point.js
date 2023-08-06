$(document).ready(()=>{
    var attribution = point_map_attributions;
    var point_field = $(`#id_${point_input_widget}`);
    var point_display = $('#point_display');

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(point_map);
    

    // Get the value of the point to edit or set a new point to coordinate [0,0]
    var marker_value;
    if(point_value){
        marker_value = point_value;        
    }else if(map_center_marker){
        marker_value = map_center_marker;
    }else{
        marker_value = [0,0]
    }
    var marker = L.marker(marker_value, {
        draggable: true,
    }).addTo(point_map);
    point_map.setView(marker_value)
    

    marker.on('dragend', ()=>{
        point_field.val(`[${marker.getLatLng().lat}, ${marker.getLatLng().lng}]`)
        point_display.html(`[${marker.getLatLng().lat}, ${marker.getLatLng().lng}]`)
    });
    
});
