$(document).ready(()=>{
    var attribution = polygon_map_attributions;
    var polygon_field = $(`#id_${polygon_input_widget}`)

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(polygon_map);


    // Polygone test
    var polygon = L.polygon([
        [6.17357,1.21276],
        [6.17375, 1.21395],
        [6.17292, 1.21390]
    ]).addTo(polygon_map);

    

    polygon.on('click', ()=>{
        polygonToArray = []
        polygonLatLng = polygon.getLatLngs()[0];
        
        polygonLatLng.forEach(corner => {
            console.log(corner)
            polygonToArray.push(`[ ${corner.lat}, ${corner.lng}]`)
        });

        polygon_field.val(`[${polygonToArray}]`)
    })
    
    
    // Icontrol for Polygon creation

    class MapManageControl extends L.Control{
        htmlElement = document.createElement('div');
        
        onAdd = (map) =>{
            this.htmlElement.className = 'map_manage_control leaflet-control-container';
            this.htmlElement.appendChild(document.querySelector("#map_manage_control"));
            return this.htmlElement
        }
    }


    let map_manage_control = new MapManageControl();
    map_manage_control.addTo(polygon_map);    
});
